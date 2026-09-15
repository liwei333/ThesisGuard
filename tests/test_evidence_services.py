"""WP-04-02 Evidence Domain Service contract tests.

These tests exercise service behavior against a real PostgreSQL database. They
intentionally stay below FastAPI/OpenAPI and above raw repositories: WP-04-02 is
the deterministic domain-service layer for the WP-04-01 persistence foundation.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio
from backend.evidence import services
from backend.evidence.errors import EvidenceDomainError
from backend.evidence.models import (
    EvidenceAuditEvent,
    EvidenceIdempotencyRecord,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

QIANGRUI_INSTRUMENT_ID = "11111111-1111-4111-8111-111111111111"
SHENLING_INSTRUMENT_ID = "22222222-2222-4222-8222-222222222222"
DEFAULT_ADMIN_DATABASE_URL = (
    "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
)
SOURCE_TYPE_ALLOWED_GRADES = {
    "COMPANY_ANNOUNCEMENT": {"S"},
    "FINANCIAL_REPORT": {"S"},
    "EXCHANGE_FILING": {"A"},
    "REGULATORY_DATA": {"A"},
    "OFFICIAL_DATA": {"A"},
    "POLICY_DOCUMENT": {"A"},
    "INVESTOR_RELATIONS": {"B"},
    "INSTITUTIONAL_SURVEY": {"B", "C"},
    "BROKER_RESEARCH": {"C"},
    "INDUSTRY_REPORT": {"C", "D"},
    "FINANCIAL_MEDIA": {"D"},
    "SOCIAL_MEDIA": {"E", "F"},
    "RUMOR": {"F"},
    "WEB_PAGE": {"D", "E", "F"},
    "USER_NOTE": {"F"},
}
FORBIDDEN_GRADE_CASES = [
    ("COMPANY_ANNOUNCEMENT", "A"),
    ("FINANCIAL_REPORT", "B"),
    ("EXCHANGE_FILING", "S"),
    ("REGULATORY_DATA", "S"),
    ("OFFICIAL_DATA", "S"),
    ("POLICY_DOCUMENT", "C"),
    ("INVESTOR_RELATIONS", "C"),
    ("INSTITUTIONAL_SURVEY", "A"),
    ("BROKER_RESEARCH", "B"),
    ("INDUSTRY_REPORT", "B"),
    ("FINANCIAL_MEDIA", "C"),
    ("SOCIAL_MEDIA", "D"),
    ("RUMOR", "E"),
    ("WEB_PAGE", "C"),
    ("USER_NOTE", "E"),
]


@pytest_asyncio.fixture
async def pg_sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Create a disposable PostgreSQL database and run Alembic migrations."""
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", DEFAULT_ADMIN_DATABASE_URL))
    test_db_name = f"tg_wp04_service_{uuid4().hex}"
    admin_db = admin_url.database or "postgres"

    admin_conn = await asyncpg.connect(
        user=admin_url.username,
        password=admin_url.password,
        host=admin_url.host or "127.0.0.1",
        port=admin_url.port or 5432,
        database=admin_db,
    )
    await admin_conn.execute(f'CREATE DATABASE "{test_db_name}"')
    await admin_conn.close()

    test_url = admin_url.set(database=test_db_name)
    test_database_url = test_url.render_as_string(hide_password=False)
    subprocess.run(  # noqa: ASYNC221
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        check=True,
        env={**os.environ, "DATABASE_URL": test_database_url},
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


def dt(year: int = 2026, month: int = 9, day: int = 12) -> datetime:
    return datetime(year, month, day, tzinfo=UTC)


async def source_with_version(
    db: AsyncSession,
    *,
    key_suffix: str = "base",
    source_type: str = "COMPANY_ANNOUNCEMENT",
    source_grade: str = "S",
    document_language: str | None = "zh-CN",
    versioned_metadata: dict | None = None,
) -> tuple[SourceDocument, SourceDocumentVersion]:
    source = await services.register_source_document(
        db,
        publisher_key="szse",
        publisher_name="深圳证券交易所",
        source_type=source_type,
        external_document_id=f"SZSE-{key_suffix}",
        canonical_url=f"https://example.test/report/{key_suffix}?utm_source=ignored",
        issuer_key="301128.SZ",
        issuer_name="强瑞技术",
        title="强瑞技术 2026 半年度报告",
        document_language=document_language,
        created_by_actor="IMPORTER",
        idempotency_key=f"source-{key_suffix}",
        as_of=dt(),
    )
    version = await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=0,
        version_reason="NEW_CONTENT",
        source_grade=source_grade,
        published_at=datetime(2026, 8, 31, tzinfo=UTC),
        observed_at=dt(),
        fetched_at=dt(),
        content_hash=f"{key_suffix}-content".ljust(64, "0")[:64],
        source_version_label="2026H1",
        media_type="application/pdf",
        object_key=f"sources/{key_suffix}.pdf",
        text_object_key=f"sources/{key_suffix}.txt",
        text_object_hash=f"{key_suffix}-text".ljust(64, "0")[:64],
        parser_name="tg-pdf",
        parser_version="1.0",
        versioned_metadata=versioned_metadata or {"page_count": 20, "period": "2026H1"},
        idempotency_key=f"source-version-{key_suffix}",
        as_of=dt(),
    )
    return source, version


async def append_source_version(
    db: AsyncSession,
    source: SourceDocument,
    *,
    key_suffix: str,
    expected_version: int,
    source_grade: str,
    version_reason: str = "NEW_CONTENT",
    content_hash: str | None = None,
    observed_at: datetime | None = None,
    fetched_at: datetime | None = None,
    object_key: str | None = None,
    text_object_key: str | None = None,
    text_object_hash: str | None = None,
    parser_name: str | None = "tg-pdf",
    parser_version: str | None = "1.0",
    versioned_metadata: dict | None = None,
    published_at: datetime | None = None,
    source_version_label: str | None = "2026H1",
    source_revision_id: str | None = None,
    source_status: str = "ACTIVE",
    source_status_changed_at: datetime | None = None,
    source_status_actor: str | None = None,
    source_status_reason: str | None = None,
    idempotency_key: str | None = None,
) -> SourceDocumentVersion:
    """Append or re-observe a source version with explicit contract fields."""
    return await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=expected_version,
        version_reason=version_reason,
        source_grade=source_grade,
        published_at=published_at or datetime(2026, 8, 31, tzinfo=UTC),
        observed_at=observed_at or dt(),
        fetched_at=fetched_at or dt(),
        content_hash=content_hash or f"{key_suffix}-content".ljust(64, "0")[:64],
        source_version_label=source_version_label,
        source_revision_id=source_revision_id,
        media_type="application/pdf",
        object_key=object_key or f"sources/{key_suffix}.pdf",
        text_object_key=text_object_key or f"sources/{key_suffix}.txt",
        text_object_hash=text_object_hash or f"{key_suffix}-text".ljust(64, "0")[:64],
        parser_name=parser_name,
        parser_version=parser_version,
        versioned_metadata=versioned_metadata or {"page_count": 20, "period": "2026H1"},
        source_status=source_status,
        source_status_changed_at=source_status_changed_at,
        source_status_actor=source_status_actor,
        source_status_reason=source_status_reason,
        idempotency_key=idempotency_key or f"source-version-{key_suffix}",
        as_of=dt(),
    )


async def evidence_fact(
    db: AsyncSession,
    *,
    key_suffix: str = "base",
    raw_value: str = "32.5%",
) -> EvidenceVersion:
    source, source_version = await source_with_version(db, key_suffix=key_suffix)
    return await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:gross_margin:2026H1",
        metric_key="gross_margin",
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 6, 30, tzinfo=UTC),
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title="强瑞技术 2026H1 毛利率",
        display_text=f"2026H1 毛利率为 {raw_value}",
        raw_value=raw_value,
        raw_unit="percent",
        normalized_value=Decimal(raw_value.rstrip("%")),
        normalized_unit="percent",
        as_of=datetime(2026, 8, 31, tzinfo=UTC),
        effective_from=datetime(2026, 8, 31, tzinfo=UTC),
        locators=[
            services.SourceLocatorInput(
                locator_type="PAGE",
                raw_locator="p.12",
                short_citation="2026H1 p.12",
                locator_payload={"page_number": 12},
                quote_hash=f"{key_suffix}-quote".ljust(64, "0")[:64],
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
                link_metadata={"scope": "primary"},
            )
        ],
        extractor_name="tg-parser",
        extractor_version="1.0",
        created_by_actor="IMPORTER",
        idempotency_key=f"evidence-{key_suffix}",
        created_at=dt(),
    )


def assert_error(exc_info: pytest.ExceptionInfo[EvidenceDomainError], code: str) -> None:
    assert exc_info.value.code == code
    assert isinstance(exc_info.value.message, str)


async def evidence_table_counts(db: AsyncSession) -> dict[str, int]:
    """Return R1A tables that must not gain rows after pre-write validation errors."""
    counts: dict[str, int] = {}
    for key, model in (
        ("series", EvidenceSeries),
        ("version", EvidenceVersion),
        ("locator", EvidenceSourceLocator),
        ("idempotency", EvidenceIdempotencyRecord),
        ("audit", EvidenceAuditEvent),
    ):
        counts[key] = int(await db.scalar(select(func.count()).select_from(model)) or 0)
    return counts


async def create_source_backed_fact_with_locators(
    db: AsyncSession,
    *,
    key_suffix: str,
    locators: list[services.SourceLocatorInput],
    versioned_metadata: dict | None = None,
) -> tuple[SourceDocumentVersion, EvidenceVersion]:
    """Create a source-backed FACT through the public service command."""
    source, source_version = await source_with_version(
        db,
        key_suffix=key_suffix,
        versioned_metadata=versioned_metadata
        or {
            "page_count": 20,
            "paragraph_count_by_page": {"12": 3},
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {"12:1": {"row_count": 5, "column_count": 4}},
            "duration_seconds": 120,
        },
    )
    created = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"locator-r1:{key_suffix}",
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title=f"Locator R1 {key_suffix}",
        display_text=f"Locator R1 {key_suffix}",
        as_of=dt(),
        locators=locators,
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key=f"locator-r1-{key_suffix}",
    )
    return source_version, created


def test_canonical_helpers_are_deterministic_and_url_identity_is_normalized() -> None:
    """Request hashes and URL identities are stable across key/query ordering."""
    left = {
        "url": "HTTPS://Example.COM:443/a/b?utm_source=x&b=2&a=1#fragment",
        "decimal": Decimal("32.50"),
        "time": datetime(2026, 9, 12, 8, 0, tzinfo=UTC),
    }
    right = {
        "time": datetime(2026, 9, 12, 8, 0, tzinfo=UTC),
        "decimal": Decimal("32.50"),
        "url": "https://example.com/a/b?a=1&b=2",
    }

    left_url = left["url"]
    assert isinstance(left_url, str)
    assert services.canonicalize_url(left_url) == "https://example.com/a/b?a=1&b=2"
    assert services.stable_hash(left) == services.stable_hash(right)


@pytest.mark.parametrize(
    ("source_type", "source_grade"),
    [
        (source_type, source_grade)
        for source_type, source_grades in SOURCE_TYPE_ALLOWED_GRADES.items()
        for source_grade in sorted(source_grades)
    ],
)
async def test_source_type_grade_matrix_accepts_every_frozen_allowed_pair(
    db: AsyncSession,
    source_type: str,
    source_grade: str,
) -> None:
    """Every frozen SourceType/SourceGrade pair is accepted by source-version import."""
    source, version = await source_with_version(
        db,
        key_suffix=f"allowed-{source_type.lower()}-{source_grade.lower()}",
        source_type=source_type,
        source_grade=source_grade,
    )

    assert source.source_type == source_type
    assert version.source_grade == source_grade


@pytest.mark.parametrize(("source_type", "source_grade"), FORBIDDEN_GRADE_CASES)
async def test_source_type_grade_matrix_rejects_representative_forbidden_pairs(
    db: AsyncSession,
    source_type: str,
    source_grade: str,
) -> None:
    """Every SourceType has at least one forbidden pair covered by PostgreSQL tests."""
    with pytest.raises(EvidenceDomainError) as exc_info:
        await source_with_version(
            db,
            key_suffix=f"forbidden-{source_type.lower()}-{source_grade.lower()}",
            source_type=source_type,
            source_grade=source_grade,
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_GRADE")
    assert exc_info.value.details["source_type"] == source_type
    assert exc_info.value.details["source_grade"] == source_grade


async def test_register_source_and_append_version_are_idempotent(db: AsyncSession) -> None:
    """Source identity upsert and exact source-version replay are idempotent."""
    source, version = await source_with_version(db, key_suffix="idempotent")
    await db.commit()

    repeated_source = await services.register_source_document(
        db,
        publisher_key="szse",
        publisher_name="深圳证券交易所",
        source_type="COMPANY_ANNOUNCEMENT",
        external_document_id="SZSE-idempotent",
        canonical_url="https://example.test/report/idempotent",
        issuer_key="301128.SZ",
        issuer_name="强瑞技术",
        title="强瑞技术 2026 半年度报告",
        document_language="zh-CN",
        created_by_actor="IMPORTER",
        idempotency_key="source-idempotent",
        as_of=dt(),
    )
    assert repeated_source.id == source.id

    repeated_version = await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=0,
        version_reason="NEW_CONTENT",
        source_grade="S",
        published_at=datetime(2026, 8, 31, tzinfo=UTC),
        observed_at=dt(),
        fetched_at=dt(),
        content_hash="idempotent-content".ljust(64, "0")[:64],
        source_version_label="2026H1",
        media_type="application/pdf",
        object_key="sources/idempotent.pdf",
        text_object_key="sources/idempotent.txt",
        text_object_hash="idempotent-text".ljust(64, "0")[:64],
        parser_name="tg-pdf",
        parser_version="1.0",
        versioned_metadata={"page_count": 20, "period": "2026H1"},
        idempotency_key="source-version-idempotent",
        as_of=dt(),
    )
    assert repeated_version.id == version.id


def test_source_version_fingerprint_is_deterministic_and_uses_contract_fields_only() -> None:
    """Source-version identity is distinct from request hash and ignores observation/storage fields."""
    base = {
        "content_hash": "a" * 64,
        "media_type": "application/pdf",
        "source_grade": "S",
        "published_at": datetime(2026, 9, 12, 8, 0, tzinfo=UTC),
        "source_version_label": "2026H1",
        "source_revision_id": "rev-1",
        "document_language": "zh-CN",
        "parser_name": "tg-pdf",
        "parser_version": "1.0",
        "text_object_hash": "b" * 64,
        "source_status": "ACTIVE",
        "source_status_changed_at": None,
        "source_status_reason": None,
        "source_status_actor": None,
        "versioned_metadata": {"period": "2026H1", "nested": {"b": 2, "a": 1}},
    }
    equivalent = {
        **base,
        "published_at": "2026-09-12T16:00:00+08:00",
        "versioned_metadata": {"nested": {"a": 1, "b": 2}, "period": "2026H1"},
        "observed_at": datetime(2026, 9, 13, tzinfo=UTC),
        "fetched_at": datetime(2026, 9, 14, tzinfo=UTC),
        "object_key": "sources/changed.pdf",
        "text_object_key": "sources/changed.txt",
        "idempotency_key": "ignored",
        "version_reason": "METADATA_CORRECTION",
        "source_document_id": "ignored-source",
    }

    assert services.source_version_fingerprint(base) == services.source_version_fingerprint(
        equivalent
    )

    for field, value in (
        ("content_hash", "c" * 64),
        ("source_grade", "A"),
        ("published_at", datetime(2026, 9, 13, tzinfo=UTC)),
        ("source_version_label", "2026Q3"),
        ("source_revision_id", "rev-2"),
        ("document_language", "en"),
        ("parser_name", "tg-html"),
        ("parser_version", "2.0"),
        ("text_object_hash", "d" * 64),
        ("source_status", "RETRACTED"),
        ("source_status_changed_at", datetime(2026, 9, 15, tzinfo=UTC)),
        ("source_status_reason", "issuer notice"),
        ("source_status_actor", "IMPORTER"),
        ("versioned_metadata", {"period": "2026H1", "restated": True}),
    ):
        changed = {**base, field: value}
        if field == "source_status":
            changed |= {
                "source_status_changed_at": datetime(2026, 9, 15, tzinfo=UTC),
                "source_status_reason": "issuer notice",
                "source_status_actor": "IMPORTER",
            }
        assert services.source_version_fingerprint(changed) != services.source_version_fingerprint(
            base
        )


async def test_same_fingerprint_new_key_reobserves_existing_source_version(
    db: AsyncSession,
) -> None:
    """A new idempotency key with unchanged fingerprint reuses S1 and records observation evidence."""
    source, first = await source_with_version(db, key_suffix="reobserve")
    await db.commit()

    audit_before = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))
    replay = await append_source_version(
        db,
        source,
        key_suffix="reobserve-later",
        expected_version=1,
        source_grade="S",
        content_hash="reobserve-content".ljust(64, "0")[:64],
        observed_at=dt(day=13),
        fetched_at=dt(day=13),
        object_key="sources/reobserve-reused.pdf",
        text_object_key="sources/reobserve-reused.txt",
        text_object_hash="reobserve-text".ljust(64, "0")[:64],
        idempotency_key="source-version-reobserve-new-key",
    )
    await db.commit()

    count = await db.scalar(
        select(func.count())
        .select_from(SourceDocumentVersion)
        .where(SourceDocumentVersion.source_document_id == source.id)
    )
    idempotency_count = await db.scalar(
        select(func.count())
        .select_from(EvidenceIdempotencyRecord)
        .where(EvidenceIdempotencyRecord.response_ref_id == first.id)
    )
    audit_after = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))

    assert replay.id == first.id
    assert count == 1
    assert idempotency_count == 2
    assert audit_before is not None and audit_after is not None
    assert audit_after == audit_before + 1


async def test_same_bytes_can_append_grade_metadata_and_retraction_source_versions(
    db: AsyncSession,
) -> None:
    """Same canonical bytes can append N+1 for grade, metadata, and lifecycle identity changes."""
    shared_content = "same-bytes-content".ljust(64, "0")[:64]
    source = await services.register_source_document(
        db,
        publisher_key="survey-provider",
        publisher_name="Institutional Survey Provider",
        source_type="INSTITUTIONAL_SURVEY",
        external_document_id="SURVEY-same-bytes",
        canonical_url="https://example.test/survey/same-bytes",
        issuer_key="301128.SZ",
        issuer_name="强瑞技术",
        title="强瑞技术机构调研",
        document_language="zh-CN",
        created_by_actor="IMPORTER",
        idempotency_key="same-bytes-source",
        as_of=dt(),
    )
    first = await append_source_version(
        db,
        source,
        key_suffix="same-bytes-initial",
        expected_version=0,
        source_grade="B",
        content_hash=shared_content,
        object_key="sources/reused.pdf",
        text_object_hash="same-bytes-text".ljust(64, "0")[:64],
        idempotency_key="same-bytes-initial",
    )
    await db.commit()

    grade = await append_source_version(
        db,
        source,
        key_suffix="same-bytes-grade",
        expected_version=1,
        version_reason="GRADE_RECLASSIFICATION",
        source_grade="C",
        content_hash=shared_content,
        object_key="sources/reused.pdf",
        text_object_hash="same-bytes-text".ljust(64, "0")[:64],
        idempotency_key="same-bytes-grade",
    )
    metadata = await append_source_version(
        db,
        source,
        key_suffix="same-bytes-metadata",
        expected_version=2,
        version_reason="METADATA_CORRECTION",
        source_grade="C",
        content_hash=shared_content,
        object_key="sources/reused.pdf",
        text_object_hash="same-bytes-text".ljust(64, "0")[:64],
        versioned_metadata={"page_count": 20, "period": "2026H1", "corrected": True},
        idempotency_key="same-bytes-metadata",
    )
    retracted = await append_source_version(
        db,
        source,
        key_suffix="same-bytes-retracted",
        expected_version=3,
        version_reason="RETRACTION_NOTICE",
        source_grade="C",
        content_hash=shared_content,
        object_key="sources/reused.pdf",
        text_object_hash="same-bytes-text".ljust(64, "0")[:64],
        versioned_metadata={"page_count": 20, "period": "2026H1", "corrected": True},
        source_status="RETRACTED",
        source_status_changed_at=dt(day=13),
        source_status_actor="IMPORTER",
        source_status_reason="issuer retracted document",
        idempotency_key="same-bytes-retracted",
    )
    await db.commit()

    assert [first.version, grade.version, metadata.version, retracted.version] == [1, 2, 3, 4]
    assert (
        len(
            {
                first.version_fingerprint,
                grade.version_fingerprint,
                metadata.version_fingerprint,
                retracted.version_fingerprint,
            }
        )
        == 4
    )
    assert {item.object_key for item in (first, grade, metadata, retracted)} == {
        "sources/reused.pdf"
    }


async def test_concurrent_identical_source_import_reconciles_to_one_version(
    pg_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """Concurrent identical-fingerprint imports create at most one SourceDocumentVersion."""
    async with pg_sessionmaker() as setup:
        source = await services.register_source_document(
            setup,
            publisher_key="szse",
            publisher_name="深圳证券交易所",
            source_type="COMPANY_ANNOUNCEMENT",
            external_document_id="SZSE-concurrent-source",
            canonical_url="https://example.test/concurrent-source",
            issuer_key="301128.SZ",
            issuer_name="强瑞技术",
            title="强瑞技术公告",
            document_language="zh-CN",
            created_by_actor="IMPORTER",
            idempotency_key="concurrent-source",
            as_of=dt(),
        )
        source_id = source.id
        await setup.commit()

    async def import_same(key: str) -> str:
        async with pg_sessionmaker() as session:
            source = await services.get_source_document(session, source_id)
            assert source is not None
            version = await append_source_version(
                session,
                source,
                key_suffix="concurrent-source-version",
                expected_version=0,
                source_grade="S",
                content_hash="concurrent-source-content".ljust(64, "0")[:64],
                text_object_hash="concurrent-source-text".ljust(64, "0")[:64],
                idempotency_key=key,
            )
            await session.commit()
            return version.id

    version_ids = await asyncio.gather(
        import_same("concurrent-source-a"),
        import_same("concurrent-source-b"),
    )

    async with pg_sessionmaker() as verify:
        version_count = await verify.scalar(
            select(func.count())
            .select_from(SourceDocumentVersion)
            .where(SourceDocumentVersion.source_document_id == source_id)
        )
        idempotency_count = await verify.scalar(
            select(func.count())
            .select_from(EvidenceIdempotencyRecord)
            .where(EvidenceIdempotencyRecord.response_ref_id == version_ids[0])
        )

    assert version_ids[0] == version_ids[1]
    assert version_count == 1
    assert idempotency_count == 2


async def test_invalid_source_lifecycle_tuple_rolls_back_source_version_idempotency_and_audit(
    db: AsyncSession,
) -> None:
    """Lifecycle audit tuple is validated before source-version/idempotency/audit rows persist."""
    source, _ = await source_with_version(db, key_suffix="lifecycle")
    await db.commit()
    before_versions = await db.scalar(select(func.count()).select_from(SourceDocumentVersion))
    before_idempotency = await db.scalar(
        select(func.count()).select_from(EvidenceIdempotencyRecord)
    )
    before_audit = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))

    with pytest.raises(EvidenceDomainError) as partial:
        await append_source_version(
            db,
            source,
            key_suffix="bad-lifecycle",
            expected_version=1,
            source_grade="S",
            source_status="RETRACTED",
            source_status_changed_at=dt(day=13),
            source_status_actor=None,
            source_status_reason="partial tuple",
            idempotency_key="bad-lifecycle",
        )
    assert_error(partial, "EVIDENCE_VALIDATION_ERROR")

    assert (
        await db.scalar(select(func.count()).select_from(SourceDocumentVersion)) == before_versions
    )
    assert (
        await db.scalar(select(func.count()).select_from(EvidenceIdempotencyRecord))
        == before_idempotency
    )
    assert await db.scalar(select(func.count()).select_from(EvidenceAuditEvent)) == before_audit


async def test_create_source_backed_evidence_persists_children_queries_and_audit(
    db: AsyncSession,
) -> None:
    """A source-backed FACT creates one series, one version, exact locators, and audit."""
    created = await evidence_fact(db, key_suffix="create")
    await db.commit()

    exact = await services.get_exact_evidence_version(db, created.id)
    current = await services.get_current_evidence(db, created.evidence_series_id)
    by_instrument = await services.list_evidence_by_instrument(db, QIANGRUI_INSTRUMENT_ID)
    by_source = await services.list_evidence_by_source_document_version(
        db,
        created.source_document_version_id or "",
    )
    valid = await services.get_current_valid_evidence(db, created.evidence_series_id)

    assert exact is not None
    assert exact.version == 1
    assert exact.source_grade_snapshot == "S"
    assert len(exact.source_locators) == 1
    assert exact.source_locators[0].raw_locator == "p.12"
    assert len(exact.instrument_links) == 1
    assert current is not None and current.id == created.id
    assert valid is not None and valid.id == created.id
    assert [item.id for item in by_source] == [created.id]
    assert [item.id for item in by_instrument] == [created.id]

    audit_count = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))
    assert audit_count and audit_count >= 3


async def test_create_evidence_rejects_bad_locator_provenance_and_links(
    db: AsyncSession,
) -> None:
    """Service validation fails before database constraints for contract counterexamples."""
    source, source_version = await source_with_version(db, key_suffix="invalid")

    with pytest.raises(EvidenceDomainError) as bad_locator:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key="bad-locator",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Bad locator",
            display_text="Bad locator",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="PAGE",
                    raw_locator="p.999",
                    short_citation="bad",
                    locator_payload={"page_number": 999},
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key="bad-locator",
        )
    assert_error(bad_locator, "EVIDENCE_INVALID_SOURCE_LOCATOR")

    with pytest.raises(EvidenceDomainError) as bad_provenance:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key="manual-fact",
            provenance_kind="MANUAL",
            origin_key="manual:fact",
            display_title="Manual fact",
            display_text="Manual facts are forbidden",
            as_of=dt(),
            manual_entry_reason="manual correction",
            manual_observed_at=dt(),
            created_by_actor="USER",
            idempotency_key="manual-fact",
        )
    assert_error(bad_provenance, "EVIDENCE_INVALID_PROVENANCE")

    first = await evidence_fact(db, key_suffix="link-a", raw_value="31.0%")
    with pytest.raises(EvidenceDomainError) as bad_corroboration:
        await services.create_corroboration_link(
            db,
            left_evidence_version_id=first.id,
            right_evidence_version_id=first.id,
            relation_type="CORROBORATES",
            created_by_actor="IMPORTER",
        )
    assert_error(bad_corroboration, "EVIDENCE_INVALID_CORROBORATION_LINK")


@pytest.mark.parametrize(
    ("locator_type", "payload"),
    [
        ("PAGE", {"page_number": 12}),
        ("PAGE_PARAGRAPH", {"page_number": 12, "paragraph_index": 2}),
        ("SECTION", {"section_title": "Management discussion"}),
        ("TABLE", {"page_number": 12, "table_index": 1}),
        ("TABLE_CELL", {"page_number": 12, "table_index": 1, "row_index": 2, "column_index": 3}),
        ("WEB_ANCHOR", {"canonical_url": "https://example.test/report", "anchor": "risk"}),
        ("TIME_RANGE", {"start_seconds": 10, "end_seconds": 20}),
    ],
)
async def test_all_contract_locator_types_accept_valid_payloads(
    db: AsyncSession,
    locator_type: str,
    payload: dict,
) -> None:
    """All frozen locator types accept contract field names and available parser bounds."""
    source, source_version = await source_with_version(
        db,
        key_suffix=f"locator-{locator_type.lower()}",
        versioned_metadata={
            "page_count": 20,
            "paragraph_count_by_page": {"12": 3},
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {"12:1": {"row_count": 5, "column_count": 4}},
            "duration_seconds": 120,
        },
    )
    created = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"locator:{locator_type}",
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title=f"{locator_type} locator",
        display_text=f"{locator_type} locator",
        as_of=dt(),
        locators=[
            services.SourceLocatorInput(
                locator_type=locator_type,
                raw_locator=locator_type,
                short_citation=locator_type,
                locator_payload=payload,
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key=f"locator-{locator_type.lower()}",
    )

    exact = await services.get_exact_evidence_version(db, created.id)
    assert exact is not None
    assert exact.source_locators[0].locator_payload == payload


@pytest.mark.parametrize(
    ("locator_type", "payload", "path"),
    [
        ("PAGE", {"page": 12}, "locator_payload.page_number"),
        ("PAGE_PARAGRAPH", {"page_number": 12}, "locator_payload.paragraph_index"),
        ("SECTION", {}, "locator_payload.section"),
        ("TABLE", {"page_number": 12}, "locator_payload.table_index"),
        (
            "TABLE_CELL",
            {"page_number": 12, "table_index": 1, "row_index": 2},
            "locator_payload.column_index",
        ),
        ("WEB_ANCHOR", {"anchor": "risk"}, "locator_payload.canonical_url"),
        ("TIME_RANGE", {"start_seconds": 20, "end_seconds": 10}, "locator_payload.time_range"),
    ],
)
async def test_all_contract_locator_types_reject_invalid_payloads_without_partial_writes(
    db: AsyncSession,
    locator_type: str,
    payload: dict,
    path: str,
) -> None:
    """Invalid locators fail before Evidence/idempotency/audit rows are retained."""
    source, source_version = await source_with_version(
        db,
        key_suffix=f"bad-locator-{locator_type.lower()}",
        versioned_metadata={
            "page_count": 20,
            "paragraph_count_by_page": {"12": 3},
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {"12:1": {"row_count": 5, "column_count": 4}},
            "duration_seconds": 120,
        },
    )
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"bad-locator:{locator_type}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title=f"Bad {locator_type} locator",
            display_text=f"Bad {locator_type} locator",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type=locator_type,
                    raw_locator=locator_type,
                    short_citation=locator_type,
                    locator_payload=payload,
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"bad-locator-{locator_type.lower()}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == path
    assert await evidence_table_counts(db) == before


async def test_web_anchor_canonical_url_only_locator_succeeds(db: AsyncSession) -> None:
    """WEB_ANCHOR only requires canonical_url; selector fields are optional."""
    payload = {"canonical_url": "https://example.test/report"}
    _, created = await create_source_backed_fact_with_locators(
        db,
        key_suffix="web-anchor-url-only",
        locators=[
            services.SourceLocatorInput(
                locator_type="WEB_ANCHOR",
                raw_locator="https://example.test/report",
                short_citation="report",
                locator_payload=payload,
            )
        ],
    )

    exact = await services.get_exact_evidence_version(db, created.id)
    assert exact is not None
    assert exact.source_locators[0].locator_payload == payload


@pytest.mark.parametrize(
    ("payload", "path"),
    [
        ({"canonical_url": "https://example.test/report", "anchor": ""}, "locator_payload.anchor"),
        (
            {"canonical_url": "https://example.test/report", "css_selector": 42},
            "locator_payload.css_selector",
        ),
        (
            {"canonical_url": "https://example.test/report", "text_quote_hash": ""},
            "locator_payload.text_quote_hash",
        ),
    ],
)
async def test_web_anchor_optional_fields_reject_invalid_structures_without_partial_writes(
    db: AsyncSession,
    payload: dict,
    path: str,
) -> None:
    """WEB_ANCHOR optional selectors are optional but structurally validated if present."""
    source, source_version = await source_with_version(db, key_suffix=f"bad-web-{path}")
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"bad-web:{path}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Bad web anchor",
            display_text="Bad web anchor",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="WEB_ANCHOR",
                    raw_locator="web",
                    short_citation="web",
                    locator_payload=payload,
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"bad-web-{path}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == path
    assert await evidence_table_counts(db) == before


@pytest.mark.parametrize(
    "canonical_url",
    ["", "   ", "\t\n", 42],
)
async def test_web_anchor_rejects_missing_blank_or_non_string_canonical_url_without_partial_writes(
    db: AsyncSession,
    canonical_url: object,
) -> None:
    """WEB_ANCHOR canonical_url must be a nonblank string."""
    source, source_version = await source_with_version(
        db, key_suffix=f"bad-web-url-{canonical_url!r}"
    )
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"bad-web-url:{canonical_url!r}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Bad web canonical URL",
            display_text="Bad web canonical URL",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="WEB_ANCHOR",
                    raw_locator="web",
                    short_citation="web",
                    locator_payload={"canonical_url": canonical_url},
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"bad-web-url-{canonical_url!r}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == "locator_payload.canonical_url"
    assert await evidence_table_counts(db) == before


@pytest.mark.parametrize(
    "payload",
    [
        {"page_number": 12, "table_index": 1},
        {"page_number": 12, "table_index": 1, "row_index": 5, "column_index": 4},
        {"page_number": 12, "table_index": 1, "cell_ref": "B2"},
    ],
)
async def test_table_locator_accepts_level_and_optional_coordinate_forms(
    db: AsyncSession,
    payload: dict,
) -> None:
    """TABLE is valid at table level and validates optional cell coordinates when supplied."""
    _, created = await create_source_backed_fact_with_locators(
        db,
        key_suffix=f"table-{services.stable_hash(payload)[:8]}",
        locators=[
            services.SourceLocatorInput(
                locator_type="TABLE",
                raw_locator="p.12 table 1",
                short_citation="table 1",
                locator_payload=payload,
            )
        ],
    )

    exact = await services.get_exact_evidence_version(db, created.id)
    assert exact is not None
    assert exact.source_locators[0].locator_payload == payload


@pytest.mark.parametrize(
    ("payload", "path"),
    [
        ({"page_number": 12, "table_index": 1, "row_index": 99}, "locator_payload.row_index"),
        ({"page_number": 12, "table_index": 1, "column_index": 99}, "locator_payload.column_index"),
        ({"page_number": 12, "table_index": 1, "row_index": 0}, "locator_payload.row_index"),
        ({"page_number": 12, "table_index": 1, "cell_ref": ""}, "locator_payload.cell_ref"),
    ],
)
async def test_table_locator_rejects_invalid_optional_coordinates_without_partial_writes(
    db: AsyncSession,
    payload: dict,
    path: str,
) -> None:
    """TABLE optional coordinates fail precisely and before mutable Evidence rows remain."""
    source, source_version = await source_with_version(
        db,
        key_suffix=f"bad-table-{path}",
        versioned_metadata={
            "page_count": 20,
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {"12:1": {"row_count": 5, "column_count": 4}},
        },
    )
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"bad-table:{path}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Bad table locator",
            display_text="Bad table locator",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="TABLE",
                    raw_locator="table",
                    short_citation="table",
                    locator_payload=payload,
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"bad-table-{path}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == path
    assert await evidence_table_counts(db) == before


@pytest.mark.parametrize(
    "payload",
    [
        {"page_number": 12, "table_index": 1, "cell_ref": "B2"},
        {"page_number": 12, "table_index": 1, "row_index": 2, "column_index": 2},
        {"page_number": 12, "table_index": 1, "cell_ref": "B2", "row_index": 2, "column_index": 2},
    ],
)
async def test_table_cell_accepts_cell_ref_or_complete_numeric_coordinates(
    db: AsyncSession,
    payload: dict,
) -> None:
    """TABLE_CELL accepts either a cell_ref representation or complete numeric coordinates."""
    _, created = await create_source_backed_fact_with_locators(
        db,
        key_suffix=f"cell-{services.stable_hash(payload)[:8]}",
        locators=[
            services.SourceLocatorInput(
                locator_type="TABLE_CELL",
                raw_locator="p.12 table 1 cell",
                short_citation="cell",
                locator_payload=payload,
            )
        ],
    )

    exact = await services.get_exact_evidence_version(db, created.id)
    assert exact is not None
    assert exact.source_locators[0].locator_payload == payload


@pytest.mark.parametrize(
    ("payload", "path"),
    [
        ({"page_number": 12, "table_index": 1, "row_index": 2}, "locator_payload.column_index"),
        ({"page_number": 12, "table_index": 1, "column_index": 2}, "locator_payload.row_index"),
        (
            {"page_number": 12, "table_index": 1, "cell_ref": "B2", "row_index": 2},
            "locator_payload.column_index",
        ),
        (
            {"page_number": 12, "table_index": 1, "cell_ref": "B2", "column_index": 2},
            "locator_payload.row_index",
        ),
        ({"page_number": 12, "table_index": 1, "cell_ref": ""}, "locator_payload.cell_ref"),
        (
            {"page_number": 12, "table_index": 1, "row_index": 99, "column_index": 2},
            "locator_payload.row_index",
        ),
        (
            {"page_number": 12, "table_index": 1, "row_index": 2, "column_index": 99},
            "locator_payload.column_index",
        ),
        (
            {
                "page_number": 12,
                "table_index": 1,
                "cell_ref": "B2",
                "row_index": 99,
                "column_index": 2,
            },
            "locator_payload.row_index",
        ),
    ],
)
async def test_table_cell_rejects_partial_invalid_or_out_of_bounds_forms_without_partial_writes(
    db: AsyncSession,
    payload: dict,
    path: str,
) -> None:
    """Invalid TABLE_CELL representations fail precisely without durable Evidence residue."""
    source, source_version = await source_with_version(
        db,
        key_suffix=f"bad-cell-{path}",
        versioned_metadata={
            "page_count": 20,
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {"12:1": {"row_count": 5, "column_count": 4}},
        },
    )
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"bad-cell:{path}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Bad table cell locator",
            display_text="Bad table cell locator",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="TABLE_CELL",
                    raw_locator="cell",
                    short_citation="cell",
                    locator_payload=payload,
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"bad-cell-{path}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == path
    assert await evidence_table_counts(db) == before


async def test_source_backed_evidence_without_locator_reports_source_version_and_path(
    db: AsyncSession,
) -> None:
    """Missing SOURCE_BACKED locators fail with stable details before Evidence writes."""
    source, source_version = await source_with_version(db, key_suffix="missing-locators")
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key="missing-locators",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Missing locators",
            display_text="Missing locators",
            as_of=dt(),
            locators=[],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key="missing-locators",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == "locators"
    assert await evidence_table_counts(db) == before


@pytest.mark.parametrize(
    ("raw_locator", "short_citation", "path"),
    [
        ("", "short", "raw_locator"),
        ("raw", "", "short_citation"),
    ],
)
async def test_locator_raw_locator_and_short_citation_report_exact_missing_path(
    db: AsyncSession,
    raw_locator: str,
    short_citation: str,
    path: str,
) -> None:
    """raw_locator and short_citation are validated separately with exact paths."""
    source, source_version = await source_with_version(db, key_suffix=f"missing-{path}")
    before = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as exc_info:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="FACT",
            claim_key=f"missing-{path}",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title=f"Missing {path}",
            display_text=f"Missing {path}",
            as_of=dt(),
            locators=[
                services.SourceLocatorInput(
                    locator_type="PAGE",
                    raw_locator=raw_locator,
                    short_citation=short_citation,
                    locator_payload={"page_number": 12},
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key=f"missing-{path}",
        )

    assert_error(exc_info, "EVIDENCE_INVALID_SOURCE_LOCATOR")
    assert exc_info.value.details["source_document_version_id"] == source_version.id
    assert exc_info.value.details["locator_path"] == path
    assert await evidence_table_counts(db) == before


async def test_revision_lifecycle_and_tombstone_are_append_only(db: AsyncSession) -> None:
    """Correction, review, verification, dispute, and invalidation append immutable versions."""
    created = await evidence_fact(db, key_suffix="life")
    await db.commit()

    corrected_base = await evidence_fact(db, key_suffix="life-correct", raw_value="32.0%")
    corrected = await services.revise_correct_evidence(
        db,
        evidence_series_id=corrected_base.evidence_series_id,
        expected_version=1,
        display_text="2026H1 毛利率为 33.0%",
        raw_value="33.0%",
        normalized_value=Decimal("33.0"),
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="parser correction",
        idempotency_key="life-correct",
        trusted_correction_rule="same-source-parser-v1",
    )
    review = await services.request_review(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=1,
        reason="needs review",
        actor="USER",
        idempotency_key="life-review",
        as_of=dt(day=14),
    )
    verified = await services.verify_or_reject(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=2,
        decision="VERIFIED",
        reason="review passed",
        actor="USER",
        idempotency_key="life-verify",
        as_of=dt(day=15),
    )
    disputed = await services.mark_disputed(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=3,
        reason="issuer later restated",
        actor="USER",
        idempotency_key="life-dispute",
        as_of=dt(day=16),
    )
    invalidated = await services.retract_or_invalidate(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=4,
        target_status="INVALIDATED",
        reason="restatement invalidates old fact",
        actor="IMPORTER",
        idempotency_key="life-invalidate",
        as_of=dt(day=17),
    )
    await db.commit()

    assert corrected.version == 2
    assert corrected.supersedes_evidence_version_id == corrected_base.id
    assert review.verification_status == "PENDING_REVIEW"
    assert verified.verification_status == "VERIFIED"
    assert disputed.verification_status == "DISPUTED"
    assert invalidated.verification_status == "INVALIDATED"
    assert invalidated.display_title == disputed.display_title
    assert len(invalidated.source_locators) == len(disputed.source_locators)

    history = await services.list_evidence_history(db, created.evidence_series_id)
    assert [item.version for item in history] == [1, 2, 3, 4, 5]

    unavailable = await services.get_current_valid_evidence(db, created.evidence_series_id)
    assert unavailable is None


async def test_state_transition_expected_version_and_idempotency_conflicts(
    db: AsyncSession,
) -> None:
    """Invalid lifecycle transitions and stale expected versions raise stable errors."""
    created = await evidence_fact(db, key_suffix="conflict")
    await db.commit()

    with pytest.raises(EvidenceDomainError) as stale:
        await services.request_review(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=0,
            reason="stale",
            actor="USER",
            idempotency_key="conflict-stale",
        )
    assert_error(stale, "EVIDENCE_VERSION_CONFLICT")
    assert stale.value.expected_version == 0
    assert stale.value.current_version == 1

    await services.request_review(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=1,
        reason="first review",
        actor="USER",
        idempotency_key="conflict-review",
    )

    with pytest.raises(EvidenceDomainError) as invalid_transition:
        await services.request_review(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=2,
            reason="already pending",
            actor="USER",
            idempotency_key="conflict-review-2",
        )
    assert_error(invalid_transition, "EVIDENCE_INVALID_STATE_TRANSITION")

    with pytest.raises(EvidenceDomainError) as idempotency:
        await services.request_review(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=1,
            reason="different request",
            actor="USER",
            idempotency_key="conflict-review",
        )
    assert_error(idempotency, "EVIDENCE_IDEMPOTENCY_CONFLICT")


async def test_identity_changing_correction_creates_replacement_series(
    db: AsyncSession,
) -> None:
    """Identity-changing corrections create a new series and leave the old one immutable."""
    prior = await evidence_fact(db, key_suffix="replacement")
    await db.commit()

    assert prior.source_document_version is not None
    replacement = await services.create_replacement_evidence_series(
        db,
        prior_evidence_version_id=prior.id,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:net_margin:2026H1",
        metric_key="net_margin",
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 6, 30, tzinfo=UTC),
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=prior.source_document_version.source_document_id,
        source_document_version_id=prior.source_document_version_id,
        display_title="强瑞技术 2026H1 净利率",
        display_text="2026H1 净利率为 11.2%",
        raw_value="11.2%",
        raw_unit="percent",
        normalized_value=Decimal("11.2"),
        normalized_unit="percent",
        as_of=prior.as_of,
        effective_from=prior.effective_from,
        locators=[
            services.SourceLocatorInput(
                locator_type="PAGE",
                raw_locator="p.13",
                short_citation="2026H1 p.13",
                locator_payload={"page_number": 13},
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="metric identity was wrong",
        idempotency_key="replacement",
    )
    await db.commit()

    assert replacement.version == 1
    assert replacement.evidence_series_id != prior.evidence_series_id
    assert replacement.supersedes_evidence_version_id == prior.id
    assert replacement.status_change_kind == "CORRECTION"

    old_history = await services.list_evidence_history(db, prior.evidence_series_id)
    assert [item.id for item in old_history] == [prior.id]


async def test_concurrent_revision_allows_only_one_next_version(
    pg_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """SELECT FOR UPDATE plus expected_version prevents duplicate N+1 writes."""
    async with pg_sessionmaker() as setup:
        created = await evidence_fact(setup, key_suffix="concurrent")
        series_id = created.evidence_series_id
        await setup.commit()

    async def correct(key: str, value: str) -> str:
        async with pg_sessionmaker() as session:
            try:
                await services.revise_correct_evidence(
                    session,
                    evidence_series_id=series_id,
                    expected_version=1,
                    display_text=f"2026H1 毛利率为 {value}",
                    raw_value=value,
                    normalized_value=Decimal(value.rstrip("%")),
                    status_changed_at=dt(day=13),
                    status_changed_by_actor="IMPORTER",
                    status_reason=key,
                    idempotency_key=key,
                    trusted_correction_rule="concurrent-test",
                )
                await session.commit()
                return "created"
            except EvidenceDomainError as exc:
                await session.rollback()
                assert exc.code == "EVIDENCE_VERSION_CONFLICT"
                return "conflict"

    results = await asyncio.gather(
        correct("concurrent-a", "33.0%"), correct("concurrent-b", "34.0%")
    )

    assert sorted(results) == ["conflict", "created"]

    async with pg_sessionmaker() as verify:
        history = await services.list_evidence_history(verify, series_id)
        assert [item.version for item in history] == [1, 2]
