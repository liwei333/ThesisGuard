from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from datetime import UTC, datetime
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
    SourceDocumentVersion,
)
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


ADMIN_URL = "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
NOW = datetime(2026, 9, 15, tzinfo=UTC)
EXACT_MATRIX = {
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


@pytest_asyncio.fixture
async def db() -> AsyncIterator[AsyncSession]:
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", ADMIN_URL))
    admin_db = admin_url.database or "postgres"
    db_name = f"tg_wp04_r1a_verify_{uuid4().hex}"
    admin = await asyncpg.connect(
        user=admin_url.username,
        password=admin_url.password,
        host=admin_url.host or "127.0.0.1",
        port=admin_url.port or 5432,
        database=admin_db,
    )
    await admin.execute(f'CREATE DATABASE "{db_name}"')
    await admin.close()
    test_url = admin_url.set(database=db_name).render_as_string(hide_password=False)
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        check=True,
        env={**os.environ, "DATABASE_URL": test_url},
        capture_output=True,
        text=True,
    )
    engine = create_async_engine(test_url)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            yield session
            await session.rollback()
    finally:
        await engine.dispose()
        cleanup = await asyncpg.connect(
            user=admin_url.username,
            password=admin_url.password,
            host=admin_url.host or "127.0.0.1",
            port=admin_url.port or 5432,
            database=admin_db,
        )
        await cleanup.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = $1 AND pid <> pg_backend_pid()",
            db_name,
        )
        await cleanup.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        await cleanup.close()


async def make_source(
    db: AsyncSession,
    suffix: str,
    source_type: str,
    grade: str,
    metadata: dict | None = None,
):
    source = await services.register_source_document(
        db,
        publisher_key=f"publisher-{suffix}",
        publisher_name="Verifier Publisher",
        source_type=source_type,
        external_document_id=f"doc-{suffix}",
        canonical_url=f"https://example.test/{suffix}",
        title="Verifier source",
        document_language="zh-CN",
        created_by_actor="IMPORTER",
        idempotency_key=f"register-{suffix}",
        as_of=NOW,
    )
    version = await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=0,
        version_reason="NEW_CONTENT",
        source_grade=grade,
        published_at=NOW,
        observed_at=NOW,
        fetched_at=NOW,
        content_hash=(f"content-{suffix}" + "0" * 128)[:64],
        source_version_label="v1",
        media_type="application/pdf",
        object_key=f"sources/{suffix}.pdf",
        text_object_hash=(f"text-{suffix}" + "0" * 128)[:64],
        parser_name="verifier-parser",
        parser_version="1",
        versioned_metadata=metadata or {"page_count": 20},
        idempotency_key=f"version-{suffix}",
        as_of=NOW,
    )
    return source, version


def test_exact_source_grade_matrix() -> None:
    assert services.SOURCE_TYPE_ALLOWED_GRADES == EXACT_MATRIX


def test_fingerprint_is_exact_contract_projection() -> None:
    payload = {
        "content_hash": "a" * 64,
        "media_type": "application/pdf",
        "source_grade": "S",
        "published_at": "2026-09-15T08:00:00+08:00",
        "source_version_label": "v1",
        "source_revision_id": "r1",
        "document_language": "zh-CN",
        "parser_name": "parser",
        "parser_version": "1",
        "text_object_hash": "b" * 64,
        "source_status": "ACTIVE",
        "source_status_changed_at": None,
        "source_status_reason": None,
        "source_status_actor": None,
        "versioned_metadata": {"z": 1, "a": {"y": 2, "x": 1}},
        "source_document_id": "must-be-excluded",
        "observed_at": NOW,
        "fetched_at": NOW,
        "object_key": "must-be-excluded",
        "text_object_key": "must-be-excluded",
        "idempotency_key": "must-be-excluded",
        "version_reason": "must-be-excluded",
    }
    exact = {name: payload.get(name) for name in services.SOURCE_VERSION_FINGERPRINT_FIELDS}
    exact["published_at"] = datetime(2026, 9, 15, tzinfo=UTC)
    assert services.source_version_fingerprint(payload) == services.stable_hash(exact)


@pytest.mark.asyncio
async def test_web_anchor_optional_fields_are_really_optional(db: AsyncSession) -> None:
    source, source_version = await make_source(db, "web-anchor", "WEB_PAGE", "D")
    created = await services.create_evidence_series_version(
        db,
        scope_type="MARKET",
        scope_key="CN_A_SHARE",
        information_type="FACT",
        claim_key="verifier:web-anchor",
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title="Web anchor",
        display_text="Web anchor",
        as_of=NOW,
        locators=[services.SourceLocatorInput(
            locator_type="WEB_ANCHOR",
            raw_locator="https://example.test/report",
            short_citation="report",
            locator_payload={"canonical_url": "https://example.test/report"},
        )],
        idempotency_key="valid-web-anchor",
    )
    assert created.source_locators[0].locator_payload == {
        "canonical_url": "https://example.test/report"
    }


@pytest.mark.asyncio
async def test_table_optional_coordinates_honor_parser_bounds(db: AsyncSession) -> None:
    source, source_version = await make_source(
        db,
        "table-bound",
        "FINANCIAL_REPORT",
        "S",
        {
            "page_count": 20,
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {
                "12:1": {"row_count": 5, "column_count": 4}
            },
        },
    )
    with pytest.raises(EvidenceDomainError) as error:
        await services.create_evidence_series_version(
            db,
            scope_type="MARKET",
            scope_key="CN_A_SHARE",
            information_type="FACT",
            claim_key="verifier:table-bound",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Table bound",
            display_text="Table bound",
            as_of=NOW,
            locators=[services.SourceLocatorInput(
                locator_type="TABLE",
                raw_locator="p.12 table 1 row 99",
                short_citation="table 1 row 99",
                locator_payload={"page_number": 12, "table_index": 1, "row_index": 99},
            )],
            idempotency_key="invalid-table-bound",
        )
    assert error.value.code == "EVIDENCE_INVALID_SOURCE_LOCATOR"
    assert error.value.details["locator_path"] == "locator_payload.row_index"


@pytest.mark.asyncio
async def test_table_cell_accepts_cell_ref_without_numeric_coordinates(db: AsyncSession) -> None:
    source, source_version = await make_source(db, "cell-ref", "FINANCIAL_REPORT", "S")
    created = await services.create_evidence_series_version(
        db,
        scope_type="MARKET",
        scope_key="CN_A_SHARE",
        information_type="FACT",
        claim_key="verifier:cell-ref",
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title="Cell ref",
        display_text="Cell ref",
        as_of=NOW,
        locators=[services.SourceLocatorInput(
            locator_type="TABLE_CELL",
            raw_locator="p.12 table 1 B2",
            short_citation="B2",
            locator_payload={"page_number": 12, "table_index": 1, "cell_ref": "B2"},
        )],
        idempotency_key="valid-cell-ref",
    )
    assert created.source_locators[0].locator_payload["cell_ref"] == "B2"


@pytest.mark.asyncio
async def test_missing_locator_error_has_required_exact_details(db: AsyncSession) -> None:
    source, source_version = await make_source(db, "no-locator", "FINANCIAL_REPORT", "S")
    with pytest.raises(EvidenceDomainError) as error:
        await services.create_evidence_series_version(
            db,
            scope_type="MARKET",
            scope_key="CN_A_SHARE",
            information_type="FACT",
            claim_key="verifier:no-locator",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="No locator",
            display_text="No locator",
            as_of=NOW,
            locators=[],
            idempotency_key="missing-locator",
        )
    assert error.value.code == "EVIDENCE_INVALID_SOURCE_LOCATOR"
    assert error.value.details["source_document_version_id"] == source_version.id
    assert error.value.details["locator_path"] == "locators"


def test_missing_short_citation_reports_exact_path() -> None:
    source_version = SourceDocumentVersion(
        id="33333333-3333-4333-8333-333333333333",
        versioned_metadata={"page_count": 20},
    )
    with pytest.raises(EvidenceDomainError) as error:
        services._validate_locator(
            source_version,
            services.SourceLocatorInput(
                locator_type="PAGE",
                raw_locator="p.12",
                short_citation="",
                locator_payload={"page_number": 12},
            ),
        )
    assert error.value.details["locator_path"] == "short_citation"


async def _tracked_counts(db: AsyncSession) -> dict[type, int | None]:
    return {
        model: await db.scalar(select(func.count()).select_from(model))
        for model in (
            EvidenceSeries,
            EvidenceVersion,
            EvidenceSourceLocator,
            EvidenceIdempotencyRecord,
            EvidenceAuditEvent,
        )
    }


@pytest.mark.asyncio
async def test_web_anchor_whitespace_canonical_url_is_invalid_without_residue(
    db: AsyncSession,
) -> None:
    source, source_version = await make_source(db, "web-whitespace", "WEB_PAGE", "D")
    before = await _tracked_counts(db)
    with pytest.raises(EvidenceDomainError) as error:
        await services.create_evidence_series_version(
            db,
            scope_type="MARKET",
            scope_key="CN_A_SHARE",
            information_type="FACT",
            claim_key="verifier:web-whitespace",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Whitespace URL",
            display_text="Whitespace URL",
            as_of=NOW,
            locators=[services.SourceLocatorInput(
                locator_type="WEB_ANCHOR",
                raw_locator="web",
                short_citation="web",
                locator_payload={"canonical_url": "   "},
            )],
            idempotency_key="invalid-web-whitespace",
        )
    assert error.value.code == "EVIDENCE_INVALID_SOURCE_LOCATOR"
    assert error.value.details["locator_path"] == "locator_payload.canonical_url"
    assert await _tracked_counts(db) == before


@pytest.mark.asyncio
async def test_table_cell_ref_does_not_allow_partial_numeric_coordinates(
    db: AsyncSession,
) -> None:
    source, source_version = await make_source(
        db,
        "cell-ref-partial",
        "FINANCIAL_REPORT",
        "S",
        {
            "page_count": 20,
            "table_count_by_page": {"12": 2},
            "table_shape_by_page_index": {
                "12:1": {"row_count": 5, "column_count": 4}
            },
        },
    )
    before = await _tracked_counts(db)
    with pytest.raises(EvidenceDomainError) as error:
        await services.create_evidence_series_version(
            db,
            scope_type="MARKET",
            scope_key="CN_A_SHARE",
            information_type="FACT",
            claim_key="verifier:cell-ref-partial",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Partial coordinates",
            display_text="Partial coordinates",
            as_of=NOW,
            locators=[services.SourceLocatorInput(
                locator_type="TABLE_CELL",
                raw_locator="B2 row 2",
                short_citation="B2",
                locator_payload={
                    "page_number": 12,
                    "table_index": 1,
                    "cell_ref": "B2",
                    "row_index": 2,
                },
            )],
            idempotency_key="invalid-cell-ref-partial",
        )
    assert error.value.code == "EVIDENCE_INVALID_SOURCE_LOCATOR"
    assert error.value.details["locator_path"] == "locator_payload.column_index"
    assert await _tracked_counts(db) == before


@pytest.mark.asyncio
async def test_same_bytes_grade_reclassification_appends(db: AsyncSession) -> None:
    source, first = await make_source(db, "grade", "INSTITUTIONAL_SURVEY", "B")
    second = await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=1,
        version_reason="GRADE_RECLASSIFICATION",
        source_grade="C",
        published_at=NOW,
        observed_at=NOW,
        fetched_at=NOW,
        content_hash=first.content_hash,
        source_version_label="v1",
        media_type="application/pdf",
        object_key=first.object_key,
        text_object_hash=first.text_object_hash,
        parser_name="verifier-parser",
        parser_version="1",
        versioned_metadata={"page_count": 20},
        idempotency_key="grade-v2",
        as_of=NOW,
    )
    await db.flush()
    count = await db.scalar(
        select(func.count()).select_from(SourceDocumentVersion).where(
            SourceDocumentVersion.source_document_id == source.id
        )
    )
    assert second.version == 2
    assert second.content_hash == first.content_hash
    assert second.object_key == first.object_key
    assert second.version_fingerprint != first.version_fingerprint
    assert count == 2


@pytest.mark.asyncio
async def test_new_key_reobserves_old_fingerprint_without_new_version(db: AsyncSession) -> None:
    source, first = await make_source(db, "reobserve", "COMPANY_ANNOUNCEMENT", "S")
    audit_before = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))
    replay = await services.append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=1,
        version_reason="NEW_CONTENT",
        source_grade="S",
        published_at=NOW,
        observed_at=datetime(2026, 9, 16, tzinfo=UTC),
        fetched_at=datetime(2026, 9, 16, tzinfo=UTC),
        content_hash=first.content_hash,
        source_version_label="v1",
        media_type="application/pdf",
        object_key="sources/reobserved-object.pdf",
        text_object_hash=first.text_object_hash,
        parser_name="verifier-parser",
        parser_version="1",
        versioned_metadata={"page_count": 20},
        idempotency_key="reobserve-new-key",
        as_of=datetime(2026, 9, 16, tzinfo=UTC),
    )
    await db.flush()
    versions = await db.scalar(
        select(func.count()).select_from(SourceDocumentVersion).where(
            SourceDocumentVersion.source_document_id == source.id
        )
    )
    idempotency = await db.scalar(
        select(func.count()).select_from(EvidenceIdempotencyRecord).where(
            EvidenceIdempotencyRecord.response_ref_id == first.id
        )
    )
    audit_after = await db.scalar(select(func.count()).select_from(EvidenceAuditEvent))
    assert replay.id == first.id
    assert versions == 1
    assert idempotency == 2
    assert audit_before is not None and audit_after == audit_before + 1


@pytest.mark.asyncio
async def test_page_number_locator_and_legacy_rollback(db: AsyncSession) -> None:
    source, source_version = await make_source(db, "locator", "FINANCIAL_REPORT", "S")
    created = await services.create_evidence_series_version(
        db,
        scope_type="MARKET",
        scope_key="CN_A_SHARE",
        information_type="FACT",
        claim_key="verifier:page-number",
        provenance_kind="SOURCE_BACKED",
        primary_source_document_id=source.id,
        source_document_version_id=source_version.id,
        display_title="Verifier locator",
        display_text="Verifier locator",
        as_of=NOW,
        locators=[services.SourceLocatorInput(
            locator_type="PAGE",
            raw_locator="p.12",
            short_citation="p.12",
            locator_payload={"page_number": 12},
        )],
        idempotency_key="valid-page-number",
    )
    assert created.source_locators[0].locator_payload == {"page_number": 12}
    before = {
        model: await db.scalar(select(func.count()).select_from(model))
        for model in (
            EvidenceSeries,
            EvidenceVersion,
            EvidenceSourceLocator,
            EvidenceIdempotencyRecord,
            EvidenceAuditEvent,
        )
    }
    with pytest.raises(EvidenceDomainError) as error:
        await services.create_evidence_series_version(
            db,
            scope_type="MARKET",
            scope_key="CN_A_SHARE",
            information_type="FACT",
            claim_key="verifier:legacy-page",
            provenance_kind="SOURCE_BACKED",
            primary_source_document_id=source.id,
            source_document_version_id=source_version.id,
            display_title="Legacy locator",
            display_text="Legacy locator",
            as_of=NOW,
            locators=[services.SourceLocatorInput(
                locator_type="PAGE",
                raw_locator="p.12",
                short_citation="p.12",
                locator_payload={"page": 12},
            )],
            idempotency_key="legacy-page",
        )
    assert error.value.code == "EVIDENCE_INVALID_SOURCE_LOCATOR"
    assert error.value.details == {
        "source_document_version_id": source_version.id,
        "locator_path": "locator_payload.page_number",
    }
    after = {
        model: await db.scalar(select(func.count()).select_from(model))
        for model in before
    }
    assert after == before
