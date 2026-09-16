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
from typing import Any
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio
from backend.evidence import services
from backend.evidence.errors import EvidenceDomainError, EvidenceValidationError
from backend.evidence.models import (
    EvidenceAuditEvent,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceInstrumentLink,
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


async def verified_evidence_fact(
    db: AsyncSession,
    *,
    key_suffix: str,
    source_status: str = "ACTIVE",
) -> EvidenceVersion:
    """Create a source-backed FACT whose latest version is eligible VERIFIED."""
    source, source_version = await source_with_version(db, key_suffix=f"{key_suffix}-source")
    if source_status == "RETRACTED":
        source_version = await append_source_version(
            db,
            source,
            key_suffix=f"{key_suffix}-source-retracted",
            expected_version=1,
            version_reason="RETRACTION_NOTICE",
            source_grade="S",
            content_hash=f"{key_suffix}-source-content".ljust(64, "0")[:64],
            object_key=f"sources/{key_suffix}-source.pdf",
            text_object_hash=f"{key_suffix}-source-text".ljust(64, "0")[:64],
            source_status="RETRACTED",
            source_status_changed_at=dt(day=13),
            source_status_actor="IMPORTER",
            source_status_reason="issuer retracted document",
            idempotency_key=f"source-version-{key_suffix}-retracted",
        )
    return await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:verified:{key_suffix}",
        metric_key=f"verified_{key_suffix}",
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 6, 30, tzinfo=UTC),
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title=f"Verified fact {key_suffix}",
        display_text=f"Verified fact {key_suffix}",
        raw_value="32.5%",
        raw_unit="percent",
        normalized_value=Decimal("32.5"),
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
        verification_status="VERIFIED",
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_change_kind="INITIAL_VERIFICATION",
        status_reason="deterministic import accepted",
        created_by_actor="IMPORTER",
        idempotency_key=f"evidence-verified-{key_suffix}",
        created_at=dt(day=13),
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
        ("instrument_link", EvidenceInstrumentLink),
        ("derivation_link", EvidenceDerivationLink),
        ("idempotency", EvidenceIdempotencyRecord),
        ("audit", EvidenceAuditEvent),
    ):
        counts[key] = int(await db.scalar(select(func.count()).select_from(model)) or 0)
    return counts


def expected_manual_origin(actor: str, claim_key: str) -> str:
    return f"manual:{actor}:{claim_key.strip()}"


def expected_derived_origin(*support_ids: str) -> str:
    support_set = sorted(set(support_ids))
    return f"derived:{services.stable_hash(support_set)}"


def expected_cross_scope(*instrument_ids: str) -> str:
    member_set = sorted(set(instrument_ids))
    return f"cross_instrument:{services.stable_hash(member_set)}"


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
    assert valid is None
    assert [item.id for item in by_source] == [created.id]
    assert [item.id for item in by_instrument] == [created.id]

    audit_count = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))
    assert audit_count and audit_count >= 3


async def test_r1c_current_valid_accepts_latest_verified_and_missing_series_is_none(
    db: AsyncSession,
) -> None:
    """R1C: current-valid returns only latest VERIFIED rows and misses safely."""
    verified = await verified_evidence_fact(db, key_suffix="r1c-valid")
    await db.commit()

    valid = await services.get_current_valid_evidence(db, verified.evidence_series_id)
    missing = await services.get_current_valid_evidence(db, str(uuid4()))

    assert valid is not None and valid.id == verified.id
    assert missing is None


@pytest.mark.parametrize(
    ("status", "expected_version"),
    [
        ("UNREVIEWED", 2),
        ("PENDING_REVIEW", 2),
        ("DISPUTED", 2),
        ("REJECTED", 3),
        ("INVALIDATED", 2),
        ("RETRACTED", 2),
    ],
)
async def test_r1c_current_valid_rejects_latest_ineligible_status_without_fallback(
    db: AsyncSession,
    status: str,
    expected_version: int,
) -> None:
    """R1C: latest ineligible lifecycle statuses do not fall back to prior VERIFIED."""
    if status in {"PENDING_REVIEW", "REJECTED"}:
        base = await evidence_fact(db, key_suffix=f"r1c-{status.lower()}")
        await db.commit()
        latest = await services.request_review(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            reason="review requested",
            actor="USER",
            idempotency_key=f"r1c-{status.lower()}-review",
            as_of=dt(day=14),
        )
        if status == "REJECTED":
            latest = await services.verify_or_reject(
                db,
                evidence_series_id=base.evidence_series_id,
                expected_version=2,
                decision="REJECTED",
                reason="review rejected",
                actor="USER",
                idempotency_key=f"r1c-{status.lower()}-reject",
                as_of=dt(day=15),
            )
    else:
        base = await verified_evidence_fact(db, key_suffix=f"r1c-{status.lower()}")
        await db.commit()
        if status == "UNREVIEWED":
            latest = await services.revise_correct_evidence(
                db,
                evidence_series_id=base.evidence_series_id,
                expected_version=1,
                display_text="Verified fact corrected and awaiting review",
                raw_value="33.0%",
                normalized_value=Decimal("33.0"),
                status_changed_at=dt(day=14),
                status_changed_by_actor="IMPORTER",
                status_reason="ordinary correction awaits review",
                idempotency_key=f"r1c-{status.lower()}-correction",
            )
        elif status == "DISPUTED":
            latest = await services.mark_disputed(
                db,
                evidence_series_id=base.evidence_series_id,
                expected_version=1,
                reason="issuer later challenged",
                actor="USER",
                idempotency_key=f"r1c-{status.lower()}-dispute",
                as_of=dt(day=14),
            )
        else:
            latest = await services.retract_or_invalidate(
                db,
                evidence_series_id=base.evidence_series_id,
                expected_version=1,
                target_status=status,
                reason=f"{status.lower()} latest",
                actor="IMPORTER",
                idempotency_key=f"r1c-{status.lower()}-tombstone",
                as_of=dt(day=14),
            )
    await db.commit()

    current = await services.get_current_evidence(db, latest.evidence_series_id)
    valid = await services.get_current_valid_evidence(db, latest.evidence_series_id)
    exact_base = await services.get_exact_evidence_version(db, base.id)
    history = await services.list_evidence_history(db, latest.evidence_series_id)

    assert latest.verification_status == status
    assert latest.version == expected_version
    assert current is not None and current.id == latest.id
    assert valid is None
    assert exact_base is not None and exact_base.id == base.id
    assert history[0].id == base.id
    assert history[-1].id == latest.id


async def test_r1c_current_valid_rejects_unreviewed_replacement_series(
    db: AsyncSession,
) -> None:
    """R1C: ordinary replacement v1 starts ineligible even when prior exact was VERIFIED."""
    prior = await verified_evidence_fact(db, key_suffix="r1c-replacement-prior")
    assert prior.source_document_version is not None
    await db.commit()

    replacement = await services.create_replacement_evidence_series(
        db,
        prior_evidence_version_id=prior.id,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="FACT",
        claim_key=f"{QIANGRUI_INSTRUMENT_ID}:r1c_replacement_metric",
        metric_key="r1c_replacement_metric",
        period_start=prior.period_start,
        period_end=prior.period_end,
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=prior.source_document_version.source_document_id,
        source_document_version_id=prior.source_document_version_id,
        display_title="R1C replacement",
        display_text="R1C replacement awaits review",
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
        status_changed_at=dt(day=14),
        status_changed_by_actor="IMPORTER",
        status_reason="identity correction awaits review",
        idempotency_key="r1c-replacement",
    )
    await db.commit()

    replacement_valid = await services.get_current_valid_evidence(
        db,
        replacement.evidence_series_id,
    )
    prior_valid = await services.get_current_valid_evidence(db, prior.evidence_series_id)
    prior_exact = await services.get_exact_evidence_version(db, prior.id)
    replacement_history = await services.list_evidence_history(db, replacement.evidence_series_id)

    assert replacement.verification_status == "UNREVIEWED"
    assert replacement.supersedes_evidence_version_id == prior.id
    assert replacement_valid is None
    assert prior_valid is not None and prior_valid.id == prior.id
    assert prior_exact is not None and prior_exact.id == prior.id
    assert [item.id for item in replacement_history] == [replacement.id]


async def test_r1c_current_valid_rejects_latest_verified_with_retracted_exact_source(
    db: AsyncSession,
) -> None:
    """R1C: latest VERIFIED remains ineligible when its exact source version is retracted."""
    verified = await verified_evidence_fact(
        db,
        key_suffix="r1c-retracted-source",
        source_status="RETRACTED",
    )
    await db.commit()

    current = await services.get_current_evidence(db, verified.evidence_series_id)
    valid = await services.get_current_valid_evidence(db, verified.evidence_series_id)
    exact = await services.get_exact_evidence_version(db, verified.id)

    assert current is not None and current.id == verified.id
    assert exact is not None and exact.id == verified.id
    assert exact.source_document_version is not None
    assert exact.source_document_version.source_status == "RETRACTED"
    assert valid is None


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


async def test_r1b_manual_identity_and_source_less_validation(db: AsyncSession) -> None:
    """Manual identities are service-derived and source-less provenance is fail-closed."""
    estimate = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="ESTIMATE",
        claim_key=" margin-estimate ",
        provenance_kind="MANUAL",
        display_title="User margin estimate",
        display_text="User estimates margin at 34%",
        raw_value="34%",
        raw_unit="percent",
        normalized_value=Decimal("34"),
        normalized_unit="percent",
        as_of=dt(),
        manual_entry_reason="user observed management guidance",
        manual_observed_at=dt(),
        created_by_actor="USER",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-manual-estimate",
    )
    hypothesis = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="USER_HYPOTHESIS",
        claim_key="margin-estimate",
        provenance_kind="MANUAL",
        display_title="User hypothesis",
        display_text="Margin expansion hypothesis",
        as_of=dt(),
        manual_entry_reason="user hypothesis",
        manual_observed_at=dt(),
        created_by_actor="USER",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-user-hypothesis",
    )
    await db.commit()

    estimate_series = await db.get(EvidenceSeries, estimate.evidence_series_id)
    hypothesis_series = await db.get(EvidenceSeries, hypothesis.evidence_series_id)
    assert estimate_series is not None
    assert hypothesis_series is not None
    assert estimate_series.origin_key == expected_manual_origin("USER", " margin-estimate ")
    assert hypothesis_series.origin_key == expected_manual_origin("USER", "margin-estimate")
    assert estimate_series.origin_key == hypothesis_series.origin_key
    assert estimate.source_document_version_id is None
    assert estimate.source_grade_snapshot is None
    assert estimate.source_locators == []

    before = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as wrong_origin:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="ESTIMATE",
            claim_key="margin-estimate",
            provenance_kind="MANUAL",
            origin_key="manual:USER:caller-controlled",
            display_title="Wrong origin",
            display_text="Wrong origin",
            as_of=dt(),
            manual_entry_reason="manual",
            manual_observed_at=dt(),
            created_by_actor="USER",
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key="r1b-wrong-manual-origin",
        )
    assert_error(wrong_origin, "EVIDENCE_INVALID_PROVENANCE")
    assert await evidence_table_counts(db) == before

    source, source_version = await source_with_version(db, key_suffix="manual-source-forbidden")
    invalid_commands: list[dict[str, Any]] = [
        {
            "information_type": "FACT",
            "provenance_kind": "MANUAL",
            "claim_key": "manual-fact",
            "manual_entry_reason": "manual",
            "manual_observed_at": dt(),
            "created_by_actor": "USER",
            "idempotency_key": "r1b-manual-fact",
        },
        {
            "information_type": "ESTIMATE",
            "provenance_kind": "MANUAL",
            "claim_key": "manual-no-reason",
            "manual_entry_reason": None,
            "manual_observed_at": dt(),
            "created_by_actor": "USER",
            "idempotency_key": "r1b-manual-no-reason",
        },
        {
            "information_type": "ESTIMATE",
            "provenance_kind": "MANUAL",
            "claim_key": "manual-with-source",
            "primary_source_document_id": source.id,
            "source_document_version_id": source_version.id,
            "manual_entry_reason": "manual",
            "manual_observed_at": dt(),
            "created_by_actor": "USER",
            "idempotency_key": "r1b-manual-with-source",
        },
        {
            "information_type": "THESIS_INFERENCE",
            "provenance_kind": "DERIVED",
            "claim_key": "derived-with-source",
            "primary_source_document_id": source.id,
            "source_document_version_id": source_version.id,
            "locators": [
                services.SourceLocatorInput(
                    locator_type="PAGE",
                    raw_locator="p.1",
                    short_citation="p.1",
                    locator_payload={"page_number": 1},
                )
            ],
            "idempotency_key": "r1b-derived-with-source",
        },
    ]
    for command in invalid_commands:
        before = await evidence_table_counts(db)
        with pytest.raises(EvidenceDomainError) as invalid:
            await services.create_evidence_series_version(
                db,
                scope_type="INSTRUMENT",
                scope_key=QIANGRUI_INSTRUMENT_ID,
                display_title="Invalid source-less provenance",
                display_text="Invalid source-less provenance",
                as_of=dt(),
                instrument_links=[
                    services.InstrumentLinkInput(
                        instrument_id=QIANGRUI_INSTRUMENT_ID,
                        role="PRIMARY_SCOPE",
                        link_order=1,
                    )
                ],
                **command,
            )
        assert_error(invalid, "EVIDENCE_INVALID_PROVENANCE")
        assert await evidence_table_counts(db) == before


async def test_r1b_derived_identity_links_validation_and_cycle_defense(
    db: AsyncSession,
) -> None:
    """Derived identity is computed from exact supports and invalid graphs leave no residue."""
    support_a = await evidence_fact(db, key_suffix="r1b-support-a")
    support_b = await evidence_fact(db, key_suffix="r1b-support-b")
    derived = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="derived-margin-quality",
        provenance_kind="DERIVED",
        display_title="Derived margin quality",
        display_text="Margin quality is supported by two facts",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_b.id,
                role="INPUT_FACT",
                support_order=2,
                support_weight=Decimal("0.4"),
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
                support_order=1,
                support_weight=Decimal("0.6"),
            ),
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-derived",
    )
    same_origin = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="derived-margin-quality-copy",
        provenance_kind="DERIVED",
        display_title="Derived copy",
        display_text="Same supports in another order",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_b.id,
                role="INPUT_FACT",
            ),
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-derived-same-origin",
    )
    await db.commit()

    series = await db.get(EvidenceSeries, derived.evidence_series_id)
    same_series = await db.get(EvidenceSeries, same_origin.evidence_series_id)
    assert series is not None
    assert same_series is not None
    assert series.origin_key == expected_derived_origin(support_a.id, support_b.id)
    assert same_series.origin_key == series.origin_key
    assert derived.source_document_version_id is None
    assert derived.source_grade_snapshot is None
    assert [(link.supporting_evidence_version_id, link.role) for link in derived.derived_links] == [
        (support_b.id, "INPUT_FACT"),
        (support_a.id, "INPUT_FACT"),
    ]

    invalid_cases = [
        ("r1b-derived-no-support", []),
        (
            "r1b-derived-invalid-role",
            [
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="NOT_A_ROLE",
                )
            ],
        ),
        (
            "r1b-derived-missing-support",
            [
                services.DerivationLinkInput(
                    supporting_evidence_version_id="99999999-9999-4999-8999-999999999999",
                    role="INPUT_FACT",
                )
            ],
        ),
        (
            "r1b-derived-duplicate-edge",
            [
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                ),
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                ),
            ],
        ),
    ]
    for key, derivation_links in invalid_cases:
        before = await evidence_table_counts(db)
        with pytest.raises(EvidenceDomainError) as invalid:
            await services.create_evidence_series_version(
                db,
                scope_type="INSTRUMENT",
                scope_key=QIANGRUI_INSTRUMENT_ID,
                information_type="THESIS_INFERENCE",
                claim_key=key,
                provenance_kind="DERIVED",
                display_title=key,
                display_text=key,
                as_of=dt(),
                derivation_links=derivation_links,
                instrument_links=[
                    services.InstrumentLinkInput(
                        instrument_id=QIANGRUI_INSTRUMENT_ID,
                        role="PRIMARY_SCOPE",
                        link_order=1,
                    )
                ],
                idempotency_key=key,
            )
        assert_error(invalid, "EVIDENCE_INVALID_DERIVATION_LINK")
        assert await evidence_table_counts(db) == before

    before = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as wrong_origin:
        await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key="derived-wrong-origin",
            provenance_kind="DERIVED",
            origin_key="derived:caller-controlled",
            display_title="Derived wrong origin",
            display_text="Derived wrong origin",
            as_of=dt(),
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key="r1b-derived-wrong-origin",
        )
    assert_error(wrong_origin, "EVIDENCE_INVALID_PROVENANCE")
    assert await evidence_table_counts(db) == before

    old_links = [(link.supporting_evidence_version_id, link.role) for link in derived.derived_links]
    prior_exact_replacement = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=1,
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="prior exact version support is acyclic",
        idempotency_key="r1b-derived-prior-exact-support",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived.id,
                role="SUPPORTS_INFERENCE",
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
            ),
        ],
    )
    assert prior_exact_replacement.version == 1
    assert prior_exact_replacement.evidence_series_id != derived.evidence_series_id
    assert prior_exact_replacement.supersedes_evidence_version_id == derived.id
    assert prior_exact_replacement.status_change_kind == "CORRECTION"
    assert prior_exact_replacement.status_changed_at is not None
    assert prior_exact_replacement.status_changed_by_actor == "IMPORTER"
    assert prior_exact_replacement.status_reason == "prior exact version support is acyclic"
    assert [
        (link.supporting_evidence_version_id, link.role)
        for link in prior_exact_replacement.derived_links
    ] == [
        (derived.id, "SUPPORTS_INFERENCE"),
        (support_a.id, "INPUT_FACT"),
    ]
    assert [(link.supporting_evidence_version_id, link.role) for link in derived.derived_links] == (
        old_links
    )

    derived_b = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="derived-b",
        provenance_kind="DERIVED",
        display_title="Derived B",
        display_text="Derived B",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-derived-b",
    )
    derived_a = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="derived-a",
        provenance_kind="DERIVED",
        display_title="Derived A",
        display_text="Derived A",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived_b.id,
                role="SUPPORTS_INFERENCE",
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-derived-a",
    )
    await db.commit()
    derived_b_old_links = [
        (link.supporting_evidence_version_id, link.role) for link in derived_b.derived_links
    ]
    derived_b_replacement = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived_b.evidence_series_id,
        expected_version=1,
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="old exact path does not reach new exact version",
        idempotency_key="r1b-derived-acyclic-prior-chain",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived_a.id,
                role="SUPPORTS_INFERENCE",
            )
        ],
    )
    assert derived_b_replacement.version == 1
    assert derived_b_replacement.evidence_series_id != derived_b.evidence_series_id
    assert derived_b_replacement.supersedes_evidence_version_id == derived_b.id
    assert [
        (link.supporting_evidence_version_id, link.role)
        for link in derived_b_replacement.derived_links
    ] == [(derived_a.id, "SUPPORTS_INFERENCE")]
    assert [
        (link.supporting_evidence_version_id, link.role) for link in derived_b.derived_links
    ] == derived_b_old_links


async def test_r1b_exact_target_derivation_cycle_validator(db: AsyncSession) -> None:
    """Production validation rejects only paths returning to the exact target version."""
    support = await evidence_fact(db, key_suffix="r1b-exact-target-support")
    other_target = await evidence_fact(db, key_suffix="r1b-exact-target-other")
    derived_b = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="r1b-exact-target-b",
        provenance_kind="DERIVED",
        display_title="Exact target B",
        display_text="Exact target B",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support.id,
                role="INPUT_FACT",
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-exact-target-b",
    )
    derived_a = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="r1b-exact-target-a",
        provenance_kind="DERIVED",
        display_title="Exact target A",
        display_text="Exact target A",
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived_b.id,
                role="SUPPORTS_INFERENCE",
            )
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-exact-target-a",
    )
    await db.commit()

    before = await evidence_table_counts(db)
    await services._validate_derivation_links(
        db,
        provenance_kind="DERIVED",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=derived_a.id,
                role="SUPPORTS_INFERENCE",
            )
        ],
        proposed_derived_evidence_version_id=other_target.id,
    )
    assert await evidence_table_counts(db) == before

    with pytest.raises(EvidenceDomainError) as exact_self:
        await services._validate_derivation_links(
            db,
            provenance_kind="DERIVED",
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=derived_b.id,
                    role="SUPPORTS_INFERENCE",
                )
            ],
            proposed_derived_evidence_version_id=derived_b.id,
        )
    assert_error(exact_self, "EVIDENCE_INVALID_DERIVATION_LINK")
    assert await evidence_table_counts(db) == before

    with pytest.raises(EvidenceDomainError) as exact_cycle:
        await services._validate_derivation_links(
            db,
            provenance_kind="DERIVED",
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=derived_a.id,
                    role="SUPPORTS_INFERENCE",
                )
            ],
            proposed_derived_evidence_version_id=derived_b.id,
        )
    assert_error(exact_cycle, "EVIDENCE_INVALID_DERIVATION_LINK")
    assert await evidence_table_counts(db) == before


@pytest.mark.parametrize(
    "operation",
    ["create", "same_series_revision", "replacement", "status_append"],
)
async def test_r1b_public_derived_writes_validate_new_exact_target_before_flush(
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    """Public DERIVED writes validate the actual new immutable ID before persistence."""
    support_a = await evidence_fact(db, key_suffix=f"r1b-target-{operation}-a")
    support_b = await evidence_fact(db, key_suffix=f"r1b-target-{operation}-b")
    derived: EvidenceVersion | None = None
    if operation != "create":
        derived = await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key=f"r1b-target-{operation}",
            provenance_kind="DERIVED",
            display_title="Target timing derived",
            display_text="Target timing derived",
            as_of=dt(),
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                )
            ],
            idempotency_key=f"r1b-target-{operation}-setup",
        )

    flush_started = False
    validation_targets: list[tuple[str | None, bool]] = []
    traversal_targets: list[tuple[str, bool]] = []
    real_flush = AsyncSession.flush
    real_validate = services._validate_derivation_links
    real_reach = services._support_graph_reaches_exact_version

    async def observe_flush(self: AsyncSession, *args: Any, **kwargs: Any) -> None:
        nonlocal flush_started
        flush_started = True
        await real_flush(self, *args, **kwargs)

    async def observe_validation(*args: Any, **kwargs: Any) -> None:
        if kwargs.get("provenance_kind") == "DERIVED":
            validation_targets.append(
                (kwargs.get("proposed_derived_evidence_version_id"), flush_started)
            )
        await real_validate(*args, **kwargs)

    async def observe_reachability(*args: Any, **kwargs: Any) -> bool:
        traversal_targets.append((kwargs["target_evidence_version_id"], flush_started))
        return await real_reach(*args, **kwargs)

    monkeypatch.setattr(AsyncSession, "flush", observe_flush)
    monkeypatch.setattr(services, "_validate_derivation_links", observe_validation)
    monkeypatch.setattr(services, "_support_graph_reaches_exact_version", observe_reachability)

    if operation == "create":
        result = await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key="r1b-target-create",
            provenance_kind="DERIVED",
            display_title="Target timing create",
            display_text="Target timing create",
            as_of=dt(),
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                )
            ],
            idempotency_key="r1b-target-create",
        )
    elif operation == "same_series_revision":
        assert derived is not None
        result = await services.revise_correct_evidence(
            db,
            evidence_series_id=derived.evidence_series_id,
            expected_version=1,
            display_text="Target timing same support set",
            status_changed_at=dt(day=13),
            status_changed_by_actor="IMPORTER",
            status_reason="same support set timing",
            idempotency_key="r1b-target-same-series",
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                    support_order=2,
                )
            ],
        )
    elif operation == "replacement":
        assert derived is not None
        result = await services.revise_correct_evidence(
            db,
            evidence_series_id=derived.evidence_series_id,
            expected_version=1,
            status_changed_at=dt(day=13),
            status_changed_by_actor="IMPORTER",
            status_reason="changed support set timing",
            idempotency_key="r1b-target-replacement",
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_a.id,
                    role="INPUT_FACT",
                ),
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support_b.id,
                    role="INPUT_FACT",
                ),
            ],
        )
    else:
        assert derived is not None
        result = await services.request_review(
            db,
            evidence_series_id=derived.evidence_series_id,
            expected_version=1,
            reason="status append timing",
            actor="IMPORTER",
            idempotency_key="r1b-target-status-append",
            as_of=dt(day=13),
        )

    assert (result.id, False) in validation_targets
    assert (result.id, False) in traversal_targets
    persisted = await db.get(EvidenceVersion, result.id)
    assert persisted is not None
    assert persisted.id == result.id


async def test_r1b_replacement_routing_child_snapshots_and_nullable_clear(
    db: AsyncSession,
) -> None:
    """Identity changes route to replacements; same-set changes append child snapshots."""
    support_a = await evidence_fact(db, key_suffix="r1b-route-a")
    support_b = await evidence_fact(db, key_suffix="r1b-route-b")
    support_c = await evidence_fact(db, key_suffix="r1b-route-c")
    derived = await services.create_evidence_series_version(
        db,
        scope_type="INSTRUMENT",
        scope_key=QIANGRUI_INSTRUMENT_ID,
        information_type="THESIS_INFERENCE",
        claim_key="r1b-route-derived",
        provenance_kind="DERIVED",
        display_title="Route derived",
        display_text="Route derived",
        raw_value="initial",
        raw_unit="score",
        normalized_text_value="initial",
        normalized_unit="score",
        currency="CNY",
        effective_from=dt(),
        effective_to=dt(day=20),
        as_of=dt(),
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
                support_order=1,
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_b.id,
                role="INPUT_FACT",
                support_order=2,
            ),
        ],
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
        idempotency_key="r1b-route-derived",
    )
    same_set = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=1,
        display_text="same support set new weights",
        status_changed_at=dt(day=13),
        status_changed_by_actor="IMPORTER",
        status_reason="same set metadata",
        idempotency_key="r1b-route-derived-same-set",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_b.id,
                role="INPUT_FACT",
                support_order=1,
                support_weight=Decimal("0.7"),
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
                support_order=2,
                support_weight=Decimal("0.3"),
            ),
        ],
    )
    assert same_set.evidence_series_id == derived.evidence_series_id
    assert same_set.version == 2
    assert [
        (link.supporting_evidence_version_id, link.support_weight)
        for link in same_set.derived_links
    ] == [
        (support_b.id, Decimal("0.7")),
        (support_a.id, Decimal("0.3")),
    ]
    assert [
        (link.supporting_evidence_version_id, link.support_weight) for link in derived.derived_links
    ] == [
        (support_a.id, None),
        (support_b.id, None),
    ]

    replacement = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=2,
        status_changed_at=dt(day=14),
        status_changed_by_actor="IMPORTER",
        status_reason="support set changed",
        idempotency_key="r1b-route-derived-replacement",
        derivation_links=[
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_a.id,
                role="INPUT_FACT",
            ),
            services.DerivationLinkInput(
                supporting_evidence_version_id=support_c.id,
                role="INPUT_FACT",
            ),
        ],
    )
    assert replacement.version == 1
    assert replacement.evidence_series_id != derived.evidence_series_id
    assert replacement.supersedes_evidence_version_id == same_set.id
    assert replacement.status_change_kind == "CORRECTION"
    replacement_review = await services.request_review(
        db,
        evidence_series_id=replacement.evidence_series_id,
        expected_version=1,
        reason="replacement review",
        actor="USER",
        idempotency_key="r1b-derived-replacement-review",
        as_of=dt(day=15),
    )
    replacement_verified = await services.verify_or_reject(
        db,
        evidence_series_id=replacement.evidence_series_id,
        expected_version=2,
        decision="VERIFIED",
        reason="replacement verified",
        actor="USER",
        idempotency_key="r1b-derived-replacement-verify",
        as_of=dt(day=16),
    )
    assert replacement_review.verification_status == "PENDING_REVIEW"
    assert replacement_verified.verification_status == "VERIFIED"

    cross_scope = expected_cross_scope(QIANGRUI_INSTRUMENT_ID, SHENLING_INSTRUMENT_ID)
    cross = await services.create_evidence_series_version(
        db,
        scope_type="CROSS_INSTRUMENT",
        scope_key=cross_scope,
        information_type="ESTIMATE",
        claim_key="cross-margin-spread",
        provenance_kind="MANUAL",
        display_title="Cross estimate",
        display_text="Cross estimate",
        as_of=dt(),
        manual_entry_reason="manual cross estimate",
        manual_observed_at=dt(),
        created_by_actor="USER",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=SHENLING_INSTRUMENT_ID,
                role="PEER",
                link_order=2,
                link_metadata={"note": "second"},
            ),
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
                link_metadata={"note": "first"},
            ),
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="RELATED_COMPANY",
                link_order=3,
                link_metadata={"duplicate_id": True},
            ),
        ],
        idempotency_key="r1b-cross",
    )
    cross_series = await db.get(EvidenceSeries, cross.evidence_series_id)
    assert cross_series is not None
    assert cross_series.scope_key == cross_scope

    before = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as wrong_scope:
        await services.create_evidence_series_version(
            db,
            scope_type="CROSS_INSTRUMENT",
            scope_key="caller-controlled",
            information_type="ESTIMATE",
            claim_key="cross-wrong-scope",
            provenance_kind="MANUAL",
            display_title="Wrong cross scope",
            display_text="Wrong cross scope",
            as_of=dt(),
            manual_entry_reason="manual",
            manual_observed_at=dt(),
            created_by_actor="USER",
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                ),
                services.InstrumentLinkInput(
                    instrument_id=SHENLING_INSTRUMENT_ID,
                    role="PEER",
                ),
            ],
            idempotency_key="r1b-cross-wrong-scope",
        )
    assert_error(wrong_scope, "EVIDENCE_INVALID_PROVENANCE")
    assert await evidence_table_counts(db) == before

    cross_same_set = await services.revise_correct_evidence(
        db,
        evidence_series_id=cross.evidence_series_id,
        expected_version=1,
        status_changed_at=dt(day=13),
        status_changed_by_actor="USER",
        status_reason="cross metadata",
        idempotency_key="r1b-cross-same-set",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=10,
                link_metadata={"updated": True},
            ),
            services.InstrumentLinkInput(
                instrument_id=SHENLING_INSTRUMENT_ID,
                role="PEER",
                link_order=20,
            ),
        ],
    )
    assert cross_same_set.evidence_series_id == cross.evidence_series_id
    assert cross_same_set.version == 2

    cross_replacement = await services.revise_correct_evidence(
        db,
        evidence_series_id=cross.evidence_series_id,
        expected_version=2,
        status_changed_at=dt(day=14),
        status_changed_by_actor="USER",
        status_reason="cross member set changed",
        idempotency_key="r1b-cross-replacement",
        instrument_links=[
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
            )
        ],
    )
    assert cross_replacement.version == 1
    assert cross_replacement.evidence_series_id != cross.evidence_series_id
    assert cross_replacement.supersedes_evidence_version_id == cross_same_set.id
    cross_review = await services.request_review(
        db,
        evidence_series_id=cross_replacement.evidence_series_id,
        expected_version=1,
        reason="cross replacement review",
        actor="USER",
        idempotency_key="r1b-cross-replacement-review",
        as_of=dt(day=15),
    )
    cross_verified = await services.verify_or_reject(
        db,
        evidence_series_id=cross_replacement.evidence_series_id,
        expected_version=2,
        decision="VERIFIED",
        reason="cross replacement verified",
        actor="USER",
        idempotency_key="r1b-cross-replacement-verify",
        as_of=dt(day=16),
    )
    assert cross_review.verification_status == "PENDING_REVIEW"
    assert cross_verified.verification_status == "VERIFIED"

    derived_tombstone = await services.retract_or_invalidate(
        db,
        evidence_series_id=replacement_verified.evidence_series_id,
        expected_version=3,
        target_status="INVALIDATED",
        reason="derived invalidated",
        actor="IMPORTER",
        idempotency_key="r1b-derived-tombstone",
        as_of=dt(day=15),
    )
    cross_tombstone = await services.retract_or_invalidate(
        db,
        evidence_series_id=cross_verified.evidence_series_id,
        expected_version=3,
        target_status="RETRACTED",
        reason="cross retracted",
        actor="USER",
        idempotency_key="r1b-cross-tombstone",
        as_of=dt(day=15),
    )
    assert len(derived_tombstone.derived_links) == len(replacement_verified.derived_links)
    assert len(cross_tombstone.instrument_links) == len(cross_verified.instrument_links)

    retained = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=2,
        display_text="omitted nullable values are retained",
        status_changed_at=dt(day=16),
        status_changed_by_actor="IMPORTER",
        status_reason="retain nullable",
        idempotency_key="r1b-nullable-retain",
    )
    assert retained.raw_unit == "score"
    assert retained.normalized_text_value == "initial"
    assert retained.normalized_unit == "score"
    assert retained.currency == "CNY"
    assert retained.effective_to == dt(day=20)

    cleared = await services.revise_correct_evidence(
        db,
        evidence_series_id=derived.evidence_series_id,
        expected_version=3,
        display_text="explicit nullable values are cleared",
        raw_unit=None,
        normalized_text_value=None,
        normalized_unit=None,
        currency=None,
        effective_to=None,
        status_changed_at=dt(day=17),
        status_changed_by_actor="IMPORTER",
        status_reason="clear nullable",
        idempotency_key="r1b-nullable-clear",
    )
    assert cleared.raw_unit is None
    assert cleared.normalized_text_value is None
    assert cleared.normalized_unit is None
    assert cleared.currency is None
    assert cleared.effective_to is None

    before = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as non_nullable_clear:
        await services.revise_correct_evidence(
            db,
            evidence_series_id=derived.evidence_series_id,
            expected_version=4,
            display_text=None,
            status_changed_at=dt(day=18),
            status_changed_by_actor="IMPORTER",
            status_reason="clear display text",
            idempotency_key="r1b-non-null-clear",
        )
    assert_error(non_nullable_clear, "EVIDENCE_INVALID_PROVENANCE")
    assert await evidence_table_counts(db) == before


async def test_r1b_llm_proposal_extractor_provenance(db: AsyncSession) -> None:
    """Automatic extraction provenance is fail-closed and persisted exactly."""
    source, source_version = await source_with_version(db, key_suffix="r1b-llm")
    base_command: dict[str, Any] = {
        "db": db,
        "scope_type": "INSTRUMENT",
        "scope_key": QIANGRUI_INSTRUMENT_ID,
        "information_type": "FACT",
        "provenance_kind": "SOURCE_BACKED",
        "primary_source_document_id": source.id,
        "source_document_version_id": source_version.id,
        "display_title": "LLM extracted fact",
        "display_text": "LLM extracted fact",
        "as_of": dt(),
        "locators": [
            services.SourceLocatorInput(
                locator_type="PAGE",
                raw_locator="p.1",
                short_citation="p.1",
                locator_payload={"page_number": 1},
            )
        ],
        "instrument_links": [
            services.InstrumentLinkInput(
                instrument_id=QIANGRUI_INSTRUMENT_ID,
                role="PRIMARY_SCOPE",
                link_order=1,
            )
        ],
    }

    invalid_extractor_cases: list[tuple[str, dict[str, Any]]] = [
        ("missing-all", {}),
        ("missing-prompt", {"extractor_name": "tg-llm", "extractor_version": "1.0"}),
        (
            "blank-name",
            {"extractor_name": " ", "extractor_version": "1.0", "prompt_template_version": "p1"},
        ),
    ]
    for suffix, extra in invalid_extractor_cases:
        before = await evidence_table_counts(db)
        with pytest.raises(EvidenceDomainError) as invalid:
            await services.create_evidence_series_version(
                **base_command,
                claim_key=f"r1b-llm-{suffix}",
                created_by_actor="LLM_PROPOSAL",
                idempotency_key=f"r1b-llm-{suffix}",
                **extra,
            )
        assert_error(invalid, "EVIDENCE_INVALID_PROVENANCE")
        assert await evidence_table_counts(db) == before

    before = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as partial_importer:
        await services.create_evidence_series_version(
            **base_command,
            claim_key="r1b-importer-partial-extractor",
            created_by_actor="IMPORTER",
            extractor_name="tg-parser",
            idempotency_key="r1b-importer-partial-extractor",
        )
    assert_error(partial_importer, "EVIDENCE_INVALID_PROVENANCE")
    assert await evidence_table_counts(db) == before

    complete = await services.create_evidence_series_version(
        **base_command,
        claim_key="r1b-llm-complete",
        created_by_actor="LLM_PROPOSAL",
        extractor_name="tg-llm",
        extractor_version="1.0",
        prompt_template_version="evidence-extract-v1",
        idempotency_key="r1b-llm-complete",
    )
    assert complete.extractor_name == "tg-llm"
    assert complete.extractor_version == "1.0"
    assert complete.prompt_template_version == "evidence-extract-v1"


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


async def evidence_with_lifecycle_status(
    db: AsyncSession,
    *,
    status: str,
    key_suffix: str,
) -> EvidenceVersion:
    """Create a series whose current version has the requested lifecycle status."""
    if status == "UNREVIEWED":
        current = await evidence_fact(db, key_suffix=key_suffix)
    elif status == "VERIFIED":
        current = await verified_evidence_fact(db, key_suffix=key_suffix)
    elif status == "PENDING_REVIEW":
        base = await evidence_fact(db, key_suffix=key_suffix)
        await db.commit()
        current = await services.request_review(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            reason="matrix review requested",
            actor="USER",
            idempotency_key=f"{key_suffix}-to-pending",
            as_of=dt(day=14),
        )
    elif status == "REJECTED":
        base = await evidence_fact(db, key_suffix=key_suffix)
        await db.commit()
        pending = await services.request_review(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            reason="matrix review requested",
            actor="USER",
            idempotency_key=f"{key_suffix}-to-pending",
            as_of=dt(day=14),
        )
        current = await services.verify_or_reject(
            db,
            evidence_series_id=pending.evidence_series_id,
            expected_version=2,
            decision="REJECTED",
            reason="matrix rejected",
            actor="USER",
            idempotency_key=f"{key_suffix}-to-rejected",
            as_of=dt(day=15),
        )
    elif status == "DISPUTED":
        base = await verified_evidence_fact(db, key_suffix=key_suffix)
        await db.commit()
        current = await services.mark_disputed(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            reason="matrix disputed",
            actor="USER",
            idempotency_key=f"{key_suffix}-to-disputed",
            as_of=dt(day=14),
        )
    elif status == "INVALIDATED":
        base = await verified_evidence_fact(db, key_suffix=key_suffix)
        await db.commit()
        current = await services.retract_or_invalidate(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            target_status="INVALIDATED",
            reason="matrix invalidated",
            actor="IMPORTER",
            idempotency_key=f"{key_suffix}-to-invalidated",
            as_of=dt(day=14),
        )
    elif status == "RETRACTED":
        base = await verified_evidence_fact(db, key_suffix=key_suffix)
        await db.commit()
        current = await services.retract_or_invalidate(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=1,
            target_status="RETRACTED",
            reason="matrix retracted",
            actor="IMPORTER",
            idempotency_key=f"{key_suffix}-to-retracted",
            as_of=dt(day=14),
        )
    else:
        raise AssertionError(f"Unhandled lifecycle status {status}")
    await db.commit()
    return current


LIFECYCLE_COMMAND_MATRIX = [
    ("UNREVIEWED", "request_review", None, True, "PENDING_REVIEW", "REVIEW_REQUEST"),
    ("UNREVIEWED", "verify_or_reject", "VERIFIED", False, None, None),
    ("UNREVIEWED", "verify_or_reject", "REJECTED", True, "REJECTED", "REVIEW_DECISION"),
    ("UNREVIEWED", "mark_disputed", None, False, None, None),
    ("UNREVIEWED", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("UNREVIEWED", "retract_or_invalidate", "RETRACTED", False, None, None),
    ("PENDING_REVIEW", "request_review", None, False, None, None),
    ("PENDING_REVIEW", "verify_or_reject", "VERIFIED", True, "VERIFIED", "REVIEW_DECISION"),
    ("PENDING_REVIEW", "verify_or_reject", "REJECTED", True, "REJECTED", "REVIEW_DECISION"),
    ("PENDING_REVIEW", "mark_disputed", None, False, None, None),
    ("PENDING_REVIEW", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("PENDING_REVIEW", "retract_or_invalidate", "RETRACTED", False, None, None),
    ("VERIFIED", "request_review", None, False, None, None),
    ("VERIFIED", "verify_or_reject", "VERIFIED", False, None, None),
    ("VERIFIED", "verify_or_reject", "REJECTED", False, None, None),
    ("VERIFIED", "mark_disputed", None, True, "DISPUTED", "DISPUTE"),
    ("VERIFIED", "retract_or_invalidate", "INVALIDATED", True, "INVALIDATED", "INVALIDATION"),
    ("VERIFIED", "retract_or_invalidate", "RETRACTED", True, "RETRACTED", "RETRACTION"),
    ("DISPUTED", "request_review", None, False, None, None),
    ("DISPUTED", "verify_or_reject", "VERIFIED", True, "VERIFIED", "DISPUTE"),
    ("DISPUTED", "verify_or_reject", "REJECTED", True, "REJECTED", "DISPUTE"),
    ("DISPUTED", "mark_disputed", None, False, None, None),
    ("DISPUTED", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("DISPUTED", "retract_or_invalidate", "RETRACTED", True, "RETRACTED", "RETRACTION"),
    ("REJECTED", "request_review", None, False, None, None),
    ("REJECTED", "verify_or_reject", "VERIFIED", False, None, None),
    ("REJECTED", "verify_or_reject", "REJECTED", False, None, None),
    ("REJECTED", "mark_disputed", None, False, None, None),
    ("REJECTED", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("REJECTED", "retract_or_invalidate", "RETRACTED", False, None, None),
    ("INVALIDATED", "request_review", None, False, None, None),
    ("INVALIDATED", "verify_or_reject", "VERIFIED", False, None, None),
    ("INVALIDATED", "verify_or_reject", "REJECTED", False, None, None),
    ("INVALIDATED", "mark_disputed", None, False, None, None),
    ("INVALIDATED", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("INVALIDATED", "retract_or_invalidate", "RETRACTED", False, None, None),
    ("RETRACTED", "request_review", None, False, None, None),
    ("RETRACTED", "verify_or_reject", "VERIFIED", False, None, None),
    ("RETRACTED", "verify_or_reject", "REJECTED", False, None, None),
    ("RETRACTED", "mark_disputed", None, False, None, None),
    ("RETRACTED", "retract_or_invalidate", "INVALIDATED", False, None, None),
    ("RETRACTED", "retract_or_invalidate", "RETRACTED", False, None, None),
]


@pytest.mark.parametrize(
    (
        "from_status",
        "command",
        "decision_or_target",
        "allowed",
        "to_status",
        "audit_kind",
    ),
    LIFECYCLE_COMMAND_MATRIX,
)
async def test_r1c_state_transition_command_matrix_and_audit_mapping(
    db: AsyncSession,
    from_status: str,
    command: str,
    decision_or_target: str | None,
    allowed: bool,
    to_status: str | None,
    audit_kind: str | None,
) -> None:
    """R1C: status commands exactly match the frozen lifecycle transition table."""
    current = await evidence_with_lifecycle_status(
        db,
        status=from_status,
        key_suffix=f"r1c-matrix-{from_status.lower()}-{command}-{decision_or_target or 'none'}",
    )
    before_counts = await evidence_table_counts(db)
    expected_version = current.version
    idempotency_key = (
        f"r1c-matrix-{from_status.lower()}-{command}-{decision_or_target or 'none'}-cmd"
    )

    async def run_command() -> EvidenceVersion:
        if command == "request_review":
            return await services.request_review(
                db,
                evidence_series_id=current.evidence_series_id,
                expected_version=expected_version,
                reason="matrix review",
                actor="USER",
                idempotency_key=idempotency_key,
                as_of=dt(day=20),
            )
        if command == "verify_or_reject":
            assert decision_or_target is not None
            return await services.verify_or_reject(
                db,
                evidence_series_id=current.evidence_series_id,
                expected_version=expected_version,
                decision=decision_or_target,
                reason="matrix decision",
                actor="USER",
                idempotency_key=idempotency_key,
                as_of=dt(day=20),
            )
        if command == "mark_disputed":
            return await services.mark_disputed(
                db,
                evidence_series_id=current.evidence_series_id,
                expected_version=expected_version,
                reason="matrix dispute",
                actor="USER",
                idempotency_key=idempotency_key,
                as_of=dt(day=20),
            )
        if command == "retract_or_invalidate":
            assert decision_or_target is not None
            return await services.retract_or_invalidate(
                db,
                evidence_series_id=current.evidence_series_id,
                expected_version=expected_version,
                target_status=decision_or_target,
                reason="matrix tombstone",
                actor="IMPORTER",
                idempotency_key=idempotency_key,
                as_of=dt(day=20),
            )
        raise AssertionError(f"Unhandled lifecycle command {command}")

    if not allowed:
        with pytest.raises(EvidenceDomainError) as invalid:
            await run_command()
        assert_error(invalid, "EVIDENCE_INVALID_STATE_TRANSITION")
        assert invalid.value.details["from_status"] == from_status
        assert await evidence_table_counts(db) == before_counts
        history = await services.list_evidence_history(db, current.evidence_series_id)
        assert history[-1].id == current.id
        return

    result = await run_command()
    await db.flush()
    after_counts = await evidence_table_counts(db)
    replay = await run_command()
    history = await services.list_evidence_history(db, current.evidence_series_id)

    assert result.id == replay.id
    assert result.version == current.version + 1
    assert result.verification_status == to_status
    assert result.status_change_kind == audit_kind
    assert result.status_changed_at == dt(day=20)
    assert result.status_changed_by_actor in {"USER", "IMPORTER"}
    assert result.status_reason in {
        "matrix review",
        "matrix decision",
        "matrix dispute",
        "matrix tombstone",
    }
    assert result.supersedes_evidence_version_id == current.id
    assert len(result.source_locators) == len(current.source_locators)
    assert len(result.instrument_links) == len(current.instrument_links)
    assert history[-2].id == current.id
    assert history[-1].id == result.id
    assert after_counts["version"] == before_counts["version"] + 1
    assert after_counts["locator"] == before_counts["locator"] + len(current.source_locators)
    assert after_counts["instrument_link"] == before_counts["instrument_link"] + len(
        current.instrument_links
    )
    assert after_counts["idempotency"] == before_counts["idempotency"] + 1
    assert after_counts["audit"] == before_counts["audit"] + 1
    assert await evidence_table_counts(db) == after_counts


async def test_r1c_state_transition_invalid_decision_and_version_conflict_leave_no_residue(
    db: AsyncSession,
) -> None:
    """R1C: invalid decision and stale expected_version fail before status writes."""
    created = await evidence_fact(db, key_suffix="r1c-invalid-decision")
    await db.commit()
    before_invalid_decision = await evidence_table_counts(db)

    with pytest.raises(EvidenceDomainError) as invalid_decision:
        await services.verify_or_reject(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=1,
            decision="MAYBE",
            reason="bad decision",
            actor="USER",
            idempotency_key="r1c-invalid-decision",
            as_of=dt(day=20),
        )
    assert_error(invalid_decision, "EVIDENCE_VALIDATION_ERROR")
    assert await evidence_table_counts(db) == before_invalid_decision

    before_conflict = await evidence_table_counts(db)
    with pytest.raises(EvidenceDomainError) as stale:
        await services.request_review(
            db,
            evidence_series_id=created.evidence_series_id,
            expected_version=0,
            reason="stale review",
            actor="USER",
            idempotency_key="r1c-stale-review",
            as_of=dt(day=20),
        )
    assert_error(stale, "EVIDENCE_VERSION_CONFLICT")
    assert stale.value.expected_version == 0
    assert stale.value.current_version == 1
    assert await evidence_table_counts(db) == before_conflict


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
    retracted = await services.retract_or_invalidate(
        db,
        evidence_series_id=created.evidence_series_id,
        expected_version=4,
        target_status="RETRACTED",
        reason="disputed fact withdrawn",
        actor="IMPORTER",
        idempotency_key="life-retract",
        as_of=dt(day=17),
    )
    invalidation_base = await verified_evidence_fact(db, key_suffix="life-invalidate")
    invalidated = await services.retract_or_invalidate(
        db,
        evidence_series_id=invalidation_base.evidence_series_id,
        expected_version=1,
        target_status="INVALIDATED",
        reason="verified fact invalidated",
        actor="IMPORTER",
        idempotency_key="life-invalidate",
        as_of=dt(day=17),
    )
    await db.commit()

    assert corrected.version == 2
    assert corrected.verification_status == "UNREVIEWED"
    assert corrected.trusted_correction_rule is None
    assert corrected.supersedes_evidence_version_id == corrected_base.id
    assert review.verification_status == "PENDING_REVIEW"
    assert verified.verification_status == "VERIFIED"
    assert disputed.verification_status == "DISPUTED"
    assert retracted.verification_status == "RETRACTED"
    assert retracted.status_change_kind == "RETRACTION"
    assert retracted.display_title == disputed.display_title
    assert len(retracted.source_locators) == len(disputed.source_locators)
    assert invalidated.verification_status == "INVALIDATED"
    assert invalidated.status_change_kind == "INVALIDATION"
    assert invalidated.supersedes_evidence_version_id == invalidation_base.id

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
        assert history[0].id == created.id
        assert history[0].raw_value == "32.5%"
        assert history[1].verification_status == "UNREVIEWED"
        assert history[1].trusted_correction_rule is None


# R1C-03A: no production trusted correction rule is approved. Historical test
# snapshots below model existing data, never authorization for a new command.
R1C03A_INVALID_RULES = [
    pytest.param("", id="empty"),
    pytest.param(" \t\n", id="whitespace"),
    pytest.param("unknown-rule", id="unknown"),
    pytest.param("same-source-parser-v1", id="old-parser-fixture"),
    pytest.param("concurrent-test", id="old-concurrency-fixture"),
    pytest.param("SAME-SOURCE-PARSER-V1", id="case-variant"),
    pytest.param(0, id="integer-zero"),
    pytest.param(1, id="integer-one"),
    pytest.param(False, id="boolean-false"),
    pytest.param(True, id="boolean-true"),
    pytest.param([], id="list"),
    pytest.param({"rule": "unknown-rule"}, id="mapping"),
    pytest.param(b"unknown-rule", id="bytes"),
    pytest.param({"unknown-rule"}, id="set"),
    pytest.param(object(), id="object"),
]


def r1c03a_columns(row: Any) -> dict[str, Any]:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def r1c03a_exact_snapshot(row: EvidenceVersion) -> dict[str, Any]:
    return {
        "version": r1c03a_columns(row),
        "locators": [r1c03a_columns(child) for child in row.source_locators],
        "instrument_links": [r1c03a_columns(child) for child in row.instrument_links],
        "derivation_links": [r1c03a_columns(child) for child in row.derived_links],
    }


async def r1c03a_legacy_prior(db: AsyncSession, *, derived: bool) -> EvidenceVersion:
    """Legally append a complete legacy snapshot; never update old rows."""
    base = await verified_evidence_fact(db, key_suffix="r1c03a-base")
    if derived:
        base = await services.create_evidence_series_version(
            db,
            scope_type="INSTRUMENT",
            scope_key=QIANGRUI_INSTRUMENT_ID,
            information_type="THESIS_INFERENCE",
            claim_key="r1c03a-derived",
            provenance_kind="DERIVED",
            display_title="Historical inference",
            display_text="Historical inference",
            as_of=dt(),
            derivation_links=[
                services.DerivationLinkInput(
                    supporting_evidence_version_id=base.id,
                    role="INPUT_FACT",
                    support_order=1,
                )
            ],
            instrument_links=[
                services.InstrumentLinkInput(
                    instrument_id=QIANGRUI_INSTRUMENT_ID,
                    role="PRIMARY_SCOPE",
                    link_order=1,
                )
            ],
            idempotency_key="r1c03a-derived-base",
        )
        pending = await services.request_review(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=base.version,
            reason="Historical review",
            actor="USER",
            idempotency_key="r1c03a-derived-review",
            as_of=dt(day=13),
        )
        base = await services.verify_or_reject(
            db,
            evidence_series_id=base.evidence_series_id,
            expected_version=pending.version,
            decision="VERIFIED",
            reason="Historical review accepted",
            actor="USER",
            idempotency_key="r1c03a-derived-verify",
            as_of=dt(day=14),
        )
    values = r1c03a_columns(base)
    values.update(
        id=str(uuid4()),
        version=base.version + 1,
        supersedes_evidence_version_id=base.id,
        verification_status="VERIFIED",
        trusted_correction_rule="legacy-historical-rule",
        status_changed_at=dt(day=15),
        status_changed_by_actor="IMPORTER",
        status_change_kind="CORRECTION",
        status_reason="Existing legacy snapshot",
        created_at=dt(day=15),
        created_by_actor="IMPORTER",
    )
    legacy = EvidenceVersion(**values)
    for relationship, model, foreign_key in (
        ("source_locators", EvidenceSourceLocator, "evidence_version_id"),
        ("instrument_links", EvidenceInstrumentLink, "evidence_version_id"),
        ("derived_links", EvidenceDerivationLink, "derived_evidence_version_id"),
    ):
        children = []
        for child in getattr(base, relationship):
            child_values = r1c03a_columns(child)
            child_values.update(id=str(uuid4()), **{foreign_key: legacy.id})
            children.append(model(**child_values))
        setattr(legacy, relationship, children)
    db.add(legacy)
    await db.flush()
    loaded = await services.get_exact_evidence_version(db, legacy.id)
    assert loaded is not None
    await db.commit()
    return loaded


def r1c03a_create_fields(prior: EvidenceVersion, series: EvidenceSeries) -> dict[str, Any]:
    """Explicit public-command fields, including complete child content."""
    return {
        "scope_type": series.scope_type,
        "scope_key": series.scope_key,
        "information_type": prior.information_type,
        "claim_key": prior.claim_key,
        "metric_key": "r1c03a-new-metric",
        "period_start": prior.period_start,
        "period_end": prior.period_end,
        "provenance_kind": prior.provenance_kind,
        "primary_source_document_id": series.primary_source_document_id,
        "source_document_version_id": prior.source_document_version_id,
        "display_title": prior.display_title,
        "display_text": "Corrected content",
        "raw_value": prior.raw_value,
        "raw_unit": prior.raw_unit,
        "normalized_value": prior.normalized_value,
        "normalized_unit": prior.normalized_unit,
        "as_of": prior.as_of,
        "extractor_name": prior.extractor_name,
        "extractor_version": prior.extractor_version,
        "locators": [
            services.SourceLocatorInput(
                locator_type=x.locator_type,
                raw_locator=x.raw_locator,
                short_citation=x.short_citation,
                locator_payload=dict(x.locator_payload),
                quote_hash=x.quote_hash,
            )
            for x in prior.source_locators
        ],
        "instrument_links": [
            services.InstrumentLinkInput(
                instrument_id=x.instrument_id,
                role=x.role,
                link_order=x.link_order,
                link_metadata=dict(x.link_metadata or {}),
            )
            for x in prior.instrument_links
        ],
    }


async def r1c03a_command(
    db: AsyncSession,
    *,
    prior: EvidenceVersion,
    entry: str,
    rule_kwargs: dict[str, Any],
    key: str,
) -> EvidenceVersion:
    audit: dict[str, Any] = {
        "status_changed_at": dt(day=16),
        "status_changed_by_actor": "IMPORTER",
        "status_reason": "R1C03A correction",
        "idempotency_key": key,
    }
    if entry in {"same-series", "automatic-replacement"}:
        children: dict[str, Any] = {}
        if entry == "automatic-replacement":
            support = await services.get_exact_evidence_version(
                db,
                prior.derived_links[0].supporting_evidence_version_id,
            )
            assert support is not None
            children["derivation_links"] = [
                services.DerivationLinkInput(
                    supporting_evidence_version_id=support.supersedes_evidence_version_id
                    or support.id,
                    role="INPUT_FACT",
                    support_order=1,
                )
            ]
            # A different exact support ID changes the DERIVED series identity.
            if children["derivation_links"][0].supporting_evidence_version_id == support.id:
                history = await services.list_evidence_history(db, prior.evidence_series_id)
                children["derivation_links"][0] = services.DerivationLinkInput(
                    supporting_evidence_version_id=history[0].id,
                    role="INPUT_FACT",
                    support_order=1,
                )
        return await services.revise_correct_evidence(
            db,
            evidence_series_id=prior.evidence_series_id,
            expected_version=prior.version,
            display_text="Corrected content",
            **audit,
            **children,
            **rule_kwargs,
        )
    series = await db.get(EvidenceSeries, prior.evidence_series_id)
    assert series is not None
    fields = r1c03a_create_fields(prior, series)
    if entry == "direct-replacement":
        return await services.create_replacement_evidence_series(
            db,
            prior_evidence_version_id=prior.id,
            **fields,
            **audit,
            **rule_kwargs,
        )
    if entry == "create-initial":
        return await services.create_evidence_series_version(
            db,
            **fields,
            idempotency_key=key,
            **rule_kwargs,
        )
    assert entry == "create-replacement"
    return await services.create_evidence_series_version(
        db,
        **fields,
        supersedes_evidence_version_id=prior.id,
        verification_status="VERIFIED",
        status_change_kind="CORRECTION",
        **audit,
        **rule_kwargs,
    )


@pytest.mark.parametrize(
    "entry",
    [
        "same-series",
        "automatic-replacement",
        "direct-replacement",
        "create-initial",
        "create-replacement",
    ],
)
@pytest.mark.parametrize("rule", R1C03A_INVALID_RULES)
async def test_r1c03a_trusted_rule_rejected_before_writes_fresh_session(
    db: AsyncSession,
    pg_sessionmaker: async_sessionmaker[AsyncSession],
    entry: str,
    rule: Any,
) -> None:
    prior = await r1c03a_legacy_prior(db, derived=entry == "automatic-replacement")
    before = await evidence_table_counts(db)
    snapshot = r1c03a_exact_snapshot(prior)
    series = await db.get(EvidenceSeries, prior.evidence_series_id)
    assert series is not None
    series_snapshot = r1c03a_columns(series)
    with pytest.raises(EvidenceValidationError) as error:
        await r1c03a_command(
            db,
            prior=prior,
            entry=entry,
            rule_kwargs={"trusted_correction_rule": rule},
            key="r1c03a-denied",
        )
    assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
    assert error.value.details["validation_path"] == "trusted_correction_rule"
    assert error.value.details["trusted_correction_rule"] == rule
    assert error.value.details["rule_type"] == type(rule).__name__
    assert not db.new
    assert not db.dirty
    await (
        db.commit()
    )  # Deliberately commit after domain rejection, never hide writes with rollback.
    async with pg_sessionmaker() as reader:
        assert await evidence_table_counts(reader) == before
        exact = await services.get_exact_evidence_version(reader, prior.id)
        assert exact is not None
        assert r1c03a_exact_snapshot(exact) == snapshot
        persisted_series = await reader.get(EvidenceSeries, prior.evidence_series_id)
        assert persisted_series is not None
        assert r1c03a_columns(persisted_series) == series_snapshot
        current = await services.get_current_evidence(reader, prior.evidence_series_id)
        assert current is not None and current.id == prior.id
        assert (
            await reader.get(
                EvidenceIdempotencyRecord, ("revise_correct_evidence", "r1c03a-denied")
            )
            is None
        )


@pytest.mark.parametrize(
    "entry", ["same-series", "automatic-replacement", "direct-replacement", "create-replacement"]
)
@pytest.mark.parametrize(
    "rule_kwargs", [{}, {"trusted_correction_rule": None}], ids=["omitted", "none"]
)
async def test_r1c03a_ordinary_correction_does_not_inherit_legacy_rule(
    db: AsyncSession,
    pg_sessionmaker: async_sessionmaker[AsyncSession],
    entry: str,
    rule_kwargs: dict[str, Any],
) -> None:
    prior = await r1c03a_legacy_prior(db, derived=entry == "automatic-replacement")
    prior_snapshot = r1c03a_exact_snapshot(prior)
    before = await evidence_table_counts(db)
    corrected = await r1c03a_command(
        db, prior=prior, entry=entry, rule_kwargs=rule_kwargs, key="r1c03a-ordinary"
    )
    corrected_id = corrected.id
    await db.commit()
    async with pg_sessionmaker() as reader:
        exact = await services.get_exact_evidence_version(reader, prior.id)
        result = await services.get_exact_evidence_version(reader, corrected_id)
        assert exact is not None and result is not None
        assert r1c03a_exact_snapshot(exact) == prior_snapshot
        assert result.verification_status == "UNREVIEWED"
        assert result.trusted_correction_rule is None
        assert result.supersedes_evidence_version_id == prior.id
        assert result.status_changed_at == dt(day=16)
        assert result.status_changed_by_actor == "IMPORTER"
        assert result.status_change_kind == "CORRECTION"
        assert result.status_reason == "R1C03A correction"
        assert result.display_text == "Corrected content"
        assert await services.get_current_valid_evidence(reader, result.evidence_series_id) is None
        if entry == "same-series":
            assert result.evidence_series_id == prior.evidence_series_id
            assert result.version == prior.version + 1
            assert (await evidence_table_counts(reader))["series"] == before["series"]
        else:
            assert result.evidence_series_id != prior.evidence_series_id
            assert result.version == 1
            assert (await evidence_table_counts(reader))["series"] == before["series"] + 1
            current = await services.get_current_evidence(reader, prior.evidence_series_id)
            assert current is not None and current.id == prior.id
        for relationship in ("source_locators", "instrument_links", "derived_links"):
            old_children = getattr(exact, relationship)
            new_children = getattr(result, relationship)
            assert len(new_children) == len(old_children)
            assert {x.id for x in old_children}.isdisjoint(x.id for x in new_children)
        pending = await services.request_review(
            reader,
            evidence_series_id=result.evidence_series_id,
            expected_version=result.version,
            reason="Ordinary correction review",
            actor="USER",
            idempotency_key="r1c03a-review",
            as_of=dt(day=17),
        )
        verified = await services.verify_or_reject(
            reader,
            evidence_series_id=result.evidence_series_id,
            expected_version=pending.version,
            decision="VERIFIED",
            reason="Review accepted",
            actor="USER",
            idempotency_key="r1c03a-verify",
            as_of=dt(day=18),
        )
        assert verified.verification_status == "VERIFIED"
        assert verified.trusted_correction_rule is None
        eligible = await services.get_current_valid_evidence(reader, result.evidence_series_id)
        assert eligible is not None and eligible.id == verified.id
        await reader.commit()


@pytest.mark.parametrize("entry", ["direct-replacement", "create-initial"])
@pytest.mark.parametrize(
    "trusted_request", [False, True], ids=["ordinary-replay", "new-trusted-request"]
)
async def test_r1c03a_replay_does_not_swallow_new_trusted_request(
    db: AsyncSession,
    pg_sessionmaker: async_sessionmaker[AsyncSession],
    entry: str,
    trusted_request: bool,
) -> None:
    prior = await r1c03a_legacy_prior(db, derived=False)
    created = await r1c03a_command(
        db, prior=prior, entry=entry, rule_kwargs={}, key="r1c03a-replay"
    )
    created_id = created.id
    await db.commit()
    before = await evidence_table_counts(db)
    async with pg_sessionmaker() as caller:
        exact_prior = await services.get_exact_evidence_version(caller, prior.id)
        assert exact_prior is not None
        if trusted_request:
            with pytest.raises(EvidenceValidationError) as error:
                await r1c03a_command(
                    caller,
                    prior=exact_prior,
                    entry=entry,
                    rule_kwargs={"trusted_correction_rule": "unknown-rule"},
                    key="r1c03a-replay",
                )
            assert error.value.code == "EVIDENCE_VALIDATION_ERROR"
            assert error.value.details["validation_path"] == "trusted_correction_rule"
        else:
            replay = await r1c03a_command(
                caller, prior=exact_prior, entry=entry, rule_kwargs={}, key="r1c03a-replay"
            )
            assert replay.id == created_id
        await caller.commit()
    async with pg_sessionmaker() as reader:
        assert await evidence_table_counts(reader) == before
        persisted = await services.get_exact_evidence_version(reader, created_id)
        assert persisted is not None
        assert persisted.verification_status == "UNREVIEWED"
        assert persisted.trusted_correction_rule is None
