"""WP-03 Research Package persistence and service contract tests.

研究包持久化测试，验证核心领域规则：
1. 追加式版本管理：v1 创建后不可变，刷新创建 v2 不修改 v1
2. 幂等性：同一 idempotency_key + request_hash 只创建一个版本
3. 乐观并发：SELECT FOR UPDATE + expected_version 防止重复版本
4. 事务安全：失败时 package 和 module 一起回滚，不留半写数据
5. 数据库约束：唯一约束作为最后防线阻止重复写入
6. 新鲜度推导：基于状态和时间戳的确定性计算

每个测试用例使用独立的临时 PostgreSQL 数据库，测试后自动清理。
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.research import services
from backend.research.models import ResearchModule, ResearchPackage
from backend.research.services import (
    IdempotencyConflict,
    ResearchPackageAlreadyExists,
    ResearchPersistenceConflict,
    ResearchVersionConflict,
    calculate_module_freshness,
    create_incremental_refresh,
    create_initial_package,
    get_current_package,
    get_package_version,
    list_package_history,
)

QIANGRUI_INSTRUMENT_ID = "11111111-1111-4111-8111-111111111111"
DEFAULT_ADMIN_DATABASE_URL = (
    "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
)


@pytest_asyncio.fixture
async def pg_sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Create a disposable PostgreSQL database and run Alembic migrations.

    每个测试函数获得独立的临时数据库，通过 Alembic 迁移建表，
    测试结束后终止连接并删除数据库，保证用例间完全隔离。
    若 PostgreSQL 不可用则跳过整个测试模块。
    """
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", DEFAULT_ADMIN_DATABASE_URL))
    test_db_name = f"tg_wp03_test_{uuid4().hex}"
    admin_db = admin_url.database or "postgres"

    try:
        admin_conn = await asyncpg.connect(
            user=admin_url.username,
            password=admin_url.password,
            host=admin_url.host or "127.0.0.1",
            port=admin_url.port or 5432,
            database=admin_db,
        )
    except OSError as exc:
        pytest.skip(f"PostgreSQL is not available for WP-03 persistence tests: {exc}")
    except asyncpg.PostgresError as exc:
        pytest.skip(f"PostgreSQL connection failed for WP-03 persistence tests: {exc}")

    await admin_conn.execute(f'CREATE DATABASE "{test_db_name}"')
    await admin_conn.close()

    test_url = admin_url.set(database=test_db_name)
    test_database_url = test_url.render_as_string(hide_password=False)
    env = {**os.environ, "DATABASE_URL": test_database_url}
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    engine = create_async_engine(test_database_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    try:
        yield sessionmaker
    finally:
        await engine.dispose()
        cleanup_conn = await asyncpg.connect(
            user=admin_url.username,
            password=admin_url.password,
            host=admin_url.host or "127.0.0.1",
            port=admin_url.port or 5432,
            database=admin_db,
        )
        await cleanup_conn.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1 AND pid <> pg_backend_pid()
            """,
            test_db_name,
        )
        await cleanup_conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        await cleanup_conn.close()


@pytest_asyncio.fixture
async def db(pg_sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """Provide an isolated session transaction for each test."""
    async with pg_sessionmaker() as session:
        yield session
        await session.rollback()


async def test_initial_package_persists_version_modules_and_unverified_freshness(
    db: AsyncSession,
) -> None:
    """First build creates version 1 with all default modules and no fake facts."""
    package = await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="initial-001",
        request_hash="initial:qiangrui",
    )
    await db.commit()

    assert package.version == 1
    assert package.previous_version_id is None
    assert package.trigger_type == "INITIAL_FULL"
    assert package.status == "PENDING"
    assert package.completed_at is None
    assert package.last_verified_at is None
    assert len(package.modules) == len(services.DEFAULT_RESEARCH_MODULE_TYPES)
    assert {module.module_type for module in package.modules} == set(
        services.DEFAULT_RESEARCH_MODULE_TYPES
    )
    assert all(module.status == "UNVERIFIED" for module in package.modules)
    assert all(module.summary is None for module in package.modules)
    assert all(module.source_refs == [] for module in package.modules)
    assert all(calculate_module_freshness(module) == "UNVERIFIED" for module in package.modules)

    current = await get_current_package(db, QIANGRUI_INSTRUMENT_ID)
    history = await list_package_history(db, QIANGRUI_INSTRUMENT_ID)

    assert current is not None
    assert current.id == package.id
    assert [item.version for item in history] == [1]


async def test_repeated_initial_is_idempotent_for_same_request_and_conflicts_for_new_request(
    db: AsyncSession,
) -> None:
    """Initial build cannot create a second version 1."""
    first = await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="initial-idempotent",
        request_hash="same-request",
    )
    await db.commit()

    repeated = await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="initial-idempotent",
        request_hash="same-request",
    )

    assert repeated.id == first.id

    with pytest.raises(ResearchPackageAlreadyExists):
        await create_initial_package(
            db,
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            idempotency_key="another-initial",
            request_hash="different-request",
        )


async def test_refresh_creates_lineage_and_copy_on_write_without_mutating_history(
    db: AsyncSession,
) -> None:
    """Refresh creates version N+1 while version N remains reproducible."""
    initial = await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="refresh-base",
        request_hash="initial",
    )
    await db.commit()
    original_company = next(module for module in initial.modules if module.module_type == "COMPANY")
    original_financial = next(
        module for module in initial.modules if module.module_type == "FINANCIAL"
    )

    refreshed = await create_incremental_refresh(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        expected_version=1,
        idempotency_key="refresh-001",
        request_hash="refresh:financial",
        refresh_module_types=("FINANCIAL",),
    )
    await db.commit()

    assert refreshed.version == 2
    assert refreshed.previous_version_id == initial.id
    assert refreshed.trigger_type == "INCREMENTAL_REFRESH"
    assert refreshed.expected_version == 1
    assert len(refreshed.modules) == len(initial.modules)

    copied_company = next(module for module in refreshed.modules if module.module_type == "COMPANY")
    new_financial = next(module for module in refreshed.modules if module.module_type == "FINANCIAL")

    assert copied_company.origin_module_id == original_company.id
    assert copied_company.summary == original_company.summary
    assert new_financial.origin_module_id is None
    assert new_financial.id != original_financial.id
    assert new_financial.status == "UNVERIFIED"
    assert new_financial.summary is None

    version_one = await get_package_version(db, QIANGRUI_INSTRUMENT_ID, 1)
    history = await list_package_history(db, QIANGRUI_INSTRUMENT_ID)

    assert version_one is not None
    assert version_one.id == initial.id
    assert [item.version for item in history] == [1, 2]


async def test_refresh_rejects_stale_expected_version_and_idempotency_mismatch(
    db: AsyncSession,
) -> None:
    """Expected-version and idempotency conflicts are stable domain errors."""
    await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="conflict-base",
        request_hash="initial",
    )
    await db.commit()
    first_refresh = await create_incremental_refresh(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        expected_version=1,
        idempotency_key="conflict-refresh",
        request_hash="refresh:v1",
    )
    await db.commit()

    repeated = await create_incremental_refresh(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        expected_version=1,
        idempotency_key="conflict-refresh",
        request_hash="refresh:v1",
    )
    assert repeated.id == first_refresh.id

    with pytest.raises(IdempotencyConflict):
        await create_incremental_refresh(
            db,
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            expected_version=1,
            idempotency_key="conflict-refresh",
            request_hash="refresh:different",
        )

    with pytest.raises(ResearchVersionConflict) as exc_info:
        await create_incremental_refresh(
            db,
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            expected_version=1,
            idempotency_key="stale-refresh",
            request_hash="refresh:stale",
        )

    assert exc_info.value.current_version == 2
    assert exc_info.value.expected_version == 1


async def test_concurrent_refresh_allows_only_one_next_version(
    pg_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """Database constraints and expected-version checks reject concurrent duplicate versions."""
    async with pg_sessionmaker() as setup:
        await create_initial_package(
            setup,
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            idempotency_key="concurrent-base",
            request_hash="initial",
        )
        await setup.commit()

    async def refresh(key: str) -> str:
        async with pg_sessionmaker() as session:
            try:
                await create_incremental_refresh(
                    session,
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    expected_version=1,
                    idempotency_key=key,
                    request_hash=key,
                )
                await session.commit()
                return "created"
            except ResearchVersionConflict:
                await session.rollback()
                return "conflict"

    results = await asyncio.gather(refresh("concurrent-a"), refresh("concurrent-b"))

    assert sorted(results) == ["conflict", "created"]

    async with pg_sessionmaker() as verify:
        history = await list_package_history(verify, QIANGRUI_INSTRUMENT_ID)
        assert [item.version for item in history] == [1, 2]


async def test_database_constraints_prevent_duplicate_versions_and_module_types(
    db: AsyncSession,
) -> None:
    """PostgreSQL constraints backstop package and module uniqueness."""
    package = await create_initial_package(
        db,
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        idempotency_key="constraint-base",
        request_hash="initial",
    )
    package_id = package.id
    await db.commit()

    duplicate_package = ResearchPackage(
        instrument_id=QIANGRUI_INSTRUMENT_ID,
        version=1,
        trigger_type="INITIAL_FULL",
        status="PENDING",
        idempotency_key="constraint-duplicate-version",
        request_hash="duplicate",
        as_of=datetime.now(UTC),
        started_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    db.add(duplicate_package)
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    duplicate_module = ResearchModule(
        research_package_id=package_id,
        module_type="COMPANY",
        module_version=1,
        status="UNVERIFIED",
        source_refs=[],
        as_of=datetime.now(UTC),
        stale_after=datetime.now(UTC) + timedelta(days=30),
        created_at=datetime.now(UTC),
    )
    db.add(duplicate_module)
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_failed_multitable_create_rolls_back_package_and_modules(
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Service failures do not leave half-created package/module rows."""
    monkeypatch.setattr(services, "DEFAULT_RESEARCH_MODULE_TYPES", ("COMPANY", "COMPANY"))

    with pytest.raises(ResearchPersistenceConflict):
        await create_initial_package(
            db,
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            idempotency_key="rollback-base",
            request_hash="initial",
        )

    package_count = await db.scalar(
        select(func.count()).select_from(ResearchPackage).where(
            ResearchPackage.instrument_id == QIANGRUI_INSTRUMENT_ID
        )
    )
    module_count = await db.scalar(select(func.count()).select_from(ResearchModule))

    assert package_count == 0
    assert module_count == 0


def test_module_freshness_is_deterministic() -> None:
    """Freshness is derived from status and timestamps, not model judgment."""
    now = datetime(2026, 9, 12, tzinfo=UTC)

    unverified = ResearchModule(
        research_package_id="package",
        module_type="COMPANY",
        module_version=1,
        status="UNVERIFIED",
        source_refs=[],
        as_of=now,
        stale_after=now + timedelta(days=30),
    )
    fresh = ResearchModule(
        research_package_id="package",
        module_type="COMPANY",
        module_version=1,
        status="UNVERIFIED",
        source_refs=[],
        as_of=now,
        last_verified_at=now,
        stale_after=now + timedelta(days=1),
    )
    stale = ResearchModule(
        research_package_id="package",
        module_type="COMPANY",
        module_version=1,
        status="UNVERIFIED",
        source_refs=[],
        as_of=now,
        last_verified_at=now - timedelta(days=31),
        stale_after=now - timedelta(days=1),
    )
    failed = ResearchModule(
        research_package_id="package",
        module_type="COMPANY",
        module_version=1,
        status="FAILED",
        source_refs=[],
        as_of=now,
        stale_after=now + timedelta(days=30),
    )

    assert calculate_module_freshness(unverified, now=now) == "UNVERIFIED"
    assert calculate_module_freshness(fresh, now=now) == "FRESH"
    assert calculate_module_freshness(stale, now=now) == "STALE"
    assert calculate_module_freshness(failed, now=now) == "FAILED"
