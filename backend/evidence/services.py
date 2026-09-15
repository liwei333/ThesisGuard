"""Evidence Domain Service commands and deterministic helpers.

WP-04-02 sits above the WP-04-01 ORM/repository layer and below any future API,
worker, parser, MinIO, embedding, RAG, Research typed-link, Thesis, or Agent
integration. Commands insert immutable rows and never commit the caller's
transaction.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from backend.evidence.errors import (
    EvidenceDomainError,
    EvidenceIdempotencyConflict,
    EvidenceInvalidCorroborationLink,
    EvidenceInvalidDerivationLink,
    EvidenceInvalidProvenance,
    EvidenceInvalidSourceGrade,
    EvidenceInvalidSourceLocator,
    EvidenceInvalidSourceType,
    EvidenceInvalidStateTransition,
    EvidencePersistenceConflict,
    EvidenceSourceDocumentNotFound,
    EvidenceSourceVersionNotFound,
    EvidenceValidationError,
    EvidenceVersionConflict,
    EvidenceVersionNotFound,
)
from backend.evidence.models import (
    ACTORS,
    CORROBORATION_RELATION_TYPES,
    DERIVATION_LINK_ROLES,
    INFORMATION_TYPES,
    INSTRUMENT_LINK_ROLES,
    LOCATOR_TYPES,
    PROVENANCE_KINDS,
    SCOPE_TYPES,
    SOURCE_GRADES,
    SOURCE_STATUS_ACTORS,
    SOURCE_STATUSES,
    SOURCE_TYPES,
    SOURCE_VERSION_REASONS,
    EvidenceAuditEvent,
    EvidenceCorroborationLink,
    EvidenceDerivationLink,
    EvidenceIdempotencyRecord,
    EvidenceInstrumentLink,
    EvidenceSeries,
    EvidenceSourceLocator,
    EvidenceVersion,
    SourceDocument,
    SourceDocumentVersion,
)
from backend.evidence.repositories import (
    _evidence_version_load_options,
    get_current_evidence,
    get_evidence_series_by_identity_hash,
    get_exact_evidence_version,
    get_latest_source_document_version,
    get_source_document,
    get_source_document_by_canonical_url_identity,
    get_source_document_by_external_identity,
    get_source_document_version,
    get_source_document_version_by_fingerprint,
    list_evidence_by_source_document_version,
    list_evidence_history,
)
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "msclkid", "yclid"}
ELIGIBLE_CURRENT_STATUSES = {"UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "DISPUTED"}
SOURCE_TYPE_ALLOWED_GRADES: dict[str, set[str]] = {
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
SOURCE_VERSION_FINGERPRINT_FIELDS: tuple[str, ...] = (
    "content_hash",
    "media_type",
    "source_grade",
    "published_at",
    "source_version_label",
    "source_revision_id",
    "document_language",
    "parser_name",
    "parser_version",
    "text_object_hash",
    "source_status",
    "source_status_changed_at",
    "source_status_reason",
    "source_status_actor",
    "versioned_metadata",
)


@dataclass(frozen=True)
class SourceLocatorInput:
    """Exact source locator payload for source-backed Evidence."""

    locator_type: str
    raw_locator: str
    short_citation: str
    locator_payload: dict[str, Any]
    quote_hash: str | None = None


@dataclass(frozen=True)
class InstrumentLinkInput:
    """Instrument fan-out payload for one EvidenceVersion."""

    instrument_id: str
    role: str
    link_order: int | None = None
    link_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class DerivationLinkInput:
    """Directed derivation edge payload."""

    supporting_evidence_version_id: str
    role: str
    support_order: int | None = None
    support_weight: Decimal | None = None


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def canonicalize_url(url: str) -> str:
    """Normalize URL identity deterministically without fetching remote content."""
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    if port is not None and not (
        (scheme == "https" and port == 443) or (scheme == "http" and port == 80)
    ):
        hostname = f"{hostname}:{port}"
    path = parsed.path or "/"
    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
        and not key.lower().startswith(TRACKING_QUERY_PREFIXES)
    ]
    query = urlencode(sorted(query_items), doseq=True)
    return urlunsplit((scheme, hostname, path, query, ""))


def _canonical_value(value: Any) -> Any:
    if isinstance(value, datetime):
        normalized_timestamp = (
            value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)
        )
        return normalized_timestamp.isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, dict):
        normalized_mapping: dict[str, Any] = {}
        for key, item in value.items():
            if key == "url" and isinstance(item, str):
                normalized_mapping[key] = canonicalize_url(item)
            else:
                normalized_mapping[str(key)] = _canonical_value(item)
        return normalized_mapping
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """Serialize command payloads to stable canonical JSON."""
    return json.dumps(
        _canonical_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def stable_hash(value: Any) -> str:
    """Return a SHA-256 hash for canonical JSON payloads."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_timestamp(value: Any) -> Any:
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    return value


def source_version_fingerprint(payload: dict[str, Any]) -> str:
    """Return the frozen §8 SourceDocumentVersion identity fingerprint."""
    identity_payload = {field: payload.get(field) for field in SOURCE_VERSION_FINGERPRINT_FIELDS}
    identity_payload["published_at"] = _canonical_timestamp(identity_payload["published_at"])
    identity_payload["source_status_changed_at"] = _canonical_timestamp(
        identity_payload["source_status_changed_at"]
    )
    return stable_hash(identity_payload)


async def register_source_document(
    db: AsyncSession,
    *,
    publisher_key: str,
    publisher_name: str,
    source_type: str,
    external_document_id: str | None = None,
    canonical_url: str | None = None,
    issuer_key: str | None = None,
    issuer_name: str | None = None,
    title: str | None = None,
    document_language: str | None = None,
    created_by_actor: str,
    idempotency_key: str,
    as_of: datetime | None = None,
) -> SourceDocument:
    """Create or replay a SourceDocument identity."""
    _ensure_enum("source_type", source_type, SOURCE_TYPES, EvidenceInvalidSourceType)
    _ensure_actor(created_by_actor)
    canonical_url_value = canonicalize_url(canonical_url) if canonical_url else None
    if external_document_id is None and canonical_url_value is None:
        raise EvidenceValidationError(
            "SourceDocument requires external_document_id or canonical_url"
        )

    payload = {
        "publisher_key": publisher_key,
        "publisher_name": publisher_name,
        "source_type": source_type,
        "external_document_id": external_document_id,
        "canonical_url": canonical_url_value,
        "issuer_key": issuer_key,
        "issuer_name": issuer_name,
        "title": title,
        "document_language": document_language,
        "created_by_actor": created_by_actor,
    }
    idempotency_scope = _source_document_idempotency_scope(
        publisher_key=publisher_key,
        source_type=source_type,
        external_document_id=external_document_id,
        canonical_url=canonical_url_value,
    )
    request_hash = stable_hash(payload)
    replay = await _idempotent_replay(
        db,
        scope=idempotency_scope,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if replay is not None:
        source = await get_source_document(db, replay.response_ref_id or "")
        if source is None:
            raise EvidencePersistenceConflict(
                "SourceDocument idempotency record points to missing row"
            )
        return source

    existing = await _find_source_document(
        db,
        publisher_key=publisher_key,
        source_type=source_type,
        external_document_id=external_document_id,
        canonical_url=canonical_url_value,
    )
    if existing is not None:
        _ensure_same_source_payload(existing, payload)
        await _record_idempotency(
            db,
            scope=idempotency_scope,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_ref_type="SourceDocument",
            response_ref_id=existing.id,
            as_of=as_of,
        )
        return existing

    source = SourceDocument(
        publisher_key=publisher_key,
        publisher_name=publisher_name,
        source_type=source_type,
        external_document_id=external_document_id,
        canonical_url=canonical_url_value,
        issuer_key=issuer_key,
        issuer_name=issuer_name,
        title=title,
        document_language=document_language,
        created_by_actor=created_by_actor,
        created_at=as_of or utc_now(),
    )
    try:
        async with db.begin_nested():
            db.add(source)
            await db.flush()
            await _record_idempotency(
                db,
                scope=idempotency_scope,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_ref_type="SourceDocument",
                response_ref_id=source.id,
                as_of=as_of,
            )
            _audit(
                db,
                "SourceDocument",
                source.id,
                "SOURCE_DOCUMENT_REGISTERED",
                payload,
                created_by_actor,
                as_of,
            )
    except IntegrityError as exc:
        raise EvidencePersistenceConflict("SourceDocument write violated constraints") from exc
    return source


async def append_source_document_version(
    db: AsyncSession,
    *,
    source_document_id: str,
    expected_version: int,
    version_reason: str,
    source_grade: str,
    published_at: datetime | None,
    observed_at: datetime,
    fetched_at: datetime,
    content_hash: str,
    source_version_label: str | None,
    media_type: str,
    object_key: str,
    idempotency_key: str,
    source_revision_id: str | None = None,
    text_object_key: str | None = None,
    text_object_hash: str | None = None,
    parser_name: str | None = None,
    parser_version: str | None = None,
    versioned_metadata: dict[str, Any] | None = None,
    source_status: str = "ACTIVE",
    source_status_changed_at: datetime | None = None,
    source_status_actor: str | None = None,
    source_status_reason: str | None = None,
    as_of: datetime | None = None,
) -> SourceDocumentVersion:
    """Append immutable source content version after expected-version checks."""
    _ensure_enum("version_reason", version_reason, SOURCE_VERSION_REASONS, EvidenceValidationError)
    _ensure_enum("source_grade", source_grade, SOURCE_GRADES, EvidenceInvalidSourceGrade)
    _ensure_enum("source_status", source_status, SOURCE_STATUSES, EvidenceValidationError)
    _validate_source_lifecycle_tuple(
        source_status=source_status,
        source_status_changed_at=source_status_changed_at,
        source_status_actor=source_status_actor,
        source_status_reason=source_status_reason,
    )
    source = await _get_source_document_for_update(db, source_document_id)
    if source is None:
        raise EvidenceSourceDocumentNotFound(
            f"SourceDocument {source_document_id} not found",
            source_document_id=source_document_id,
        )
    _ensure_source_grade_allowed(source.source_type, source_grade)

    fingerprint_payload = {
        "content_hash": content_hash,
        "media_type": media_type,
        "source_grade": source_grade,
        "published_at": published_at,
        "source_version_label": source_version_label,
        "source_revision_id": source_revision_id,
        "document_language": source.document_language,
        "parser_name": parser_name,
        "parser_version": parser_version,
        "text_object_hash": text_object_hash,
        "source_status": source_status,
        "source_status_changed_at": source_status_changed_at,
        "source_status_reason": source_status_reason,
        "source_status_actor": source_status_actor,
        "versioned_metadata": versioned_metadata or {},
    }
    fingerprint = source_version_fingerprint(fingerprint_payload)
    request_payload = {
        "operation": "append_source_document_version",
        "source_document_id": source_document_id,
        "expected_version": expected_version,
        "version_reason": version_reason,
        "version_fingerprint": fingerprint,
        "observed_at": observed_at,
        "fetched_at": fetched_at,
        "object_key": object_key,
        "text_object_key": text_object_key,
        "fingerprint_payload": fingerprint_payload,
    }
    audit_payload = {
        **request_payload,
        "content_hash": content_hash,
        "media_type": media_type,
        "source_grade": source_grade,
        "published_at": published_at,
        "source_version_label": source_version_label,
        "source_revision_id": source_revision_id,
        "document_language": source.document_language,
        "parser_name": parser_name,
        "parser_version": parser_version,
        "text_object_hash": text_object_hash,
        "source_status": source_status,
        "versioned_metadata": versioned_metadata or {},
    }
    request_hash = stable_hash(request_payload)
    idempotency_scope = _source_version_idempotency_scope(source_document_id)
    replay = await _idempotent_replay(
        db,
        scope=idempotency_scope,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if replay is not None:
        version = await get_source_document_version(db, replay.response_ref_id or "")
        if version is None:
            raise EvidencePersistenceConflict(
                "SourceDocumentVersion idempotency record points to missing row"
            )
        return version

    duplicate = await get_source_document_version_by_fingerprint(
        db,
        source_document_id,
        fingerprint,
    )
    if duplicate is not None:
        await _record_source_reobservation(
            db,
            idempotency_scope=idempotency_scope,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            source_document_id=source_document_id,
            source_document_version_id=duplicate.id,
            audit_payload=audit_payload,
            as_of=as_of,
        )
        return duplicate

    current = await get_latest_source_document_version(db, source_document_id)
    current_version = current.version if current is not None else 0
    if current_version != expected_version:
        raise EvidenceVersionConflict(
            f"Expected source version {expected_version}, current version is {current_version}",
            expected_version=expected_version,
            current_version=current_version,
        )

    version = SourceDocumentVersion(
        source_document_id=source_document_id,
        version=current_version + 1,
        version_reason=version_reason,
        source_grade=source_grade,
        version_fingerprint=fingerprint,
        published_at=published_at,
        observed_at=observed_at,
        fetched_at=fetched_at,
        content_hash=content_hash,
        source_version_label=source_version_label,
        source_revision_id=source_revision_id,
        media_type=media_type,
        object_key=object_key,
        text_object_key=text_object_key,
        text_object_hash=text_object_hash,
        parser_name=parser_name,
        parser_version=parser_version,
        versioned_metadata=versioned_metadata or {},
        source_status=source_status,
        source_status_changed_at=source_status_changed_at,
        source_status_actor=source_status_actor,
        source_status_reason=source_status_reason,
        created_at=as_of or utc_now(),
    )
    try:
        async with db.begin_nested():
            db.add(version)
            await db.flush()
            await _record_idempotency(
                db,
                scope=idempotency_scope,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_ref_type="SourceDocumentVersion",
                response_ref_id=version.id,
                as_of=as_of,
            )
            _audit(
                db,
                "SourceDocument",
                source_document_id,
                "SOURCE_DOCUMENT_VERSION_APPENDED",
                audit_payload,
                "IMPORTER",
                as_of,
            )
    except IntegrityError as exc:
        duplicate = await get_source_document_version_by_fingerprint(
            db, source_document_id, fingerprint
        )
        if duplicate is not None:
            await _record_source_reobservation(
                db,
                idempotency_scope=idempotency_scope,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                source_document_id=source_document_id,
                source_document_version_id=duplicate.id,
                audit_payload=audit_payload,
                as_of=as_of,
            )
            return duplicate
        raise EvidencePersistenceConflict(
            "SourceDocumentVersion write violated constraints"
        ) from exc
    return version


async def create_evidence_series_version(
    db: AsyncSession,
    *,
    scope_type: str,
    scope_key: str,
    information_type: str,
    claim_key: str,
    provenance_kind: str,
    display_title: str,
    display_text: str,
    as_of: datetime,
    idempotency_key: str,
    metric_key: str | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    primary_source_document_id: str | None = None,
    origin_key: str | None = None,
    source_document_version_id: str | None = None,
    raw_value: str | None = None,
    raw_unit: str | None = None,
    normalized_value: Decimal | None = None,
    normalized_text_value: str | None = None,
    normalized_unit: str | None = None,
    currency: str | None = None,
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
    locators: Sequence[SourceLocatorInput] | None = None,
    instrument_links: Sequence[InstrumentLinkInput] | None = None,
    derivation_links: Sequence[DerivationLinkInput] | None = None,
    corroborates_evidence_version_ids: Sequence[str] | None = None,
    extractor_name: str | None = None,
    extractor_version: str | None = None,
    prompt_template_version: str | None = None,
    manual_entry_reason: str | None = None,
    manual_observed_at: datetime | None = None,
    verification_status: str = "UNREVIEWED",
    status_changed_at: datetime | None = None,
    status_changed_by_actor: str | None = None,
    status_change_kind: str | None = None,
    status_reason: str | None = None,
    trusted_correction_rule: str | None = None,
    created_by_actor: str = "IMPORTER",
    created_at: datetime | None = None,
    supersedes_evidence_version_id: str | None = None,
) -> EvidenceVersion:
    """Create an EvidenceSeries if needed and insert immutable version 1."""
    _validate_identity_enums(scope_type, information_type, provenance_kind)
    _ensure_actor(created_by_actor)
    source_version = await _validate_provenance(
        db,
        information_type=information_type,
        provenance_kind=provenance_kind,
        primary_source_document_id=primary_source_document_id,
        origin_key=origin_key,
        source_document_version_id=source_document_version_id,
        manual_entry_reason=manual_entry_reason,
        manual_observed_at=manual_observed_at,
        locators=locators or (),
    )
    await _validate_instrument_links(db, scope_type, scope_key, instrument_links or ())
    if derivation_links:
        await _validate_derivation_links(db, derivation_links)
    series_hash = _series_identity_hash(
        scope_type=scope_type,
        scope_key=scope_key,
        information_type=information_type,
        claim_key=claim_key,
        metric_key=metric_key,
        period_start=period_start,
        period_end=period_end,
        provenance_kind=provenance_kind,
        primary_source_document_id=primary_source_document_id,
        origin_key=origin_key,
    )
    payload = {
        "series_hash": series_hash,
        "source_document_version_id": source_document_version_id,
        "display_title": display_title,
        "display_text": display_text,
        "raw_value": raw_value,
        "normalized_value": normalized_value,
        "as_of": as_of,
        "locators": [locator.__dict__ for locator in (locators or ())],
        "instrument_links": [link.__dict__ for link in (instrument_links or ())],
        "derivation_links": [link.__dict__ for link in (derivation_links or ())],
        "verification_status": verification_status,
    }
    request_hash = stable_hash(payload)
    replay = await _idempotent_replay(
        db,
        scope="create_evidence_series_version",
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if replay is not None:
        existing = await get_exact_evidence_version(db, replay.response_ref_id or "")
        if existing is None:
            raise EvidencePersistenceConflict(
                "EvidenceVersion idempotency record points to missing row"
            )
        return existing

    series = await get_evidence_series_by_identity_hash(db, series_hash)
    if series is None:
        series = EvidenceSeries(
            id=uuid_str(),
            scope_type=scope_type,
            scope_key=scope_key,
            information_type=information_type,
            claim_key=claim_key,
            metric_key=metric_key,
            period_start=period_start,
            period_end=period_end,
            provenance_kind=provenance_kind,
            primary_source_document_id=primary_source_document_id,
            origin_key=origin_key,
            series_identity_hash=series_hash,
            created_at=created_at or utc_now(),
            created_by_actor=created_by_actor,
        )
    else:
        current = await get_current_evidence(db, series.id)
        if current is not None:
            raise EvidencePersistenceConflict("EvidenceSeries already has an initial version")

    source_grade_snapshot = source_version.source_grade if source_version is not None else None
    version = EvidenceVersion(
        evidence_series_id=series.id,
        version=1,
        source_document_version_id=source_document_version_id
        if provenance_kind == "SOURCE_BACKED"
        else None,
        information_type=information_type,
        provenance_kind=provenance_kind,
        source_grade_snapshot=source_grade_snapshot,
        verification_status=verification_status,
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_change_kind=status_change_kind,
        status_reason=status_reason,
        display_title=display_title,
        display_text=display_text,
        claim_key=claim_key,
        metric_key=metric_key,
        raw_value=raw_value,
        raw_unit=raw_unit,
        normalized_value=normalized_value,
        normalized_text_value=normalized_text_value,
        normalized_unit=normalized_unit,
        currency=currency,
        period_start=period_start,
        period_end=period_end,
        as_of=as_of,
        effective_from=effective_from,
        effective_to=effective_to,
        supersedes_evidence_version_id=supersedes_evidence_version_id,
        created_at=created_at or utc_now(),
        created_by_actor=created_by_actor,
        extractor_name=extractor_name,
        extractor_version=extractor_version,
        prompt_template_version=prompt_template_version,
        manual_entry_reason=manual_entry_reason,
        manual_observed_at=manual_observed_at,
        trusted_correction_rule=trusted_correction_rule,
    )
    _attach_children(
        version,
        source_document_version_id,
        locators or (),
        instrument_links or (),
        derivation_links or (),
    )
    try:
        async with db.begin_nested():
            db.add(series)
            db.add(version)
            await db.flush()
            await _create_corroboration_links(
                db,
                version.id,
                corroborates_evidence_version_ids or (),
                created_by_actor,
                created_at,
            )
            await _record_idempotency(
                db,
                scope="create_evidence_series_version",
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_ref_type="EvidenceVersion",
                response_ref_id=version.id,
                as_of=created_at,
            )
            _audit(
                db,
                "EvidenceSeries",
                series.id,
                "EVIDENCE_SERIES_CREATED",
                {"series_hash": series_hash},
                created_by_actor,
                created_at,
            )
            _audit(
                db,
                "EvidenceVersion",
                version.id,
                "EVIDENCE_VERSION_CREATED",
                payload,
                created_by_actor,
                created_at,
            )
    except IntegrityError as exc:
        raise EvidencePersistenceConflict("EvidenceVersion write violated constraints") from exc
    loaded = await get_exact_evidence_version(db, version.id)
    if loaded is None:
        raise EvidencePersistenceConflict("EvidenceVersion was not persisted")
    return loaded


async def revise_correct_evidence(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    status_changed_at: datetime,
    status_changed_by_actor: str,
    status_reason: str,
    idempotency_key: str,
    display_title: str | None = None,
    display_text: str | None = None,
    raw_value: str | None = None,
    raw_unit: str | None = None,
    normalized_value: Decimal | None = None,
    normalized_text_value: str | None = None,
    normalized_unit: str | None = None,
    currency: str | None = None,
    as_of: datetime | None = None,
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
    trusted_correction_rule: str | None = None,
) -> EvidenceVersion:
    """Append a same-identity correction as EvidenceVersion N+1."""
    current = await _get_current_evidence_for_update(db, evidence_series_id)
    if current is None:
        raise EvidenceVersionNotFound(f"No EvidenceVersion exists for series {evidence_series_id}")
    _ensure_expected_version(current, expected_version)
    payload = {
        "evidence_series_id": evidence_series_id,
        "expected_version": expected_version,
        "display_title": display_title,
        "display_text": display_text,
        "raw_value": raw_value,
        "normalized_value": normalized_value,
        "status_changed_at": status_changed_at,
        "status_changed_by_actor": status_changed_by_actor,
        "status_reason": status_reason,
    }
    return await _append_status_or_revision(
        db,
        current=current,
        payload=payload,
        idempotency_scope="revise_correct_evidence",
        idempotency_key=idempotency_key,
        verification_status="VERIFIED" if trusted_correction_rule else "UNREVIEWED",
        status_change_kind="CORRECTION",
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_reason=status_reason,
        overrides={
            "display_title": display_title,
            "display_text": display_text,
            "raw_value": raw_value,
            "raw_unit": raw_unit,
            "normalized_value": normalized_value,
            "normalized_text_value": normalized_text_value,
            "normalized_unit": normalized_unit,
            "currency": currency,
            "as_of": as_of,
            "effective_from": effective_from,
            "effective_to": effective_to,
            "trusted_correction_rule": trusted_correction_rule,
        },
    )


async def request_review(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    reason: str,
    actor: str,
    idempotency_key: str,
    as_of: datetime | None = None,
) -> EvidenceVersion:
    """Append a PENDING_REVIEW status version."""
    return await _status_command(
        db,
        evidence_series_id=evidence_series_id,
        expected_version=expected_version,
        target_status="PENDING_REVIEW",
        status_change_kind="REVIEW_REQUEST",
        allowed_from={"UNREVIEWED"},
        reason=reason,
        actor=actor,
        idempotency_scope="request_review",
        idempotency_key=idempotency_key,
        as_of=as_of,
    )


async def verify_or_reject(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    decision: str,
    reason: str,
    actor: str,
    idempotency_key: str,
    as_of: datetime | None = None,
) -> EvidenceVersion:
    """Append a VERIFIED or REJECTED review decision."""
    if decision not in {"VERIFIED", "REJECTED"}:
        raise EvidenceValidationError("decision must be VERIFIED or REJECTED")
    return await _status_command(
        db,
        evidence_series_id=evidence_series_id,
        expected_version=expected_version,
        target_status=decision,
        status_change_kind="REVIEW_DECISION",
        allowed_from={"PENDING_REVIEW", "DISPUTED"},
        reason=reason,
        actor=actor,
        idempotency_scope="verify_or_reject",
        idempotency_key=idempotency_key,
        as_of=as_of,
    )


async def mark_disputed(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    reason: str,
    actor: str,
    idempotency_key: str,
    as_of: datetime | None = None,
) -> EvidenceVersion:
    """Append a DISPUTED status version."""
    return await _status_command(
        db,
        evidence_series_id=evidence_series_id,
        expected_version=expected_version,
        target_status="DISPUTED",
        status_change_kind="DISPUTE",
        allowed_from={"VERIFIED", "REJECTED", "PENDING_REVIEW"},
        reason=reason,
        actor=actor,
        idempotency_scope="mark_disputed",
        idempotency_key=idempotency_key,
        as_of=as_of,
    )


async def retract_or_invalidate(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    target_status: str,
    reason: str,
    actor: str,
    idempotency_key: str,
    as_of: datetime | None = None,
) -> EvidenceVersion:
    """Append a RETRACTED or INVALIDATED tombstone snapshot."""
    if target_status not in {"RETRACTED", "INVALIDATED"}:
        raise EvidenceValidationError("target_status must be RETRACTED or INVALIDATED")
    return await _status_command(
        db,
        evidence_series_id=evidence_series_id,
        expected_version=expected_version,
        target_status=target_status,
        status_change_kind="RETRACTION" if target_status == "RETRACTED" else "INVALIDATION",
        allowed_from={"UNREVIEWED", "PENDING_REVIEW", "VERIFIED", "REJECTED", "DISPUTED"},
        reason=reason,
        actor=actor,
        idempotency_scope="retract_or_invalidate",
        idempotency_key=idempotency_key,
        as_of=as_of,
    )


async def create_replacement_evidence_series(
    db: AsyncSession,
    *,
    prior_evidence_version_id: str,
    scope_type: str,
    scope_key: str,
    information_type: str,
    claim_key: str,
    provenance_kind: str,
    display_title: str,
    display_text: str,
    as_of: datetime,
    status_changed_at: datetime,
    status_changed_by_actor: str,
    status_reason: str,
    idempotency_key: str,
    metric_key: str | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    primary_source_document_id: str | None = None,
    origin_key: str | None = None,
    source_document_version_id: str | None = None,
    raw_value: str | None = None,
    raw_unit: str | None = None,
    normalized_value: Decimal | None = None,
    normalized_text_value: str | None = None,
    normalized_unit: str | None = None,
    currency: str | None = None,
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
    locators: Sequence[SourceLocatorInput] | None = None,
    instrument_links: Sequence[InstrumentLinkInput] | None = None,
    trusted_correction_rule: str | None = None,
    created_by_actor: str = "IMPORTER",
) -> EvidenceVersion:
    """Create a replacement series for identity-changing correction."""
    prior = await get_exact_evidence_version(db, prior_evidence_version_id)
    if prior is None:
        raise EvidenceVersionNotFound(
            f"EvidenceVersion {prior_evidence_version_id} not found",
            evidence_version_id=prior_evidence_version_id,
        )
    prior_series = await db.get(EvidenceSeries, prior.evidence_series_id)
    if prior_series is None:
        raise EvidencePersistenceConflict("Prior EvidenceVersion points to missing series")
    new_identity = _series_identity_hash(
        scope_type=scope_type,
        scope_key=scope_key,
        information_type=information_type,
        claim_key=claim_key,
        metric_key=metric_key,
        period_start=period_start,
        period_end=period_end,
        provenance_kind=provenance_kind,
        primary_source_document_id=primary_source_document_id,
        origin_key=origin_key,
    )
    if new_identity == prior_series.series_identity_hash:
        raise EvidenceValidationError("Replacement must change at least one identity dimension")

    payload = {
        "prior_evidence_version_id": prior_evidence_version_id,
        "new_identity": new_identity,
        "display_title": display_title,
        "display_text": display_text,
        "status_changed_at": status_changed_at,
        "status_changed_by_actor": status_changed_by_actor,
        "status_reason": status_reason,
    }
    request_hash = stable_hash(payload)
    replay = await _idempotent_replay(
        db,
        scope="create_replacement_evidence_series",
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if replay is not None:
        existing = await get_exact_evidence_version(db, replay.response_ref_id or "")
        if existing is None:
            raise EvidencePersistenceConflict(
                "Replacement idempotency record points to missing row"
            )
        return existing

    created = await create_evidence_series_version(
        db,
        scope_type=scope_type,
        scope_key=scope_key,
        information_type=information_type,
        claim_key=claim_key,
        metric_key=metric_key,
        period_start=period_start,
        period_end=period_end,
        provenance_kind=provenance_kind,
        primary_source_document_id=primary_source_document_id,
        origin_key=origin_key,
        source_document_version_id=source_document_version_id,
        display_title=display_title,
        display_text=display_text,
        raw_value=raw_value,
        raw_unit=raw_unit,
        normalized_value=normalized_value,
        normalized_text_value=normalized_text_value,
        normalized_unit=normalized_unit,
        currency=currency,
        as_of=as_of,
        effective_from=effective_from,
        effective_to=effective_to,
        locators=locators,
        instrument_links=instrument_links,
        verification_status="VERIFIED" if trusted_correction_rule else "UNREVIEWED",
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_change_kind="CORRECTION",
        status_reason=status_reason,
        trusted_correction_rule=trusted_correction_rule,
        created_by_actor=created_by_actor,
        idempotency_key=f"{idempotency_key}:inner",
        created_at=status_changed_at,
        supersedes_evidence_version_id=prior_evidence_version_id,
    )
    try:
        async with db.begin_nested():
            await db.flush()
            await _record_idempotency(
                db,
                scope="create_replacement_evidence_series",
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_ref_type="EvidenceVersion",
                response_ref_id=created.id,
                as_of=status_changed_at,
            )
    except IntegrityError as exc:
        raise EvidencePersistenceConflict(
            "Replacement EvidenceVersion write violated constraints"
        ) from exc
    loaded = await get_exact_evidence_version(db, created.id)
    if loaded is None:
        raise EvidencePersistenceConflict("Replacement EvidenceVersion was not persisted")
    return loaded


async def create_corroboration_link(
    db: AsyncSession,
    *,
    left_evidence_version_id: str,
    right_evidence_version_id: str,
    relation_type: str,
    created_by_actor: str,
    created_at: datetime | None = None,
) -> EvidenceCorroborationLink:
    """Create a symmetric corroboration/conflict link between exact versions."""
    _ensure_actor(created_by_actor)
    if relation_type not in CORROBORATION_RELATION_TYPES:
        raise EvidenceInvalidCorroborationLink("Unknown corroboration relation type")
    if left_evidence_version_id == right_evidence_version_id:
        raise EvidenceInvalidCorroborationLink("Evidence cannot corroborate itself")
    left = await get_exact_evidence_version(db, left_evidence_version_id)
    right = await get_exact_evidence_version(db, right_evidence_version_id)
    if left is None or right is None:
        raise EvidenceInvalidCorroborationLink("Both EvidenceVersions must exist")
    left_id, right_id = sorted((left_evidence_version_id, right_evidence_version_id))
    link = EvidenceCorroborationLink(
        left_evidence_version_id=left_id,
        right_evidence_version_id=right_id,
        relation_type=relation_type,
        created_at=created_at or utc_now(),
        created_by_actor=created_by_actor,
    )
    try:
        async with db.begin_nested():
            db.add(link)
            await db.flush()
    except IntegrityError as exc:
        raise EvidenceInvalidCorroborationLink(
            "Corroboration link is duplicate or invalid"
        ) from exc
    return link


async def get_current_valid_evidence(
    db: AsyncSession,
    evidence_series_id: str,
) -> EvidenceVersion | None:
    """Return current only if latest version is eligible; never fall back."""
    current = await get_current_evidence(db, evidence_series_id)
    if current is None or current.verification_status not in ELIGIBLE_CURRENT_STATUSES:
        return None
    if (
        current.source_document_version is not None
        and current.source_document_version.source_status == "RETRACTED"
    ):
        return None
    return current


async def list_evidence_by_instrument(
    db: AsyncSession,
    instrument_id: str,
) -> list[EvidenceVersion]:
    """Return current EvidenceVersions linked to an instrument."""
    result = await db.execute(
        select(EvidenceVersion)
        .options(*_evidence_version_load_options())
        .join(EvidenceInstrumentLink)
        .where(EvidenceInstrumentLink.instrument_id == instrument_id)
        .order_by(EvidenceVersion.created_at.asc(), EvidenceVersion.id.asc())
    )
    rows = list(result.scalars().unique().all())
    current_ids: set[str] = set()
    for evidence in rows:
        current = await get_current_evidence(db, evidence.evidence_series_id)
        if current is not None:
            current_ids.add(current.id)
    return [row for row in rows if row.id in current_ids]


async def _status_command(
    db: AsyncSession,
    *,
    evidence_series_id: str,
    expected_version: int,
    target_status: str,
    status_change_kind: str,
    allowed_from: set[str],
    reason: str,
    actor: str,
    idempotency_scope: str,
    idempotency_key: str,
    as_of: datetime | None,
) -> EvidenceVersion:
    _ensure_actor(actor)
    current = await _get_current_evidence_for_update(db, evidence_series_id)
    if current is None:
        raise EvidenceVersionNotFound(f"No EvidenceVersion exists for series {evidence_series_id}")
    payload = {
        "evidence_series_id": evidence_series_id,
        "expected_version": expected_version,
        "target_status": target_status,
        "reason": reason,
        "actor": actor,
    }
    replay = await _idempotent_replay(
        db,
        scope=idempotency_scope,
        idempotency_key=idempotency_key,
        request_hash=stable_hash(payload),
    )
    if replay is not None:
        existing = await get_exact_evidence_version(db, replay.response_ref_id or "")
        if existing is None:
            raise EvidencePersistenceConflict("Status idempotency record points to missing row")
        return existing
    _ensure_expected_version(current, expected_version)
    if current.verification_status not in allowed_from:
        raise EvidenceInvalidStateTransition(
            f"Cannot move EvidenceVersion from {current.verification_status} to {target_status}",
            from_status=current.verification_status,
            requested_status=target_status,
        )
    return await _append_status_or_revision(
        db,
        current=current,
        payload=payload,
        idempotency_scope=idempotency_scope,
        idempotency_key=idempotency_key,
        verification_status=target_status,
        status_change_kind=status_change_kind,
        status_changed_at=as_of or utc_now(),
        status_changed_by_actor=actor,
        status_reason=reason,
        overrides={},
    )


async def _append_status_or_revision(
    db: AsyncSession,
    *,
    current: EvidenceVersion,
    payload: dict[str, Any],
    idempotency_scope: str,
    idempotency_key: str,
    verification_status: str,
    status_change_kind: str,
    status_changed_at: datetime,
    status_changed_by_actor: str,
    status_reason: str,
    overrides: dict[str, Any],
) -> EvidenceVersion:
    request_hash = stable_hash(payload)
    replay = await _idempotent_replay(
        db,
        scope=idempotency_scope,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
    )
    if replay is not None:
        existing = await get_exact_evidence_version(db, replay.response_ref_id or "")
        if existing is None:
            raise EvidencePersistenceConflict("Evidence idempotency record points to missing row")
        return existing
    child_locators = [
        SourceLocatorInput(
            locator_type=locator.locator_type,
            raw_locator=locator.raw_locator,
            short_citation=locator.short_citation,
            locator_payload=dict(locator.locator_payload),
            quote_hash=locator.quote_hash,
        )
        for locator in current.source_locators
    ]
    child_links = [
        InstrumentLinkInput(
            instrument_id=link.instrument_id,
            role=link.role,
            link_order=link.link_order,
            link_metadata=dict(link.link_metadata or {}),
        )
        for link in current.instrument_links
    ]
    version = EvidenceVersion(
        evidence_series_id=current.evidence_series_id,
        version=current.version + 1,
        source_document_version_id=current.source_document_version_id,
        information_type=current.information_type,
        provenance_kind=current.provenance_kind,
        source_grade_snapshot=current.source_grade_snapshot,
        verification_status=verification_status,
        status_changed_at=status_changed_at,
        status_changed_by_actor=status_changed_by_actor,
        status_change_kind=status_change_kind,
        status_reason=status_reason,
        display_title=_override(overrides, "display_title", current.display_title),
        display_text=_override(overrides, "display_text", current.display_text),
        claim_key=current.claim_key,
        metric_key=current.metric_key,
        raw_value=_override(overrides, "raw_value", current.raw_value),
        raw_unit=_override(overrides, "raw_unit", current.raw_unit),
        normalized_value=_override(overrides, "normalized_value", current.normalized_value),
        normalized_text_value=_override(
            overrides, "normalized_text_value", current.normalized_text_value
        ),
        normalized_unit=_override(overrides, "normalized_unit", current.normalized_unit),
        currency=_override(overrides, "currency", current.currency),
        period_start=current.period_start,
        period_end=current.period_end,
        as_of=_override(overrides, "as_of", current.as_of),
        effective_from=_override(overrides, "effective_from", current.effective_from),
        effective_to=_override(overrides, "effective_to", current.effective_to),
        supersedes_evidence_version_id=current.id,
        created_at=status_changed_at,
        created_by_actor=status_changed_by_actor,
        extractor_name=current.extractor_name,
        extractor_version=current.extractor_version,
        prompt_template_version=current.prompt_template_version,
        manual_entry_reason=current.manual_entry_reason,
        manual_observed_at=current.manual_observed_at,
        trusted_correction_rule=_override(
            overrides, "trusted_correction_rule", current.trusted_correction_rule
        ),
    )
    _attach_children(version, current.source_document_version_id, child_locators, child_links, ())
    try:
        async with db.begin_nested():
            db.add(version)
            await db.flush()
            await _record_idempotency(
                db,
                scope=idempotency_scope,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_ref_type="EvidenceVersion",
                response_ref_id=version.id,
                as_of=status_changed_at,
            )
            _audit(
                db,
                "EvidenceVersion",
                version.id,
                f"EVIDENCE_{status_change_kind}",
                payload,
                status_changed_by_actor,
                status_changed_at,
            )
    except IntegrityError as exc:
        latest = await get_current_evidence(db, current.evidence_series_id)
        raise EvidenceVersionConflict(
            f"Expected Evidence version {current.version}, current version is {latest.version if latest else None}",
            expected_version=current.version,
            current_version=latest.version if latest is not None else None,
        ) from exc
    loaded = await get_exact_evidence_version(db, version.id)
    if loaded is None:
        raise EvidencePersistenceConflict("EvidenceVersion was not persisted")
    return loaded


def _override(overrides: dict[str, Any], key: str, fallback: Any) -> Any:
    return fallback if key not in overrides or overrides[key] is None else overrides[key]


async def _find_source_document(
    db: AsyncSession,
    *,
    publisher_key: str,
    source_type: str,
    external_document_id: str | None,
    canonical_url: str | None,
) -> SourceDocument | None:
    if external_document_id is not None:
        return await get_source_document_by_external_identity(
            db,
            publisher_key,
            source_type,
            external_document_id,
        )
    if canonical_url is not None:
        return await get_source_document_by_canonical_url_identity(
            db,
            publisher_key,
            source_type,
            canonical_url,
        )
    return None


def _source_document_idempotency_scope(
    *,
    publisher_key: str,
    source_type: str,
    external_document_id: str | None,
    canonical_url: str | None,
) -> str:
    identity = {
        "publisher_key": publisher_key,
        "source_type": source_type,
        "external_document_id": external_document_id,
        "canonical_url": canonical_url if external_document_id is None else None,
    }
    return f"source_document:{stable_hash(identity)}"


def _source_version_idempotency_scope(source_document_id: str) -> str:
    return f"source_document:{source_document_id}:version_import"


def _validate_source_lifecycle_tuple(
    *,
    source_status: str,
    source_status_changed_at: datetime | None,
    source_status_actor: str | None,
    source_status_reason: str | None,
) -> None:
    has_any_audit = any(
        item is not None
        for item in (source_status_changed_at, source_status_actor, source_status_reason)
    )
    has_all_audit = all(
        item is not None
        for item in (source_status_changed_at, source_status_actor, source_status_reason)
    )
    if source_status == "ACTIVE":
        if has_any_audit:
            raise EvidenceValidationError(
                "ACTIVE source status cannot carry lifecycle audit metadata",
                validation_path="source_status",
            )
        return
    if source_status not in {"RETRACTED", "SUPERSEDED"}:
        raise EvidenceValidationError(
            f"Invalid source lifecycle status: {source_status}",
            validation_path="source_status",
        )
    if not has_all_audit:
        raise EvidenceValidationError(
            "RETRACTED/SUPERSEDED source status requires complete lifecycle audit metadata",
            validation_path="source_status",
        )
    if source_status_actor not in SOURCE_STATUS_ACTORS:
        raise EvidenceValidationError(
            f"Invalid source status actor: {source_status_actor}",
            validation_path="source_status_actor",
        )


async def _record_source_reobservation(
    db: AsyncSession,
    *,
    idempotency_scope: str,
    idempotency_key: str,
    request_hash: str,
    source_document_id: str,
    source_document_version_id: str,
    audit_payload: dict[str, Any],
    as_of: datetime | None,
) -> None:
    async with db.begin_nested():
        await _record_idempotency(
            db,
            scope=idempotency_scope,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            response_ref_type="SourceDocumentVersion",
            response_ref_id=source_document_version_id,
            as_of=as_of,
        )
        _audit(
            db,
            "SourceDocument",
            source_document_id,
            "SOURCE_DOCUMENT_VERSION_REOBSERVED",
            {**audit_payload, "source_document_version_id": source_document_version_id},
            "IMPORTER",
            as_of,
        )
        await db.flush()


def _ensure_same_source_payload(source: SourceDocument, payload: dict[str, Any]) -> None:
    comparable = {
        "publisher_key": source.publisher_key,
        "publisher_name": source.publisher_name,
        "source_type": source.source_type,
        "external_document_id": source.external_document_id,
        "canonical_url": source.canonical_url,
        "issuer_key": source.issuer_key,
        "issuer_name": source.issuer_name,
        "title": source.title,
        "document_language": source.document_language,
        "created_by_actor": source.created_by_actor,
    }
    if comparable != payload:
        raise EvidencePersistenceConflict(
            "SourceDocument identity already exists with different metadata"
        )


async def _get_source_document_for_update(
    db: AsyncSession,
    source_document_id: str,
) -> SourceDocument | None:
    result = await db.execute(
        select(SourceDocument).where(SourceDocument.id == source_document_id).with_for_update()
    )
    return result.scalar_one_or_none()


async def _get_current_evidence_for_update(
    db: AsyncSession,
    evidence_series_id: str,
) -> EvidenceVersion | None:
    result = await db.execute(
        _evidence_select()
        .where(EvidenceVersion.evidence_series_id == evidence_series_id)
        .order_by(EvidenceVersion.version.desc())
        .limit(1)
        .with_for_update()
    )
    return result.scalar_one_or_none()


def _evidence_select() -> Select[tuple[EvidenceVersion]]:
    return select(EvidenceVersion).options(*_evidence_version_load_options())


def _validate_identity_enums(scope_type: str, information_type: str, provenance_kind: str) -> None:
    _ensure_enum("scope_type", scope_type, SCOPE_TYPES, EvidenceValidationError)
    _ensure_enum("information_type", information_type, INFORMATION_TYPES, EvidenceValidationError)
    _ensure_enum("provenance_kind", provenance_kind, PROVENANCE_KINDS, EvidenceInvalidProvenance)


def _ensure_enum(
    field_name: str,
    value: str,
    allowed: Sequence[str],
    error_type: type[EvidenceDomainError],
) -> None:
    if value not in allowed:
        if field_name == "source_type":
            raise error_type(f"Invalid {field_name}: {value}", source_type=value)
        if field_name == "source_grade":
            raise error_type(f"Invalid {field_name}: {value}", source_grade=value)
        raise error_type(
            f"Invalid {field_name}: {value}",
            validation_path=field_name,
            invalid_value=value,
        )


def _ensure_actor(actor: str) -> None:
    if actor not in ACTORS:
        raise EvidenceValidationError(f"Invalid actor: {actor}", actor=actor)


def _ensure_source_grade_allowed(source_type: str, source_grade: str) -> None:
    allowed = SOURCE_TYPE_ALLOWED_GRADES.get(source_type)
    if allowed is None:
        raise EvidenceInvalidSourceType(
            f"Invalid source type: {source_type}", source_type=source_type
        )
    if source_grade not in allowed:
        raise EvidenceInvalidSourceGrade(
            f"Source grade {source_grade} is incompatible with {source_type}",
            source_grade=source_grade,
            source_type=source_type,
        )


async def _validate_provenance(
    db: AsyncSession,
    *,
    information_type: str,
    provenance_kind: str,
    primary_source_document_id: str | None,
    origin_key: str | None,
    source_document_version_id: str | None,
    manual_entry_reason: str | None,
    manual_observed_at: datetime | None,
    locators: Sequence[SourceLocatorInput],
) -> SourceDocumentVersion | None:
    if information_type == "FACT" and provenance_kind != "SOURCE_BACKED":
        raise EvidenceInvalidProvenance("FACT Evidence must be SOURCE_BACKED")
    if information_type == "THESIS_INFERENCE" and provenance_kind != "DERIVED":
        raise EvidenceInvalidProvenance("THESIS_INFERENCE must be DERIVED")
    if provenance_kind == "SOURCE_BACKED":
        if (
            primary_source_document_id is None
            or origin_key is not None
            or source_document_version_id is None
        ):
            raise EvidenceInvalidProvenance(
                "SOURCE_BACKED Evidence requires source document/version provenance"
            )
        source_version = await get_source_document_version(db, source_document_version_id)
        if source_version is None:
            raise EvidenceSourceVersionNotFound(
                f"SourceDocumentVersion {source_document_version_id} not found",
                source_document_version_id=source_document_version_id,
            )
        if source_version.source_document_id != primary_source_document_id:
            raise EvidenceInvalidProvenance(
                "Source version does not belong to primary source document"
            )
        source = await get_source_document(db, primary_source_document_id)
        if source is None:
            raise EvidenceSourceDocumentNotFound(
                f"SourceDocument {primary_source_document_id} not found",
                source_document_id=primary_source_document_id,
            )
        _ensure_source_grade_allowed(source.source_type, source_version.source_grade)
        if not locators:
            raise EvidenceInvalidSourceLocator(
                "SOURCE_BACKED Evidence requires at least one locator",
                source_document_version_id=source_version.id,
                locator_path="locators",
            )
        for locator in locators:
            _validate_locator(source_version, locator)
        return source_version
    if (
        primary_source_document_id is not None
        or source_document_version_id is not None
        or origin_key is None
    ):
        raise EvidenceInvalidProvenance(
            "MANUAL/DERIVED Evidence requires origin_key and no source document"
        )
    if provenance_kind == "MANUAL" and (manual_entry_reason is None or manual_observed_at is None):
        raise EvidenceInvalidProvenance(
            "MANUAL Evidence requires manual_entry_reason and manual_observed_at"
        )
    return None


def _validate_locator(source_version: SourceDocumentVersion, locator: SourceLocatorInput) -> None:
    if locator.locator_type not in LOCATOR_TYPES:
        _raise_invalid_locator(source_version.id, "locator_type", "Invalid source locator type")
    if not locator.raw_locator:
        _raise_invalid_locator(
            source_version.id,
            "raw_locator",
            "Source locator requires raw locator",
        )
    if not locator.short_citation:
        _raise_invalid_locator(
            source_version.id,
            "short_citation",
            "Source locator requires short citation",
        )
    payload = locator.locator_payload
    metadata = source_version.versioned_metadata
    if locator.locator_type == "PAGE":
        page_number = _required_positive_int(
            source_version.id, payload, "page_number", "locator_payload.page_number"
        )
        _validate_page_bound(source_version.id, page_number, metadata)
        return
    if locator.locator_type == "PAGE_PARAGRAPH":
        page_number = _required_positive_int(
            source_version.id, payload, "page_number", "locator_payload.page_number"
        )
        paragraph_index = _required_positive_int(
            source_version.id,
            payload,
            "paragraph_index",
            "locator_payload.paragraph_index",
        )
        _validate_page_bound(source_version.id, page_number, metadata)
        paragraph_count = _metadata_int_map_value(metadata, "paragraph_count_by_page", page_number)
        if paragraph_count is not None and paragraph_index > paragraph_count:
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.paragraph_index",
                "Paragraph locator exceeds parser paragraph count",
            )
        return
    if locator.locator_type == "SECTION":
        if not any(payload.get(key) for key in ("section_id", "section_title", "section_path")):
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.section",
                "SECTION locator requires section_id, section_title, or section_path",
            )
        return
    if locator.locator_type == "TABLE":
        page_number = _required_positive_int(
            source_version.id, payload, "page_number", "locator_payload.page_number"
        )
        table_index = _required_positive_int(
            source_version.id, payload, "table_index", "locator_payload.table_index"
        )
        _validate_page_bound(source_version.id, page_number, metadata)
        _validate_table_bound(source_version.id, page_number, table_index, metadata)
        row_index = _optional_positive_int(
            source_version.id, payload, "row_index", "locator_payload.row_index"
        )
        column_index = _optional_positive_int(
            source_version.id, payload, "column_index", "locator_payload.column_index"
        )
        _optional_nonempty_string(
            source_version.id, payload, "cell_ref", "locator_payload.cell_ref"
        )
        table_shape = _metadata_table_shape(metadata, page_number, table_index)
        if row_index is not None or column_index is not None:
            _validate_table_shape_bounds(
                source_version.id,
                table_shape,
                row_index=row_index,
                column_index=column_index,
            )
        return
    if locator.locator_type == "TABLE_CELL":
        page_number = _required_positive_int(
            source_version.id, payload, "page_number", "locator_payload.page_number"
        )
        table_index = _required_positive_int(
            source_version.id, payload, "table_index", "locator_payload.table_index"
        )
        cell_ref = _optional_nonempty_string(
            source_version.id, payload, "cell_ref", "locator_payload.cell_ref"
        )
        row_index = _optional_positive_int(
            source_version.id, payload, "row_index", "locator_payload.row_index"
        )
        column_index = _optional_positive_int(
            source_version.id, payload, "column_index", "locator_payload.column_index"
        )
        if (row_index is None) != (column_index is None):
            if row_index is None:
                _raise_invalid_locator(
                    source_version.id,
                    "locator_payload.row_index",
                    "TABLE_CELL locator requires row_index with numeric coordinates",
                )
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.column_index",
                "TABLE_CELL locator requires column_index with numeric coordinates",
            )
        if cell_ref is None:
            if row_index is None:
                _raise_invalid_locator(
                    source_version.id,
                    "locator_payload.row_index",
                    "TABLE_CELL locator requires row_index with numeric coordinates",
                )
            if column_index is None:
                _raise_invalid_locator(
                    source_version.id,
                    "locator_payload.column_index",
                    "TABLE_CELL locator requires column_index with numeric coordinates",
                )
        _validate_page_bound(source_version.id, page_number, metadata)
        _validate_table_bound(source_version.id, page_number, table_index, metadata)
        table_shape = _metadata_table_shape(metadata, page_number, table_index)
        _validate_table_shape_bounds(
            source_version.id,
            table_shape,
            row_index=row_index,
            column_index=column_index,
        )
        return
    if locator.locator_type == "WEB_ANCHOR":
        canonical_url = payload.get("canonical_url")
        if not isinstance(canonical_url, str) or not canonical_url.strip():
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.canonical_url",
                "WEB_ANCHOR locator requires canonical_url",
            )
        for field in ("anchor", "css_selector", "text_quote_hash"):
            _optional_nonempty_string(source_version.id, payload, field, f"locator_payload.{field}")
        return
    if locator.locator_type == "TIME_RANGE":
        start = payload.get("start_seconds")
        end = payload.get("end_seconds")
        if not isinstance(start, (int, float)) or isinstance(start, bool):
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.time_range",
                "TIME_RANGE locator requires non-negative start_seconds and greater end_seconds",
            )
            return
        if not isinstance(end, (int, float)) or isinstance(end, bool):
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.time_range",
                "TIME_RANGE locator requires non-negative start_seconds and greater end_seconds",
            )
            return
        if start < 0 or end <= start:
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.time_range",
                "TIME_RANGE locator requires non-negative start_seconds and greater end_seconds",
            )
            return
        duration = metadata.get("duration_seconds")
        if isinstance(duration, (int, float)) and end > duration:
            _raise_invalid_locator(
                source_version.id,
                "locator_payload.end_seconds",
                "TIME_RANGE locator exceeds parser duration",
            )


def _raise_invalid_locator(
    source_document_version_id: str,
    locator_path: str,
    message: str,
) -> None:
    raise EvidenceInvalidSourceLocator(
        message,
        source_document_version_id=source_document_version_id,
        locator_path=locator_path,
    )


def _required_positive_int(
    source_document_version_id: str,
    payload: dict[str, Any],
    field: str,
    locator_path: str,
) -> int:
    value = payload.get(field)
    if type(value) is int and value >= 1:
        return value
    _raise_invalid_locator(
        source_document_version_id,
        locator_path,
        f"Locator requires positive integer {field}",
    )
    return 0


def _optional_positive_int(
    source_document_version_id: str,
    payload: dict[str, Any],
    field: str,
    locator_path: str,
) -> int | None:
    if field not in payload:
        return None
    value = payload.get(field)
    if type(value) is int and value >= 1:
        return value
    _raise_invalid_locator(
        source_document_version_id,
        locator_path,
        f"Locator requires positive integer {field}",
    )
    return None


def _optional_nonempty_string(
    source_document_version_id: str,
    payload: dict[str, Any],
    field: str,
    locator_path: str,
) -> str | None:
    if field not in payload:
        return None
    value = payload.get(field)
    if isinstance(value, str) and value.strip():
        return value
    _raise_invalid_locator(
        source_document_version_id,
        locator_path,
        f"Locator requires nonempty string {field}",
    )
    return None


def _validate_page_bound(
    source_document_version_id: str,
    page_number: int,
    metadata: dict[str, Any],
) -> None:
    page_count = metadata.get("page_count")
    if isinstance(page_count, int) and page_number > page_count:
        _raise_invalid_locator(
            source_document_version_id,
            "locator_payload.page_number",
            "Locator page exceeds parser page count",
        )


def _metadata_int_map_value(
    metadata: dict[str, Any],
    field: str,
    index: int,
) -> int | None:
    mapping = metadata.get(field)
    if not isinstance(mapping, dict):
        return None
    value = mapping.get(index)
    if value is None:
        value = mapping.get(str(index))
    return value if isinstance(value, int) else None


def _validate_table_bound(
    source_document_version_id: str,
    page_number: int,
    table_index: int,
    metadata: dict[str, Any],
) -> None:
    table_count = _metadata_int_map_value(metadata, "table_count_by_page", page_number)
    if table_count is not None and table_index > table_count:
        _raise_invalid_locator(
            source_document_version_id,
            "locator_payload.table_index",
            "Table locator exceeds parser table count",
        )


def _metadata_table_shape(
    metadata: dict[str, Any],
    page_number: int,
    table_index: int,
) -> dict[str, Any] | None:
    shapes = metadata.get("table_shape_by_page_index")
    if not isinstance(shapes, dict):
        return None
    shape = shapes.get(f"{page_number}:{table_index}")
    if shape is None:
        shape = shapes.get((page_number, table_index))
    return shape if isinstance(shape, dict) else None


def _validate_table_shape_bounds(
    source_document_version_id: str,
    table_shape: dict[str, Any] | None,
    *,
    row_index: int | None,
    column_index: int | None,
) -> None:
    if table_shape is None:
        return
    row_count = table_shape.get("row_count")
    column_count = table_shape.get("column_count")
    if row_index is not None and type(row_count) is int and row_index > row_count:
        _raise_invalid_locator(
            source_document_version_id,
            "locator_payload.row_index",
            "Locator row exceeds parser table shape",
        )
    if column_index is not None and type(column_count) is int and column_index > column_count:
        _raise_invalid_locator(
            source_document_version_id,
            "locator_payload.column_index",
            "Locator column exceeds parser table shape",
        )


async def _validate_instrument_links(
    db: AsyncSession,
    scope_type: str,
    scope_key: str,
    instrument_links: Sequence[InstrumentLinkInput],
) -> None:
    if scope_type == "INSTRUMENT" and not any(
        link.instrument_id == scope_key and link.role == "PRIMARY_SCOPE"
        for link in instrument_links
    ):
        raise EvidenceValidationError("INSTRUMENT scope requires PRIMARY_SCOPE instrument link")
    for link in instrument_links:
        if link.role not in INSTRUMENT_LINK_ROLES:
            raise EvidenceValidationError(f"Invalid instrument link role: {link.role}")
        if await db.get(Instrument, link.instrument_id) is None:
            raise EvidenceValidationError(
                f"Instrument {link.instrument_id} not found",
                instrument_id=link.instrument_id,
            )


async def _validate_derivation_links(
    db: AsyncSession,
    derivation_links: Sequence[DerivationLinkInput],
) -> None:
    seen: set[tuple[str, str]] = set()
    for link in derivation_links:
        if link.role not in DERIVATION_LINK_ROLES:
            raise EvidenceInvalidDerivationLink("Invalid derivation role")
        if await get_exact_evidence_version(db, link.supporting_evidence_version_id) is None:
            raise EvidenceInvalidDerivationLink("Supporting EvidenceVersion does not exist")
        key = (link.supporting_evidence_version_id, link.role)
        if key in seen:
            raise EvidenceInvalidDerivationLink("Duplicate derivation support link")
        seen.add(key)


def _series_identity_hash(
    *,
    scope_type: str,
    scope_key: str,
    information_type: str,
    claim_key: str,
    metric_key: str | None,
    period_start: datetime | None,
    period_end: datetime | None,
    provenance_kind: str,
    primary_source_document_id: str | None,
    origin_key: str | None,
) -> str:
    return stable_hash(
        {
            "scope_type": scope_type,
            "scope_key": scope_key,
            "information_type": information_type,
            "claim_key": claim_key,
            "metric_key": metric_key,
            "period_start": period_start,
            "period_end": period_end,
            "provenance_kind": provenance_kind,
            "primary_source_document_id": primary_source_document_id,
            "origin_key": origin_key,
        }
    )


def _attach_children(
    version: EvidenceVersion,
    source_document_version_id: str | None,
    locators: Sequence[SourceLocatorInput],
    instrument_links: Sequence[InstrumentLinkInput],
    derivation_links: Sequence[DerivationLinkInput],
) -> None:
    version.source_locators = [
        EvidenceSourceLocator(
            source_document_version_id=source_document_version_id or "",
            locator_type=locator.locator_type,
            raw_locator=locator.raw_locator,
            short_citation=locator.short_citation,
            locator_payload=dict(locator.locator_payload),
            quote_hash=locator.quote_hash,
        )
        for locator in locators
    ]
    version.instrument_links = [
        EvidenceInstrumentLink(
            instrument_id=link.instrument_id,
            role=link.role,
            link_order=link.link_order,
            link_metadata=dict(link.link_metadata or {}),
        )
        for link in instrument_links
    ]
    version.derived_links = [
        EvidenceDerivationLink(
            supporting_evidence_version_id=link.supporting_evidence_version_id,
            role=link.role,
            support_order=link.support_order,
            support_weight=link.support_weight,
        )
        for link in derivation_links
    ]


async def _create_corroboration_links(
    db: AsyncSession,
    evidence_version_id: str,
    corroborates_evidence_version_ids: Sequence[str],
    actor: str,
    created_at: datetime | None,
) -> None:
    for other_id in corroborates_evidence_version_ids:
        await create_corroboration_link(
            db,
            left_evidence_version_id=evidence_version_id,
            right_evidence_version_id=other_id,
            relation_type="CORROBORATES",
            created_by_actor=actor,
            created_at=created_at,
        )


def _ensure_expected_version(current: EvidenceVersion, expected_version: int) -> None:
    if current.version != expected_version:
        raise EvidenceVersionConflict(
            f"Expected Evidence version {expected_version}, current version is {current.version}",
            expected_version=expected_version,
            current_version=current.version,
        )


async def _idempotent_replay(
    db: AsyncSession,
    *,
    scope: str,
    idempotency_key: str,
    request_hash: str,
) -> EvidenceIdempotencyRecord | None:
    record = await db.get(EvidenceIdempotencyRecord, (scope, idempotency_key))
    if record is None:
        return None
    if record.request_hash != request_hash:
        raise EvidenceIdempotencyConflict(
            "Idempotency key was already used for a different Evidence request",
            scope=scope,
            idempotency_key=idempotency_key,
        )
    return record


async def _record_idempotency(
    db: AsyncSession,
    *,
    scope: str,
    idempotency_key: str,
    request_hash: str,
    response_ref_type: str,
    response_ref_id: str,
    as_of: datetime | None,
) -> None:
    db.add(
        EvidenceIdempotencyRecord(
            scope=scope,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            status="COMMITTED",
            response_ref_type=response_ref_type,
            response_ref_id=response_ref_id,
            created_at=as_of or utc_now(),
        )
    )
    await db.flush()


def _audit(
    db: AsyncSession,
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    payload: dict[str, Any],
    actor: str,
    occurred_at: datetime | None,
) -> None:
    db.add(
        EvidenceAuditEvent(
            id=uuid_str(),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=_canonical_value(payload),
            occurred_at=occurred_at or utc_now(),
            actor=actor,
        )
    )


__all__ = [
    "DerivationLinkInput",
    "InstrumentLinkInput",
    "SourceLocatorInput",
    "append_source_document_version",
    "canonical_json",
    "canonicalize_url",
    "create_corroboration_link",
    "create_evidence_series_version",
    "create_replacement_evidence_series",
    "get_current_evidence",
    "get_current_valid_evidence",
    "get_exact_evidence_version",
    "list_evidence_by_instrument",
    "list_evidence_by_source_document_version",
    "list_evidence_history",
    "mark_disputed",
    "register_source_document",
    "request_review",
    "retract_or_invalidate",
    "revise_correct_evidence",
    "source_version_fingerprint",
    "stable_hash",
    "verify_or_reject",
]
