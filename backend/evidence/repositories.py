"""Minimal async query helpers for Evidence persistence."""

from __future__ import annotations

from typing import Any

from backend.evidence.models import (
    EvidenceCorroborationLink,
    EvidenceDerivationLink,
    EvidenceInstrumentLink,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


def _evidence_version_load_options() -> tuple[Any, ...]:
    return (
        selectinload(EvidenceVersion.source_locators).selectinload(
            EvidenceSourceLocator.source_document_version
        ),
        selectinload(EvidenceVersion.instrument_links).selectinload(
            EvidenceInstrumentLink.instrument
        ),
        selectinload(EvidenceVersion.left_corroboration_links).selectinload(
            EvidenceCorroborationLink.right_evidence_version
        ),
        selectinload(EvidenceVersion.right_corroboration_links).selectinload(
            EvidenceCorroborationLink.left_evidence_version
        ),
        selectinload(EvidenceVersion.derived_links).selectinload(
            EvidenceDerivationLink.supporting_evidence_version
        ),
        selectinload(EvidenceVersion.supporting_derivation_links).selectinload(
            EvidenceDerivationLink.derived_evidence_version
        ),
        selectinload(EvidenceVersion.source_document_version),
        selectinload(EvidenceVersion.supersedes_evidence_version),
    )


async def get_source_document(
    db: AsyncSession,
    source_document_id: str,
) -> SourceDocument | None:
    """Return a SourceDocument by exact ID."""
    return await db.get(SourceDocument, source_document_id)


async def get_source_document_by_external_identity(
    db: AsyncSession,
    publisher_key: str,
    source_type: str,
    external_document_id: str,
) -> SourceDocument | None:
    """Return a SourceDocument by stable publisher/type/external identity."""
    result = await db.execute(
        select(SourceDocument).where(
            SourceDocument.publisher_key == publisher_key,
            SourceDocument.source_type == source_type,
            SourceDocument.external_document_id == external_document_id,
        )
    )
    return result.scalar_one_or_none()


async def get_source_document_by_canonical_url_identity(
    db: AsyncSession,
    publisher_key: str,
    source_type: str,
    canonical_url: str,
) -> SourceDocument | None:
    """Return a fallback URL identity only when no external ID exists."""
    result = await db.execute(
        select(SourceDocument).where(
            SourceDocument.publisher_key == publisher_key,
            SourceDocument.source_type == source_type,
            SourceDocument.external_document_id.is_(None),
            SourceDocument.canonical_url == canonical_url,
        )
    )
    return result.scalar_one_or_none()


async def get_source_document_version(
    db: AsyncSession,
    source_document_version_id: str,
) -> SourceDocumentVersion | None:
    """Return a SourceDocumentVersion by exact ID."""
    return await db.get(SourceDocumentVersion, source_document_version_id)


async def get_source_document_version_by_fingerprint(
    db: AsyncSession,
    source_document_id: str,
    version_fingerprint: str,
) -> SourceDocumentVersion | None:
    """Return a SourceDocumentVersion by source identity and version fingerprint."""
    result = await db.execute(
        select(SourceDocumentVersion).where(
            SourceDocumentVersion.source_document_id == source_document_id,
            SourceDocumentVersion.version_fingerprint == version_fingerprint,
        )
    )
    return result.scalar_one_or_none()


async def get_latest_source_document_version(
    db: AsyncSession,
    source_document_id: str,
) -> SourceDocumentVersion | None:
    """Return the highest SourceDocumentVersion for a source identity."""
    result = await db.execute(
        select(SourceDocumentVersion)
        .where(SourceDocumentVersion.source_document_id == source_document_id)
        .order_by(SourceDocumentVersion.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_evidence_series_by_identity_hash(
    db: AsyncSession,
    series_identity_hash: str,
) -> EvidenceSeries | None:
    """Return an EvidenceSeries by canonical identity hash."""
    result = await db.execute(
        select(EvidenceSeries).where(EvidenceSeries.series_identity_hash == series_identity_hash)
    )
    return result.scalar_one_or_none()


async def get_exact_evidence_version(
    db: AsyncSession,
    evidence_version_id: str,
) -> EvidenceVersion | None:
    """Return one immutable EvidenceVersion with its query-time child rows."""
    result = await db.execute(
        select(EvidenceVersion)
        .options(*_evidence_version_load_options())
        .where(EvidenceVersion.id == evidence_version_id)
    )
    return result.scalar_one_or_none()


async def get_current_evidence(
    db: AsyncSession,
    evidence_series_id: str,
) -> EvidenceVersion | None:
    """Return the highest EvidenceVersion for one EvidenceSeries."""
    result = await db.execute(
        select(EvidenceVersion)
        .options(*_evidence_version_load_options())
        .where(EvidenceVersion.evidence_series_id == evidence_series_id)
        .order_by(EvidenceVersion.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_evidence_history(
    db: AsyncSession,
    evidence_series_id: str,
) -> list[EvidenceVersion]:
    """Return all versions for one EvidenceSeries in ascending version order."""
    result = await db.execute(
        select(EvidenceVersion)
        .options(*_evidence_version_load_options())
        .where(EvidenceVersion.evidence_series_id == evidence_series_id)
        .order_by(EvidenceVersion.version.asc())
    )
    return list(result.scalars().all())


async def list_evidence_by_source_document_version(
    db: AsyncSession,
    source_document_version_id: str,
) -> list[EvidenceVersion]:
    """Return EvidenceVersions extracted from one exact SourceDocumentVersion."""
    result = await db.execute(
        select(EvidenceVersion)
        .options(*_evidence_version_load_options())
        .where(EvidenceVersion.source_document_version_id == source_document_version_id)
        .order_by(EvidenceVersion.created_at.asc(), EvidenceVersion.id.asc())
    )
    return list(result.scalars().all())
