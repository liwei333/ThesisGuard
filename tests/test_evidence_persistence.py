"""WP-04 Evidence persistence and database contract tests."""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from importlib import import_module
from pathlib import Path
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio
from backend.evidence.models import (
    EvidenceCorroborationLink,
    EvidenceDerivationLink,
    EvidenceInstrumentLink,
    EvidenceIdempotencyRecord,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    INITIAL_STATE_CHECK,
    SourceDocument,
    SourceDocumentVersion,
)
from backend.evidence.repositories import (
    get_current_evidence,
    get_exact_evidence_version,
    list_evidence_by_source_document_version,
    list_evidence_history,
)
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

QIANGRUI_INSTRUMENT_ID = "11111111-1111-4111-8111-111111111111"
SHENLING_INSTRUMENT_ID = "22222222-2222-4222-8222-222222222222"
DEFAULT_ADMIN_DATABASE_URL = (
    "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
)
CONTRACT_SOURCE_TYPES = (
    "COMPANY_ANNOUNCEMENT",
    "FINANCIAL_REPORT",
    "EXCHANGE_FILING",
    "REGULATORY_DATA",
    "OFFICIAL_DATA",
    "POLICY_DOCUMENT",
    "INVESTOR_RELATIONS",
    "INSTITUTIONAL_SURVEY",
    "BROKER_RESEARCH",
    "INDUSTRY_REPORT",
    "FINANCIAL_MEDIA",
    "SOCIAL_MEDIA",
    "RUMOR",
    "WEB_PAGE",
    "USER_NOTE",
)
REMOVED_SOURCE_TYPES = (
    "EXCHANGE_" + "ANNOUNCEMENT",
    "COMPANY_" + "REPORT",
    "N" + "EWS",
    "REGULATORY_" + "FILING",
    "MANUAL_" + "NOTE",
    "OT" + "HER",
)


@pytest_asyncio.fixture
async def pg_sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Create a disposable PostgreSQL database and run Alembic migrations."""
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", DEFAULT_ADMIN_DATABASE_URL))
    test_db_name = f"tg_wp04_test_{uuid4().hex}"
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


def source_document(
    doc_id: str = "src-doc-001",
    external_id: str | None = "SZSE-301128-2026H1",
    *,
    source_type: str = "COMPANY_ANNOUNCEMENT",
    canonical_url: str | None = None,
    actor: str = "IMPORTER",
) -> SourceDocument:
    """Build a source identity row with a stable exchange document ID."""
    return SourceDocument(
        id=doc_id,
        publisher_key="szse",
        publisher_name="深圳证券交易所",
        issuer_key="301128.SZ",
        issuer_name="强瑞技术",
        source_type=source_type,
        external_document_id=external_id,
        canonical_url=canonical_url
        if canonical_url is not None
        else (f"https://example.test/{external_id}" if external_id is not None else None),
        title="强瑞技术 2026 半年度报告",
        document_language="zh-CN",
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor=actor,
    )


def source_version(
    version_id: str,
    document_id: str = "src-doc-001",
    *,
    version: int = 1,
    source_grade: str = "A",
    version_fingerprint: str | None = None,
    content_hash: str | None = None,
    source_status: str = "ACTIVE",
    source_status_changed_at: datetime | None = None,
    source_status_actor: str | None = None,
    source_status_reason: str | None = None,
) -> SourceDocumentVersion:
    """Build a source document version snapshot."""
    return SourceDocumentVersion(
        id=version_id,
        source_document_id=document_id,
        version=version,
        version_reason="NEW_CONTENT",
        source_grade=source_grade,
        version_fingerprint=version_fingerprint
        or f"{version_id}-fingerprint".ljust(64, "0")[:64],
        published_at=datetime(2026, 8, 31, tzinfo=UTC),
        observed_at=datetime(2026, 9, 12, tzinfo=UTC),
        fetched_at=datetime(2026, 9, 12, tzinfo=UTC),
        content_hash=content_hash or f"{version_id}-content".ljust(64, "0")[:64],
        source_version_label="2026H1",
        media_type="application/pdf",
        object_key=f"sources/{version_id}.pdf",
        text_object_key=f"sources/{version_id}.txt",
        text_object_hash=f"{version_id}-text".ljust(64, "0")[:64],
        parser_name="tg-pdf",
        parser_version="1.0",
        versioned_metadata={"period": "2026H1"},
        source_status=source_status,
        source_status_changed_at=source_status_changed_at,
        source_status_actor=source_status_actor,
        source_status_reason=source_status_reason,
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
    )


def evidence_series(
    series_id: str,
    *,
    document_id: str = "src-doc-001",
    metric_key: str = "gross_margin",
    identity_hash: str | None = None,
) -> EvidenceSeries:
    """Build a source-backed EvidenceSeries identity."""
    return EvidenceSeries(
        id=series_id,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:{metric_key}:2026H1",
        metric_key=metric_key,
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 6, 30, tzinfo=UTC),
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=document_id,
        origin_key=None,
        series_identity_hash=identity_hash or f"{series_id}-identity".ljust(64, "0")[:64],
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="IMPORTER",
    )


def evidence_version(
    version_id: str,
    *,
    series_id: str,
    source_version_id: str,
    version: int = 1,
    metric_key: str = "gross_margin",
    verification_status: str = "UNREVIEWED",
    status_changed_at: datetime | None = None,
    status_changed_by_actor: str | None = None,
    status_change_kind: str | None = None,
    status_reason: str | None = None,
    supersedes_evidence_version_id: str | None = None,
    trusted_correction_rule: str | None = None,
) -> EvidenceVersion:
    """Build a source-backed EvidenceVersion snapshot."""
    return EvidenceVersion(
        id=version_id,
        evidence_series_id=series_id,
        version=version,
        source_document_version_id=source_version_id,
        information_type="FACT",
        provenance_kind="SOURCE_BACKED",
        source_grade_snapshot="A",
        verification_status=verification_status,
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_change_kind=status_change_kind,
        status_reason=status_reason,
        display_title="强瑞技术 2026H1 毛利率",
        display_text="2026H1 毛利率为 32.5%",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:{metric_key}:2026H1",
        metric_key=metric_key,
        raw_value="32.5%",
        raw_unit="percent",
        normalized_value=Decimal("32.5"),
        normalized_unit="percent",
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 6, 30, tzinfo=UTC),
        as_of=datetime(2026, 8, 31, tzinfo=UTC),
        effective_from=datetime(2026, 8, 31, tzinfo=UTC),
        supersedes_evidence_version_id=supersedes_evidence_version_id,
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="IMPORTER",
        extractor_name="tg-parser",
        extractor_version="1.0",
        trusted_correction_rule=trusted_correction_rule,
    )


async def insert_source_backed_fact(
    db: AsyncSession,
    *,
    document_id: str = "src-doc-001",
    source_version_id: str = "src-ver-001",
    series_id: str = "series-001",
    evidence_version_id: str = "ev-001",
    metric_key: str = "gross_margin",
) -> EvidenceVersion:
    """Insert a minimal source-backed fact with locator and instrument child rows."""
    doc = source_document(document_id, external_id=f"SZSE-{document_id}")
    src_ver = source_version(source_version_id, document_id=document_id)
    series = evidence_series(series_id, document_id=document_id, metric_key=metric_key)
    ev = evidence_version(
        evidence_version_id,
        series_id=series_id,
        source_version_id=source_version_id,
        metric_key=metric_key,
    )
    db.add_all([doc, src_ver, series, ev])
    await db.flush()

    db.add_all(
        [
            EvidenceSourceLocator(
                id=f"locator-{evidence_version_id}",
                evidence_version_id=evidence_version_id,
                source_document_version_id=source_version_id,
                locator_type="PAGE",
                raw_locator="p.12",
                short_citation="2026H1 p.12",
                locator_payload={"page": 12},
                quote_hash=f"{evidence_version_id}-quote".ljust(64, "0")[:64],
                created_at=datetime(2026, 9, 12, tzinfo=UTC),
            ),
            EvidenceInstrumentLink(
                id=f"instrument-{evidence_version_id}",
                evidence_version_id=evidence_version_id,
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
                link_metadata={"scope": "primary"},
                created_at=datetime(2026, 9, 12, tzinfo=UTC),
            ),
        ]
    )
    await db.flush()
    return ev


def add_source_backed_fact_graph(
    db: AsyncSession,
    *,
    document_id: str,
    source_version_id: str,
    series_id: str,
    evidence_version_id: str,
    metric_key: str = "gross_margin",
    verification_status: str = "UNREVIEWED",
    status_changed_at: datetime | None = None,
    status_changed_by_actor: str | None = None,
    status_change_kind: str | None = None,
    status_reason: str | None = None,
    supersedes_evidence_version_id: str | None = None,
) -> EvidenceVersion:
    """Stage a source-backed EvidenceVersion graph without flushing it."""
    doc = source_document(document_id, external_id=f"SZSE-{document_id}")
    src_ver = source_version(source_version_id, document_id=document_id)
    series = evidence_series(series_id, document_id=document_id, metric_key=metric_key)
    ev = evidence_version(
        evidence_version_id,
        series_id=series_id,
        source_version_id=source_version_id,
        metric_key=metric_key,
        verification_status=verification_status,
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_change_kind=status_change_kind,
        status_reason=status_reason,
        supersedes_evidence_version_id=supersedes_evidence_version_id,
    )
    db.add_all([doc, src_ver, series, ev])
    return ev


async def test_repository_contract_surface_uses_plural_module() -> None:
    """WP04-01 exposes persistence queries from backend.evidence.repositories."""
    repositories = import_module("backend.evidence.repositories")

    for helper_name in (
        "get_source_document",
        "get_source_document_by_external_identity",
        "get_source_document_by_canonical_url_identity",
        "get_source_document_version",
        "get_source_document_version_by_fingerprint",
        "get_latest_source_document_version",
        "get_evidence_series_by_identity_hash",
        "get_exact_evidence_version",
        "get_current_evidence",
        "list_evidence_history",
        "list_evidence_by_source_document_version",
    ):
        assert callable(getattr(repositories, helper_name))

    assert not hasattr(repositories, "get_current_valid_evidence")


async def test_source_document_enforces_contract_enums_and_identity(db: AsyncSession) -> None:
    """SourceDocument accepts only frozen SourceType/actor values and requires identity."""
    for index, source_type in enumerate(CONTRACT_SOURCE_TYPES):
        db.add(
            source_document(
                doc_id=f"src-type-{index}",
                external_id=f"contract-{index}",
                source_type=source_type,
            )
        )
    db.add(
        source_document(
            doc_id="src-llm-actor",
            external_id="llm-actor",
            source_type="WEB_PAGE",
            actor="LLM_PROPOSAL",
        )
    )
    db.add(
        source_document(
            doc_id="src-url-only",
            external_id=None,
            source_type="WEB_PAGE",
            canonical_url="https://example.test/url-only",
        )
    )
    db.add(
        source_document(
            doc_id="src-both-identities",
            external_id="external-and-url",
            source_type="WEB_PAGE",
            canonical_url="https://example.test/external-and-url",
        )
    )
    await db.flush()
    await db.rollback()

    for index, source_type in enumerate((*REMOVED_SOURCE_TYPES, "UNKNOWN_SOURCE")):
        db.add(
            source_document(
                doc_id=f"bad-source-type-{index}",
                external_id=f"bad-{source_type}",
                source_type=source_type,
            )
        )
        with pytest.raises(IntegrityError):
            await db.flush()
        await db.rollback()

    db.add(
        source_document(
            doc_id="bad-actor",
            external_id="bad-actor",
            source_type="WEB_PAGE",
            actor="ROBOT",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(
        source_document(
            doc_id="missing-identity",
            external_id=None,
            source_type="WEB_PAGE",
            canonical_url=None,
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_source_document_partial_identity_rules(db: AsyncSession) -> None:
    """External identity wins over URL fallback, and null identity cannot bypass checks."""
    db.add(
        source_document(
            doc_id="external-a",
            external_id="same-external",
            source_type="COMPANY_ANNOUNCEMENT",
            canonical_url="https://example.test/a",
        )
    )
    db.add(
        source_document(
            doc_id="external-b",
            external_id="same-external",
            source_type="COMPANY_ANNOUNCEMENT",
            canonical_url="https://example.test/b",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(
        source_document(
            doc_id="fallback-a",
            external_id=None,
            source_type="WEB_PAGE",
            canonical_url="https://example.test/fallback",
        )
    )
    db.add(
        source_document(
            doc_id="fallback-b",
            external_id=None,
            source_type="WEB_PAGE",
            canonical_url="https://example.test/fallback",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(
        source_document(
            doc_id="external-url-a",
            external_id="external-a",
            source_type="WEB_PAGE",
            canonical_url="https://example.test/shared-url",
        )
    )
    db.add(
        source_document(
            doc_id="external-url-b",
            external_id="external-b",
            source_type="WEB_PAGE",
            canonical_url="https://example.test/shared-url",
        )
    )
    await db.flush()


async def test_source_document_version_grade_identity_lifecycle_and_repository(
    db: AsyncSession,
) -> None:
    """SourceDocumentVersion identity is fingerprint-based and lifecycle-audited."""
    repositories = import_module("backend.evidence.repositories")
    db.add(source_document("src-doc-grade", external_id="grade-doc"))
    db.add(
        source_version(
            "src-ver-grade-e",
            document_id="src-doc-grade",
            source_grade="E",
            version_fingerprint="grade-e-fingerprint".ljust(64, "0")[:64],
        )
    )
    db.add(
        source_version(
            "src-ver-grade-a",
            document_id="src-doc-grade",
            version=2,
            source_grade="A",
            version_fingerprint="grade-a-fingerprint".ljust(64, "0")[:64],
            content_hash="grade-e-content".ljust(64, "0")[:64],
        )
    )
    await db.flush()

    by_fingerprint = await repositories.get_source_document_version_by_fingerprint(
        db,
        "src-doc-grade",
        "grade-e-fingerprint".ljust(64, "0")[:64],
    )
    latest = await repositories.get_latest_source_document_version(db, "src-doc-grade")
    assert by_fingerprint is not None
    assert by_fingerprint.id == "src-ver-grade-e"
    assert latest is not None
    assert latest.id == "src-ver-grade-a"
    await db.rollback()

    db.add(source_document("src-doc-bad-grade", external_id="bad-grade-doc"))
    db.add(source_version("src-ver-bad-grade", "src-doc-bad-grade", source_grade="Z"))
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(source_document("src-doc-duplicate", external_id="duplicate-version-doc"))
    db.add(source_version("src-ver-1", "src-doc-duplicate"))
    db.add(
        source_version(
            "src-ver-2",
            "src-doc-duplicate",
            version=1,
            version_fingerprint="different-fingerprint".ljust(64, "0")[:64],
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(source_document("src-doc-duplicate-fp", external_id="duplicate-fp-doc"))
    db.add(source_version("src-ver-1", "src-doc-duplicate-fp"))
    db.add(
        source_version(
            "src-ver-2",
            "src-doc-duplicate-fp",
            version=2,
            version_fingerprint="src-ver-1-fingerprint".ljust(64, "0")[:64],
            content_hash="different-content".ljust(64, "0")[:64],
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(source_document("src-doc-active-audit", external_id="active-audit-doc"))
    db.add(
        source_version(
            "src-ver-active-audit",
            "src-doc-active-audit",
            source_status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            source_status_actor="IMPORTER",
            source_status_reason="active rows cannot carry lifecycle audit tuple",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    db.add(source_document("src-doc-retracted", external_id="retracted-doc"))
    db.add(
        source_version(
            "src-ver-retracted",
            "src-doc-retracted",
            source_status="RETRACTED",
            source_status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            source_status_actor="IMPORTER",
            source_status_reason="issuer retracted source",
        )
    )
    db.add(source_document("src-doc-superseeded", external_id="superseeded-doc"))
    db.add(
        source_version(
            "src-ver-superseeded",
            "src-doc-superseeded",
            source_status="SUPERSEDED",
            source_status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            source_status_actor="ADMIN_SCRIPT",
            source_status_reason="source superseded",
        )
    )
    await db.flush()


async def test_source_and_series_identity_repository_helpers(db: AsyncSession) -> None:
    """Repository helpers resolve exact source and Evidence identity keys."""
    repositories = import_module("backend.evidence.repositories")
    external_doc = source_document(
        "src-doc-external",
        external_id="external-lookup",
        source_type="COMPANY_ANNOUNCEMENT",
        canonical_url="https://example.test/external-lookup",
    )
    url_doc = source_document(
        "src-doc-url",
        external_id=None,
        source_type="WEB_PAGE",
        canonical_url="https://example.test/url-lookup",
    )
    db.add_all([external_doc, url_doc])
    db.add(source_version("src-ver-external", "src-doc-external"))
    series_hash = "series-identity-lookup".ljust(64, "0")[:64]
    db.add(
        evidence_series(
            "series-lookup",
            document_id="src-doc-external",
            identity_hash=series_hash,
        )
    )
    await db.flush()

    by_id = await repositories.get_source_document(db, "src-doc-external")
    by_external = await repositories.get_source_document_by_external_identity(
        db,
        "szse",
        "COMPANY_ANNOUNCEMENT",
        "external-lookup",
    )
    by_url = await repositories.get_source_document_by_canonical_url_identity(
        db,
        "szse",
        "WEB_PAGE",
        "https://example.test/url-lookup",
    )
    external_by_url = await repositories.get_source_document_by_canonical_url_identity(
        db,
        "szse",
        "COMPANY_ANNOUNCEMENT",
        "https://example.test/external-lookup",
    )
    series = await repositories.get_evidence_series_by_identity_hash(db, series_hash)

    assert by_id is not None and by_id.id == "src-doc-external"
    assert by_external is not None and by_external.id == "src-doc-external"
    assert by_url is not None and by_url.id == "src-doc-url"
    assert external_by_url is None
    assert series is not None and series.id == "series-lookup"


async def test_evidence_series_version_lifecycle_and_current_queries(db: AsyncSession) -> None:
    """EvidenceVersion lifecycle constraints preserve append-only current/history semantics."""
    await insert_source_backed_fact(db)
    db.add(
        evidence_version(
            "ev-002",
            series_id="series-001",
            source_version_id="src-ver-001",
            version=2,
            verification_status="VERIFIED",
            status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            status_changed_by_actor="USER",
            status_change_kind="REVIEW_DECISION",
            status_reason="reviewed against source locator",
        )
    )
    await db.flush()
    exact_v1 = await get_exact_evidence_version(db, "ev-001")
    current = await get_current_evidence(db, "series-001")
    history = await list_evidence_history(db, "series-001")
    assert exact_v1 is not None and exact_v1.version == 1
    assert current is not None and current.id == "ev-002"
    assert [item.id for item in history] == ["ev-001", "ev-002"]
    await db.rollback()

    await insert_source_backed_fact(db)
    db.add(
        evidence_version(
            "ev-002",
            series_id="series-001",
            source_version_id="src-ver-001",
            version=2,
            verification_status="VERIFIED",
            status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            status_change_kind="REVIEW_DECISION",
            status_reason="partial audit tuple",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    replacement_series = evidence_series(
        "series-002",
        metric_key="net_margin",
        identity_hash="series-002-identity".ljust(64, "0")[:64],
    )
    wrong_kind_replacement = evidence_version(
        "ev-002",
        series_id="series-002",
        source_version_id="src-ver-001",
        metric_key="net_margin",
        supersedes_evidence_version_id="ev-001",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="USER",
        status_change_kind="REVIEW_DECISION",
        status_reason="replacement must be correction lineage",
    )
    db.add_all([replacement_series, wrong_kind_replacement])
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    correction_without_predecessor = evidence_version(
        "ev-correction-without-predecessor",
        series_id="series-001",
        source_version_id="src-ver-001",
        version=2,
        verification_status="UNREVIEWED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="USER",
        status_change_kind="CORRECTION",
        status_reason="correction must point to exact predecessor",
    )
    db.add(correction_without_predecessor)
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    trusted_missing_rule = evidence_version(
        "ev-trusted-missing-rule",
        series_id="series-001",
        source_version_id="src-ver-001",
        version=2,
        verification_status="VERIFIED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="SYSTEM",
        status_change_kind="CORRECTION",
        status_reason="trusted correction needs named rule",
        supersedes_evidence_version_id="ev-001",
    )
    db.add(trusted_missing_rule)
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_initial_v1_without_predecessor_has_only_two_legal_forms(
    db: AsyncSession,
) -> None:
    """Brand-new v1 can only be UNREVIEWED/null-audit or VERIFIED/INITIAL_VERIFICATION."""
    add_source_backed_fact_graph(
        db,
        document_id="src-doc-initial-unreviewed",
        source_version_id="src-ver-initial-unreviewed",
        series_id="series-initial-unreviewed",
        evidence_version_id="ev-initial-unreviewed",
    )
    await db.flush()
    await db.rollback()

    add_source_backed_fact_graph(
        db,
        document_id="src-doc-initial-verified",
        source_version_id="src-ver-initial-verified",
        series_id="series-initial-verified",
        evidence_version_id="ev-initial-verified",
        verification_status="VERIFIED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="SYSTEM",
        status_change_kind="INITIAL_VERIFICATION",
        status_reason="Trusted deterministic import verified at creation.",
    )
    await db.flush()
    await db.rollback()

    illegal_initial_states = (
        ("PENDING_REVIEW", "REVIEW_REQUEST"),
        ("REJECTED", "REVIEW_DECISION"),
        ("DISPUTED", "DISPUTE"),
        ("INVALIDATED", "INVALIDATION"),
        ("RETRACTED", "RETRACTION"),
        ("VERIFIED", "REVIEW_DECISION"),
        ("VERIFIED", "DISPUTE"),
    )
    accepted_illegal_initial_states: list[tuple[str, str]] = []
    for index, (verification_status, status_change_kind) in enumerate(illegal_initial_states):
        add_source_backed_fact_graph(
            db,
            document_id=f"src-doc-illegal-initial-{index}",
            source_version_id=f"src-ver-illegal-initial-{index}",
            series_id=f"series-illegal-initial-{index}",
            evidence_version_id=f"ev-illegal-initial-{index}",
            verification_status=verification_status,
            status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            status_changed_by_actor="USER",
            status_change_kind=status_change_kind,
            status_reason="A no-predecessor v1 cannot represent a post-creation transition.",
        )
        try:
            await db.flush()
        except IntegrityError:
            pass
        else:
            accepted_illegal_initial_states.append((verification_status, status_change_kind))
        await db.rollback()
    assert accepted_illegal_initial_states == []

    add_source_backed_fact_graph(
        db,
        document_id="src-doc-initial-verified-null-audit",
        source_version_id="src-ver-initial-verified-null-audit",
        series_id="series-initial-verified-null-audit",
        evidence_version_id="ev-initial-verified-null-audit",
        verification_status="VERIFIED",
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    add_source_backed_fact_graph(
        db,
        document_id="src-doc-iv-partial-audit",
        source_version_id="src-ver-iv-partial-audit",
        series_id="series-iv-partial-audit",
        evidence_version_id="ev-iv-partial-audit",
        verification_status="VERIFIED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="SYSTEM",
        status_change_kind="INITIAL_VERIFICATION",
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_evidence_provenance_combinations(db: AsyncSession) -> None:
    """Source-backed, manual, and derived provenance combinations are database-backed."""
    db.add(source_document("src-doc-provenance", external_id="provenance-doc"))
    db.add(source_version("src-ver-provenance", "src-doc-provenance"))
    db.add(
        evidence_series(
            "series-source-backed",
            document_id="src-doc-provenance",
            identity_hash="series-source-backed".ljust(64, "0")[:64],
        )
    )
    db.add(
        evidence_version(
            "ev-source-missing-version",
            series_id="series-source-backed",
            source_version_id="src-ver-provenance",
        )
    )
    await db.flush()
    await db.rollback()

    manual_series = EvidenceSeries(
        id="series-manual-estimate",
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="ESTIMATE",
        claim_key="manual-estimate",
        provenance_kind="MANUAL",
        origin_key="manual:USER:estimate",
        series_identity_hash="series-manual-estimate".ljust(64, "0")[:64],
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="USER",
    )
    manual_ev = EvidenceVersion(
        id="ev-manual-estimate",
        evidence_series_id="series-manual-estimate",
        version=1,
        information_type="ESTIMATE",
        provenance_kind="MANUAL",
        verification_status="UNREVIEWED",
        display_title="Manual estimate",
        display_text="Manual estimate with reason.",
        claim_key="manual-estimate",
        as_of=datetime(2026, 9, 12, tzinfo=UTC),
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="USER",
        manual_entry_reason="manual estimate",
        manual_observed_at=datetime(2026, 9, 12, tzinfo=UTC),
    )
    db.add_all([manual_series, manual_ev])
    await db.flush()
    await db.rollback()

    db.add(
        EvidenceSeries(
            id="series-derived-with-source",
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key="derived-invalid",
            provenance_kind="DERIVED",
            origin_key="derived:support",
            series_identity_hash="series-derived-with-source".ljust(64, "0")[:64],
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
            created_by_actor="SYSTEM",
        )
    )
    db.add(
        EvidenceVersion(
            id="ev-derived-with-source",
            evidence_series_id="series-derived-with-source",
            version=1,
            source_document_version_id="src-ver-provenance",
            information_type="THESIS_INFERENCE",
            provenance_kind="DERIVED",
            source_grade_snapshot="A",
            verification_status="UNREVIEWED",
            display_title="Derived invalid",
            display_text="Derived evidence cannot carry source version fields.",
            claim_key="derived-invalid",
            as_of=datetime(2026, 9, 12, tzinfo=UTC),
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
            created_by_actor="SYSTEM",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_child_link_uniqueness_and_snapshot_loading(db: AsyncSession) -> None:
    """Child links are immutable exact-version rows and load with exact Evidence queries."""
    await insert_source_backed_fact(db)
    await insert_source_backed_fact(
        db,
        document_id="src-doc-002",
        source_version_id="src-ver-002",
        series_id="series-002",
        evidence_version_id="ev-002",
        metric_key="net_margin",
    )
    db.add(
        EvidenceInstrumentLink(
            id="instrument-duplicate",
            evidence_version_id="ev-001",
            instrument_id=QIANGRUI_INSTRUMENT_ID,
            role="PRIMARY_SCOPE",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    await insert_source_backed_fact(
        db,
        document_id="src-doc-002",
        source_version_id="src-ver-002",
        series_id="series-002",
        evidence_version_id="ev-002",
        metric_key="net_margin",
    )
    db.add(
        EvidenceCorroborationLink(
            id="corroboration-valid",
            left_evidence_version_id="ev-001",
            right_evidence_version_id="ev-002",
            relation_type="CORROBORATES",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
            created_by_actor="USER",
        )
    )
    db.add(
        EvidenceDerivationLink(
            id="derivation-valid",
            derived_evidence_version_id="ev-002",
            supporting_evidence_version_id="ev-001",
            role="INPUT_FACT",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    await db.flush()

    exact = await get_exact_evidence_version(db, "ev-001")
    assert exact is not None
    assert [link.id for link in exact.left_corroboration_links] == ["corroboration-valid"]
    assert [link.id for link in exact.supporting_derivation_links] == ["derivation-valid"]
    await db.rollback()

    await insert_source_backed_fact(db)
    await insert_source_backed_fact(
        db,
        document_id="src-doc-002",
        source_version_id="src-ver-002",
        series_id="series-002",
        evidence_version_id="ev-002",
        metric_key="net_margin",
    )
    db.add(
        EvidenceCorroborationLink(
            id="corroboration-reverse",
            left_evidence_version_id="ev-002",
            right_evidence_version_id="ev-001",
            relation_type="CORROBORATES",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
            created_by_actor="USER",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    db.add(
        EvidenceDerivationLink(
            id="derivation-duplicate-a",
            derived_evidence_version_id="ev-001",
            supporting_evidence_version_id="ev-001",
            role="SUPPORTS_INFERENCE",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    await insert_source_backed_fact(
        db,
        document_id="src-doc-002",
        source_version_id="src-ver-002",
        series_id="series-002",
        evidence_version_id="ev-002",
        metric_key="net_margin",
    )
    db.add_all(
        [
            EvidenceDerivationLink(
                id="derivation-duplicate-a",
                derived_evidence_version_id="ev-002",
                supporting_evidence_version_id="ev-001",
                role="INPUT_FACT",
                created_at=datetime(2026, 9, 12, tzinfo=UTC),
            ),
            EvidenceDerivationLink(
                id="derivation-duplicate-b",
                derived_evidence_version_id="ev-002",
                supporting_evidence_version_id="ev-001",
                role="INPUT_FACT",
                created_at=datetime(2026, 9, 12, tzinfo=UTC),
            ),
        ]
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_evidence_idempotency_record_composite_identity(db: AsyncSession) -> None:
    """Idempotency records are keyed by operation scope plus idempotency key."""
    db.add(
        EvidenceIdempotencyRecord(
            scope="source_document:external-1",
            idempotency_key="idem-key",
            request_hash="hash-a",
            status="COMMITTED",
            response_ref_type="SourceDocumentVersion",
            response_ref_id="src-ver-001",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    db.add(
        EvidenceIdempotencyRecord(
            scope="evidence_series:series-1",
            idempotency_key="idem-key",
            request_hash="hash-b",
            status="COMMITTED",
            response_ref_type="EvidenceVersion",
            response_ref_id="ev-001",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    await db.flush()

    db.add(
        EvidenceIdempotencyRecord(
            scope="source_document:external-1",
            idempotency_key="idem-key",
            request_hash="hash-conflict",
            status="COMMITTED",
            response_ref_type="SourceDocumentVersion",
            response_ref_id="src-ver-002",
            created_at=datetime(2026, 9, 12, tzinfo=UTC),
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_evidence_migration_creates_contract_tables_and_constraints(
    pg_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """Alembic head contains the WP-04 Evidence persistence foundation."""
    async with pg_sessionmaker() as session:
        rows = await session.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                """
            )
        )
        tables = set(rows.scalars())

        assert {
            "source_document",
            "source_document_version",
            "evidence_series",
            "evidence_version",
            "evidence_source_locator",
            "evidence_instrument_link",
            "evidence_corroboration_link",
            "evidence_derivation_link",
            "evidence_idempotency_record",
            "evidence_audit_event",
        }.issubset(tables)

        constraints = await session.execute(
            text(
                """
                SELECT conname, pg_get_constraintdef(oid) AS definition
                FROM pg_constraint
                WHERE conrelid IN (
                    'source_document_version'::regclass,
                    'evidence_series'::regclass,
                    'evidence_version'::regclass,
                    'evidence_corroboration_link'::regclass,
                    'evidence_derivation_link'::regclass
                )
                """
            )
        )
        constraint_definitions = {
            row.conname: row.definition for row in constraints
        }
        constraint_names = set(constraint_definitions)
        migration_text = Path(
            "migrations/versions/20260914_004_evidence_persistence.py"
        ).read_text()
        model_initial_constraint = next(
            constraint
            for constraint in EvidenceVersion.__table__.constraints
            if constraint.name == "ck_evidence_version_initial_state"
        )

        assert "ck_evidence_version_status_audit_null_only_initial" in constraint_names
        assert "ck_evidence_version_initial_state" in constraint_names
        assert str(model_initial_constraint.sqltext) == INITIAL_STATE_CHECK
        assert "INITIAL_STATE_CHECK = (" in migration_text
        assert "ck_evidence_version_initial_state" in migration_text
        assert "status_change_kind = 'INITIAL_VERIFICATION'" in migration_text
        assert "INITIAL_VERIFICATION" in constraint_definitions[
            "ck_evidence_version_initial_state"
        ]
        assert "UNREVIEWED" in constraint_definitions["ck_evidence_version_initial_state"]
        assert "ck_evidence_version_supersedes_requires_audit" in constraint_names
        assert "ck_evidence_version_replacement_v1_kind" in constraint_names
        assert "ck_evidence_version_correction_requires_predecessor" in constraint_names
        assert "ck_evidence_version_tombstone_requires_predecessor" in constraint_names
        assert "ck_evidence_version_source_provenance" in constraint_names
        assert "ck_source_document_version_source_status_metadata" in constraint_names
        assert "ck_evidence_corroboration_link_ordering" in constraint_names
        assert "ck_evidence_derivation_link_no_self_link" in constraint_names


async def test_source_backed_fact_persists_and_repository_reads_current_history_and_source(
    db: AsyncSession,
) -> None:
    """Repository helpers read exact immutable versions and current series state."""
    inserted = await insert_source_backed_fact(db)
    await db.commit()

    current = await get_current_evidence(db, "series-001")
    exact = await get_exact_evidence_version(db, "ev-001")
    history = await list_evidence_history(db, "series-001")
    by_source = await list_evidence_by_source_document_version(db, "src-ver-001")

    assert current is not None
    assert current.id == inserted.id
    assert exact is not None
    assert exact.id == inserted.id
    assert len(exact.source_locators) == 1
    assert exact.source_locators[0].raw_locator == "p.12"
    assert len(exact.instrument_links) == 1
    assert exact.instrument_links[0].instrument_id == QIANGRUI_INSTRUMENT_ID
    assert [item.version for item in history] == [1]
    assert [item.id for item in by_source] == ["ev-001"]


async def test_replacement_v1_cannot_use_initial_null_audit_escape_hatch(
    db: AsyncSession,
) -> None:
    """Identity-changing replacement v1 always needs predecessor FK and full audit tuple."""
    await insert_source_backed_fact(db)
    replacement_series = evidence_series(
        "series-002",
        metric_key="net_margin",
        identity_hash="series-002-identity".ljust(64, "0")[:64],
    )
    invalid_replacement = evidence_version(
        "ev-002",
        series_id="series-002",
        source_version_id="src-ver-001",
        metric_key="net_margin",
        supersedes_evidence_version_id="ev-001",
    )
    db.add_all([replacement_series, invalid_replacement])

    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    audited_replacement_series = evidence_series(
        "series-002",
        metric_key="net_margin",
        identity_hash="series-002-identity".ljust(64, "0")[:64],
    )
    audited_replacement = evidence_version(
        "ev-002",
        series_id="series-002",
        source_version_id="src-ver-001",
        metric_key="net_margin",
        supersedes_evidence_version_id="ev-001",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="USER",
        status_change_kind="CORRECTION",
        status_reason="Metric was reclassified from gross_margin to net_margin.",
    )
    db.add_all([audited_replacement_series, audited_replacement])
    await db.flush()

    assert audited_replacement.version == 1
    assert audited_replacement.verification_status == "UNREVIEWED"
    assert audited_replacement.supersedes_evidence_version_id == "ev-001"


async def test_tombstone_requires_exact_predecessor_and_complete_snapshot(
    db: AsyncSession,
) -> None:
    """Invalidated/retracted rows are complete N+1 snapshots, not metadata flags."""
    await insert_source_backed_fact(db)

    invalid_tombstone = evidence_version(
        "ev-002",
        series_id="series-001",
        source_version_id="src-ver-001",
        version=2,
        verification_status="RETRACTED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="IMPORTER",
        status_change_kind="RETRACTION",
        status_reason="Issuer published a retraction notice.",
    )
    db.add(invalid_tombstone)

    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    tombstone = evidence_version(
        "ev-002",
        series_id="series-001",
        source_version_id="src-ver-001",
        version=2,
        verification_status="RETRACTED",
        status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
        status_changed_by_actor="IMPORTER",
        status_change_kind="RETRACTION",
        status_reason="Issuer published a retraction notice.",
        supersedes_evidence_version_id="ev-001",
    )
    db.add(tombstone)
    await db.flush()

    current = await get_current_evidence(db, "series-001")
    assert current is not None
    assert current.id == "ev-002"
    assert current.verification_status == "RETRACTED"
    assert current.supersedes_evidence_version_id == "ev-001"


async def test_invalidated_tombstone_is_current_and_requires_complete_audit(
    db: AsyncSession,
) -> None:
    """INVALIDATED tombstone is a complete N+1 snapshot and remains current."""
    await insert_source_backed_fact(db)
    db.add(
        evidence_version(
            "ev-002",
            series_id="series-001",
            source_version_id="src-ver-001",
            version=2,
            verification_status="VERIFIED",
            status_changed_at=datetime(2026, 9, 13, tzinfo=UTC),
            status_changed_by_actor="USER",
            status_change_kind="REVIEW_DECISION",
            status_reason="Reviewed against the source.",
        )
    )
    await db.flush()
    invalidated = evidence_version(
        "ev-003",
        series_id="series-001",
        source_version_id="src-ver-001",
        version=3,
        verification_status="INVALIDATED",
        status_changed_at=datetime(2026, 9, 14, tzinfo=UTC),
        status_changed_by_actor="USER",
        status_change_kind="INVALIDATION",
        status_reason="Later evidence disproved the old metric.",
        supersedes_evidence_version_id="ev-002",
    )
    db.add(invalidated)
    await db.flush()

    current = await get_current_evidence(db, "series-001")
    assert current is not None
    assert current.id == "ev-003"
    assert current.verification_status == "INVALIDATED"
    assert current.supersedes_evidence_version_id == "ev-002"
    await db.rollback()

    await insert_source_backed_fact(db)
    db.add(
        evidence_version(
            "ev-002",
            series_id="series-001",
            source_version_id="src-ver-001",
            version=2,
            verification_status="INVALIDATED",
            status_changed_at=datetime(2026, 9, 14, tzinfo=UTC),
            status_changed_by_actor="USER",
            status_change_kind="INVALIDATION",
            status_reason="Missing predecessor must be rejected.",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    db.add(
        evidence_version(
            "ev-002",
            series_id="series-001",
            source_version_id="src-ver-001",
            version=2,
            verification_status="INVALIDATED",
            status_changed_at=datetime(2026, 9, 14, tzinfo=UTC),
            status_change_kind="INVALIDATION",
            status_reason="Partial audit tuple must be rejected.",
            supersedes_evidence_version_id="ev-001",
        )
    )
    with pytest.raises(IntegrityError):
        await db.flush()


async def test_database_rejects_invalid_provenance_and_child_links(db: AsyncSession) -> None:
    """PostgreSQL constraints backstop provenance, locator, and relationship identity."""
    await insert_source_backed_fact(db)

    manual_fact = EvidenceVersion(
        id="ev-manual-fact",
        evidence_series_id="series-001",
        version=2,
        source_document_version_id=None,
        information_type="FACT",
        provenance_kind="MANUAL",
        source_grade_snapshot=None,
        verification_status="UNREVIEWED",
        display_title="Manual fact",
        display_text="Manual fact should not be accepted.",
        claim_key="manual-fact",
        as_of=datetime(2026, 9, 12, tzinfo=UTC),
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="USER",
        manual_entry_reason="manual entry",
        manual_observed_at=datetime(2026, 9, 12, tzinfo=UTC),
    )
    db.add(manual_fact)

    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    duplicate_locator = EvidenceSourceLocator(
        id="locator-duplicate",
        evidence_version_id="ev-001",
        source_document_version_id="src-ver-001",
        locator_type="PAGE",
        raw_locator="p.12",
        short_citation="2026H1 p.12",
        locator_payload={"page": 12},
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
    )
    db.add(duplicate_locator)

    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    self_corroboration = EvidenceCorroborationLink(
        id="corroboration-self",
        left_evidence_version_id="ev-001",
        right_evidence_version_id="ev-001",
        relation_type="CORROBORATES",
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        created_by_actor="USER",
    )
    db.add(self_corroboration)

    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()

    await insert_source_backed_fact(db)
    self_derivation = EvidenceDerivationLink(
        id="derivation-self",
        derived_evidence_version_id="ev-001",
        supporting_evidence_version_id="ev-001",
        role="SUPPORTS_INFERENCE",
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
    )
    db.add(self_derivation)

    with pytest.raises(IntegrityError):
        await db.flush()


async def test_evidence_models_are_registered_for_metadata_create_all() -> None:
    """The central models registry imports WP-04 tables into Base.metadata."""
    from backend.common.db import models_registry  # noqa: F401
    from backend.common.db.session import Base

    assert {
        "source_document",
        "source_document_version",
        "evidence_series",
        "evidence_version",
        "evidence_source_locator",
        "evidence_instrument_link",
        "evidence_corroboration_link",
        "evidence_derivation_link",
        "evidence_idempotency_record",
        "evidence_audit_event",
    }.issubset(Base.metadata.tables)

    assert EvidenceVersion.__tablename__ == "evidence_version"
