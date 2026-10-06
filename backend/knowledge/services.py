"""Knowledge domain services.

Commands manage knowledge base lifecycle, document upload, import task
tracking, and search orchestration. Write commands insert immutable
records and never commit the caller's transaction.

Search orchestrates the adapter call and maps WeKnora results to
Thesis-side reference structures.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from backend.common.config import settings
from backend.common.storage import storage as minio_storage
from backend.evidence.repositories import get_latest_source_document_version
from backend.evidence.services import (
    append_source_document_version,
    register_source_document,
)
from backend.instrument.models import Instrument
from backend.knowledge.errors import (
    KnowledgeBaseNotFound,
    KnowledgeDocumentNotFound,
    KnowledgeDuplicateDocument,
    KnowledgeIdempotencyConflict,
    KnowledgeInvalidStateTransition,
    KnowledgePersistenceConflict,
    KnowledgeValidationError,
    KnowledgeWeKnoraNotConfigured,
)
from backend.knowledge.models import (
    KnowledgeBase,
    KnowledgeDocument,
    KnowledgeImportTask,
    KnowledgeInstrumentLink,
)
from backend.knowledge.repositories import (
    find_document_by_hash,
    get_import_task_by_idempotency,
    get_knowledge_base,
    get_knowledge_document,
    list_knowledge_bases,
    list_knowledge_documents,
)
from backend.knowledge.weknora_client import (
    WeKnoraError,
    WeKnoraStatus,
    get_document_status,
)
from backend.knowledge.weknora_client import (
    create_knowledge_base as weknora_create_kb,
)
from backend.knowledge.weknora_client import (
    get_document_content as weknora_get_document_content,
)
from backend.knowledge.weknora_client import (
    hybrid_search as weknora_search,
)
from backend.knowledge.weknora_client import (
    upload_document as weknora_upload,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def _stable_hash(value: Any) -> str:
    """Return a SHA-256 hash for a JSON-serializable value."""
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def get_document_content(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
) -> tuple[bytes, str] | None:
    """Get the original document content for viewing.

    Returns (bytes, filename) or None if not found.
    Primary source: MinIO. Fallback: WeKnora download endpoint.
    """
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
        )

    # Primary: MinIO
    content = minio_storage.get_object(doc.object_key)
    if content is not None:
        return (content, doc.title)

    # Fallback: WeKnora
    if doc.weknora_document_id and _weknora_available():
        kb = await get_knowledge_base(db, doc.knowledge_base_id)
        if kb and kb.weknora_kb_id:
            try:
                weknora_content = await weknora_get_document_content(
                    kb.weknora_kb_id, doc.weknora_document_id
                )
                if weknora_content:
                    return (weknora_content, doc.title)
            except WeKnoraError as exc:
                logger.warning("WeKnora download failed for doc %s: %s", doc.id, exc)

    return None


def _weknora_available() -> bool:
    """Check whether WeKnora is configured and enabled."""
    return settings.WEKNORA_ENABLED and bool(settings.WEKNORA_HOST)


@dataclass(frozen=True)
class SearchResultItem:
    """One search result from a knowledge base query."""

    ref_id: str
    knowledge_base_id: str
    source_document_version_id: str | None
    title: str
    excerpt: str
    score: float
    score_type: str
    published_at: datetime | None
    instrument_id: str | None
    chunk_id: str | None
    provider_document_id: str | None
    content_hash: str | None
    locator_precision: str
    warnings: list[str]


@dataclass(frozen=True)
class SearchResponse:
    """Knowledge search response with status and results."""

    status: str  # SUCCESS, PARTIAL, EMPTY, NOT_CONFIGURED, UNAVAILABLE
    results: list[SearchResultItem]
    warnings: list[str]
    query: str
    knowledge_base_ids: list[str]


async def create_knowledge_base(
    db: AsyncSession,
    *,
    name: str,
    description: str | None = None,
    category: str = "COMPANY_INDUSTRY",
    created_by_actor: str = "USER",
) -> KnowledgeBase:
    """Create a knowledge base. Optionally provisions WeKnora KB if available."""
    if not name or not name.strip():
        raise KnowledgeValidationError("Knowledge base name must not be blank")

    status = "NOT_CONFIGURED"
    weknora_kb_id = None
    weknora_version = None

    if _weknora_available():
        try:
            kb_record = await weknora_create_kb(name=name, description=description)
            weknora_kb_id = kb_record.get("id") or kb_record.get("kb_id")
            weknora_version = kb_record.get("version")
            status = "READY"
        except WeKnoraError as exc:
            logger.warning("WeKnora KB creation failed, storing local-only: %s", exc)
            status = "NOT_CONFIGURED"

    kb = KnowledgeBase(
        name=name.strip(),
        description=description,
        category=category,
        status=status,
        weknora_kb_id=weknora_kb_id,
        weknora_version=weknora_version,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    try:
        async with db.begin_nested():
            db.add(kb)
            await db.flush()
    except IntegrityError as exc:
        raise KnowledgePersistenceConflict(
            "Knowledge base write violated constraints"
        ) from exc
    return kb


async def list_all_knowledge_bases(db: AsyncSession) -> list[KnowledgeBase]:
    """List all knowledge bases."""
    return await list_knowledge_bases(db)


async def get_knowledge_base_by_id(
    db: AsyncSession, kb_id: str
) -> KnowledgeBase:
    """Get one knowledge base or raise."""
    kb = await get_knowledge_base(db, kb_id)
    if kb is None:
        raise KnowledgeBaseNotFound(
            f"Knowledge base {kb_id} not found",
            knowledge_base_id=kb_id,
        )
    return kb


async def get_knowledge_documents(
    db: AsyncSession, kb_id: str
) -> list[KnowledgeDocument]:
    """List documents in a knowledge base."""
    return await list_knowledge_documents(db, kb_id)


async def upload_knowledge_document(
    db: AsyncSession,
    *,
    knowledge_base_id: str,
    filename: str,
    file_content: bytes,
    media_type: str,
    title: str | None = None,
    published_at: datetime | None = None,
    instrument_id: str | None = None,
    source_type: str = "USER_NOTE",
    publisher_key: str = "thesisguard-knowledge",
    publisher_name: str = "ThesisGuard Knowledge",
    created_by_actor: str = "USER",
    idempotency_key: str = "",
    metadata: dict[str, Any] | None = None,
) -> KnowledgeDocument:
    """Upload a document: persist raw file, create source + version, map to WeKnora."""
    if not filename or not filename.strip():
        raise KnowledgeValidationError("Filename must not be blank")
    if not file_content:
        raise KnowledgeValidationError("File content must not be empty")

    kb = await get_knowledge_base(db, knowledge_base_id)
    if kb is None:
        raise KnowledgeBaseNotFound(
            f"Knowledge base {knowledge_base_id} not found",
            knowledge_base_id=knowledge_base_id,
        )

    content_hash = hashlib.sha256(file_content).hexdigest()
    existing = await find_document_by_hash(db, knowledge_base_id, content_hash)
    if existing is not None:
        raise KnowledgeDuplicateDocument(
            "Document with identical content hash already exists in this knowledge base",
            knowledge_document_id=existing.id,
            content_hash=content_hash,
        )

    # Build a stable logical identity for the local file.
    # This is NOT a fabricated exchange URL — it namespaced local import ID
    # that is deterministic for the same (kb, filename) pair.
    safe_name = filename.strip().replace("/", "_").replace("\\", "_")
    external_id = f"local:{knowledge_base_id}:{safe_name}"

    # Persist raw file in MinIO (outside any DB transaction).
    object_key = f"knowledge/{knowledge_base_id}/{content_hash}/{safe_name}"
    minio_storage.put_object(
        key=object_key,
        data=file_content,
        content_type=media_type,
    )

    # Register source document + version via existing Evidence services.
    # The external_document_id provides the required identity anchor.
    source = await register_source_document(
        db,
        publisher_key=publisher_key,
        publisher_name=publisher_name,
        source_type=source_type,
        external_document_id=external_id,
        title=title or filename,
        created_by_actor=created_by_actor,
        idempotency_key=idempotency_key or _stable_hash(
            {"kb": knowledge_base_id, "file": filename, "hash": content_hash}
        ),
    )

    # Use repository query for expected_version — avoids lazy-loading
    # source.versions outside the service layer.
    latest_version = await get_latest_source_document_version(db, source.id)
    expected_version = latest_version.version if latest_version is not None else 0

    source_version = await append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=expected_version,
        version_reason="NEW_CONTENT",
        source_grade="F",  # Knowledge content is low-grade by default
        published_at=published_at,
        observed_at=utc_now(),
        fetched_at=utc_now(),
        content_hash=content_hash,
        source_version_label=None,
        media_type=media_type,
        object_key=object_key,
        idempotency_key=idempotency_key or _stable_hash(
            {"kb": knowledge_base_id, "version": filename, "hash": content_hash}
        ),
    )

    doc = KnowledgeDocument(
        knowledge_base_id=knowledge_base_id,
        source_document_version_id=source_version.id,
        title=title or filename,
        object_key=object_key,
        content_hash=content_hash,
        media_type=media_type,
        file_size_bytes=len(file_content),
        processing_status="PENDING",
        published_at=published_at,
        metadata_json=metadata or {},
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    try:
        async with db.begin_nested():
            db.add(doc)
            await db.flush()
    except IntegrityError as exc:
        raise KnowledgePersistenceConflict(
            "Knowledge document write violated constraints"
        ) from exc

    # Link instrument if provided
    if instrument_id:
        instrument = await db.get(Instrument, instrument_id)
        if instrument is not None:
            link = KnowledgeInstrumentLink(
                knowledge_base_id=knowledge_base_id,
                instrument_id=instrument_id,
            )
            db.add(link)
            await db.flush()

    return doc


MAX_RETRY_COUNT = 3


async def submit_document_to_weknora(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
    idempotency_key: str,
) -> KnowledgeImportTask:
    """Submit a document to WeKnora for processing.

    Flow:
    1. Validate state in a short transaction (idempotency + guard checks).
    2. Call WeKnora HTTP OUTSIDE any DB transaction.
    3. Persist the result in a second short transaction.
    """
    if not _weknora_available():
        raise KnowledgeWeKnoraNotConfigured(
            "WeKnora is not configured or disabled"
        )

    # --- Phase 1: Validate and create task record (short transaction) ---
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
        )

    # Guard: retired documents cannot be submitted
    if doc.processing_status == "RETIRED":
        raise KnowledgeInvalidStateTransition(
            "Cannot submit a retired document",
            from_status=doc.processing_status,
        )

    # Guard: already processing — prevent concurrent duplicate tasks
    if doc.processing_status in ("SUBMITTING", "PROCESSING"):
        existing_task = await get_import_task_by_idempotency(
            db, knowledge_document_id, idempotency_key
        )
        if existing_task is not None:
            return existing_task
        raise KnowledgeIdempotencyConflict(
            "Document is already being processed",
            knowledge_document_id=knowledge_document_id,
        )

    # Guard: max retries exceeded
    if doc.retry_count >= MAX_RETRY_COUNT:
        raise KnowledgeInvalidStateTransition(
            f"Max retry count ({MAX_RETRY_COUNT}) exceeded",
            retry_count=doc.retry_count,
        )

    kb = await get_knowledge_base(db, doc.knowledge_base_id)
    if kb is None:
        raise KnowledgeBaseNotFound(
            f"Knowledge base {doc.knowledge_base_id} not found"
        )

    if not kb.weknora_kb_id:
        raise KnowledgeWeKnoraNotConfigured(
            "Knowledge base has no WeKnora KB mapping"
        )

    # Idempotency check
    existing_task = await get_import_task_by_idempotency(
        db, knowledge_document_id, idempotency_key
    )
    if existing_task is not None:
        if existing_task.status == "COMPLETED":
            return existing_task
        raise KnowledgeIdempotencyConflict(
            "Import task with this idempotency key already exists",
            task_id=existing_task.id,
        )

    # Read raw file from MinIO (sync I/O — bounded by file size)
    file_bytes = minio_storage.get_object(doc.object_key)
    if file_bytes is None:
        raise KnowledgeValidationError(
            f"Raw file not found in storage: {doc.object_key}"
        )

    # Create task and update document status
    task = KnowledgeImportTask(
        knowledge_document_id=knowledge_document_id,
        idempotency_key=idempotency_key,
        request_hash=_stable_hash(
            {"doc": knowledge_document_id, "kb": kb.weknora_kb_id}
        ),
        status="PENDING",
    )
    doc.processing_status = "SUBMITTING"
    doc.last_error = None

    try:
        async with db.begin_nested():
            db.add(task)
            await db.flush()
    except IntegrityError as exc:
        raise KnowledgePersistenceConflict(
            "Import task write violated constraints"
        ) from exc

    # --- Phase 2: HTTP call OUTSIDE any DB transaction ---
    try:
        upload_result = await weknora_upload(
            kb_id=kb.weknora_kb_id,
            filename=doc.title,
            file_content=file_bytes,
            content_type=doc.media_type,
        )
        weknora_knowledge_id = upload_result.get("id") or upload_result.get("ID")
        if not weknora_knowledge_id:
            raise WeKnoraError(
                f"WeKnora upload returned no knowledge ID: {upload_result}"
            )
    except WeKnoraError as exc:
        # --- Phase 3a: Persist failure (short transaction) ---
        doc = await get_knowledge_document(db, knowledge_document_id)
        if doc is not None:
            doc.processing_status = "FAILED"
            doc.last_error = exc.message
            doc.retry_count += 1
            doc.updated_at = utc_now()
        fail_task = await get_import_task_by_idempotency(
            db, knowledge_document_id, idempotency_key
        )
        if fail_task is not None:
            fail_task.status = "FAILED"
            fail_task.error_message = exc.message
        await db.flush()
        logger.warning("WeKnora upload failed for doc %s: %s", doc.id if doc else "?", exc)
        return task  # Return original task (PENDING state preserved)

    # --- Phase 3b: Persist success (short transaction) ---
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is not None:
        # Guard: document was retired during the HTTP call
        if doc.processing_status == "RETIRED":
            logger.info("Doc %s was retired during upload; keeping RETIRED", doc.id)
            done_task = await get_import_task_by_idempotency(
                db, knowledge_document_id, idempotency_key
            )
            if done_task is not None:
                done_task.status = "COMPLETED"
                done_task.completed_at = utc_now()
            await db.flush()
            return task

        doc.weknora_document_id = weknora_knowledge_id
        doc.processing_status = "PROCESSING"
        doc.updated_at = utc_now()

    done_task = await get_import_task_by_idempotency(
        db, knowledge_document_id, idempotency_key
    )
    if done_task is not None:
        done_task.status = "COMPLETED"
        done_task.completed_at = utc_now()
        done_task.weknora_task_id = weknora_knowledge_id
    await db.flush()

    return task


async def sync_document_status(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
) -> KnowledgeDocument:
    """Poll WeKnora for the real parse status of a document.

    Maps WeKnora parse_status → our processing_status:
      pending     → PENDING
      processing  → PROCESSING
      finalizing  → PROCESSING
      completed   → READY
      failed      → FAILED
    """
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
        )

    if doc.processing_status == "RETIRED":
        return doc  # Never revive retired documents

    if not doc.weknora_document_id:
        return doc  # Not yet submitted

    if not _weknora_available():
        return doc  # Can't sync without service

    kb = await get_knowledge_base(db, doc.knowledge_base_id)
    if kb is None or not kb.weknora_kb_id:
        return doc

    try:
        status_data = await get_document_status(
            kb_id=kb.weknora_kb_id or "",
            knowledge_id=doc.weknora_document_id or "",
        )
    except WeKnoraError as exc:
        logger.warning("WeKnora status sync failed for doc %s: %s", doc.id, exc)
        return doc

    parse_status = status_data.get("parse_status", "")
    status_mapping = {
        "pending": "PENDING",
        "processing": "PROCESSING",
        "finalizing": "PROCESSING",
        "completed": "READY",
        "failed": "FAILED",
    }
    new_status = status_mapping.get(parse_status)
    if new_status and new_status != doc.processing_status:
        doc.processing_status = new_status
        doc.updated_at = utc_now()
        if new_status == "FAILED":
            doc.last_error = status_data.get("last_error", "WeKnora parse failed")
        await db.flush()

    return doc


async def sync_pending_documents(
    db: AsyncSession,
    *,
    limit: int = 10,
) -> int:
    """Sync status for all PROCESSING documents. Returns count updated."""
    if not _weknora_available():
        return 0

    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.processing_status.in_(["PENDING", "SUBMITTING", "PROCESSING"])
        ).limit(limit)
    )
    pending = list(result.scalars().all())
    updated = 0
    for doc in pending:
        before = doc.processing_status
        await sync_document_status(db, knowledge_document_id=doc.id)
        if doc.processing_status != before:
            updated += 1
    return updated


async def retire_document(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
) -> KnowledgeDocument:
    """Retire a document — excluded from new search, history preserved.

    Retire is idempotent: retiring an already-retired document succeeds.
    """
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
        )
    if doc.processing_status == "RETIRED":
        return doc  # Idempotent

    doc.processing_status = "RETIRED"
    doc.updated_at = utc_now()
    await db.flush()
    return doc


async def link_instrument_to_knowledge_base(
    db: AsyncSession,
    *,
    knowledge_base_id: str,
    instrument_id: str,
) -> KnowledgeInstrumentLink:
    """Link an instrument to a knowledge base."""
    kb = await get_knowledge_base(db, knowledge_base_id)
    if kb is None:
        raise KnowledgeBaseNotFound(
            f"Knowledge base {knowledge_base_id} not found"
        )
    instrument = await db.get(Instrument, instrument_id)
    if instrument is None:
        raise KnowledgeValidationError(
            f"Instrument {instrument_id} not found",
            validation_path="instrument_id",
        )

    link = KnowledgeInstrumentLink(
        knowledge_base_id=knowledge_base_id,
        instrument_id=instrument_id,
    )
    try:
        async with db.begin_nested():
            db.add(link)
            await db.flush()
    except IntegrityError:
        # Already linked — not an error
        pass
    return link


async def search_knowledge(
    db: AsyncSession,
    *,
    query: str,
    knowledge_base_ids: list[str] | None = None,
    instrument_id: str | None = None,
    limit: int = 10,
) -> SearchResponse:
    """Search knowledge bases and return citation-backed excerpts.

    Scope resolution:
    - If both knowledge_base_ids and instrument_id are given, we intersect:
      only KBs that are in the requested list AND linked to the instrument.
    - Results are post-filtered: only READY, non-retired documents with valid
      SourceDocumentVersion mappings are included. Unmapped results are counted
      in diagnostics but never returned as trusted citations.
    """
    if not query or not query.strip():
        raise KnowledgeValidationError("Search query must not be blank")

    if not _weknora_available():
        return SearchResponse(
            status=WeKnoraStatus.NOT_CONFIGURED,
            results=[],
            warnings=["WeKnora knowledge service is not configured"],
            query=query,
            knowledge_base_ids=[],
        )

    # Resolve target knowledge bases
    target_kbs: list[KnowledgeBase] = []
    if knowledge_base_ids and instrument_id:
        # Intersection: requested KBs that are also linked to the instrument
        from backend.knowledge.repositories import list_knowledge_bases_by_instrument
        instrument_kbs = await list_knowledge_bases_by_instrument(db, instrument_id)
        instrument_kb_ids = {kb.id for kb in instrument_kbs}
        for kb_id in knowledge_base_ids:
            kb = await get_knowledge_base(db, kb_id)
            if (kb is not None
                    and kb.id in instrument_kb_ids
                    and kb.status == "READY"
                    and kb.weknora_kb_id):
                target_kbs.append(kb)
    elif knowledge_base_ids:
        for kb_id in knowledge_base_ids:
            kb = await get_knowledge_base(db, kb_id)
            if kb is not None and kb.status == "READY" and kb.weknora_kb_id:
                target_kbs.append(kb)
    elif instrument_id:
        from backend.knowledge.repositories import list_knowledge_bases_by_instrument
        instrument_kbs = await list_knowledge_bases_by_instrument(db, instrument_id)
        target_kbs = [kb for kb in instrument_kbs
                      if kb.status == "READY" and kb.weknora_kb_id]
    else:
        all_kbs = await list_knowledge_bases(db)
        target_kbs = [kb for kb in all_kbs
                      if kb.status == "READY" and kb.weknora_kb_id]

    if not target_kbs:
        return SearchResponse(
            status="EMPTY",
            results=[],
            warnings=[],
            query=query,
            knowledge_base_ids=[],
        )

    # Build a lookup: weknora_knowledge_id → (doc, kb_id) for all non-retired
    # READY documents in the target KBs. This constrains mapping to the
    # authorized scope — prevents returning results from other KBs.
    target_kb_ids = {kb.id for kb in target_kbs}
    from sqlalchemy import select as sa_select
    docs_result = await db.execute(
        sa_select(KnowledgeDocument).where(
            KnowledgeDocument.knowledge_base_id.in_(list(target_kb_ids)),
            KnowledgeDocument.weknora_document_id.isnot(None),
        )
    )
    all_kb_docs = list(docs_result.scalars().all())
    knowledge_id_map: dict[str, KnowledgeDocument] = {}
    for d in all_kb_docs:
        if d.weknora_document_id and d.processing_status not in ("RETIRED", "FAILED"):
            knowledge_id_map[d.weknora_document_id] = d

    results: list[SearchResultItem] = []
    warnings: list[str] = []
    unmapped_count = 0

    for kb in target_kbs:
        if not kb.weknora_kb_id:
            continue
        try:
            search_data = await weknora_search(
                kb_id=kb.weknora_kb_id,
                query=query,
                limit=limit,
            )
            raw_items = _extract_search_items(search_data)
            for item in raw_items:
                knowledge_id = item.get("knowledge_id") or item.get("KnowledgeID")
                chunk_id = item.get("id") or item.get("chunk_id") or item.get("ChunkIndex", 0)

                # Map to our document — MUST be in authorized scope
                mapped_doc = knowledge_id_map.get(knowledge_id) if knowledge_id else None

                if not mapped_doc:
                    unmapped_count += 1
                    continue  # Skip unmapped — never return as trusted citation

                # Post-filter: double-check KB归属 + retired status
                if mapped_doc.knowledge_base_id not in target_kb_ids:
                    continue
                if mapped_doc.processing_status == "RETIRED":
                    continue

                source_version_id = mapped_doc.source_document_version_id
                content_hash = mapped_doc.content_hash

                results.append(
                    SearchResultItem(
                        ref_id=mapped_doc.id,
                        knowledge_base_id=kb.id,
                        source_document_version_id=source_version_id,
                        title=item.get("knowledge_title", item.get("KnowledgeTitle", mapped_doc.title)),
                        excerpt=item.get("content", item.get("Content", "")),
                        score=item.get("score", item.get("Score", 0.0)),
                        score_type=_match_type_label(item.get("match_type", item.get("MatchType"))),
                        published_at=mapped_doc.published_at,
                        instrument_id=None,  # Set by caller context if needed
                        chunk_id=str(chunk_id) if chunk_id else None,
                        provider_document_id=knowledge_id,
                        content_hash=content_hash,
                        locator_precision="CHUNK",
                        warnings=[],
                    )
                )
        except WeKnoraError as exc:
            warnings.append(f"Search failed for KB {kb.name}: {exc.message}")
            logger.warning("WeKnora search failed for KB %s: %s", kb.id, exc)

    if unmapped_count > 0:
        warnings.append(f"{unmapped_count} result(s) could not be mapped to authorized documents")

    if not results:
        if warnings:
            status = "UNAVAILABLE" if any("failed" in w.lower() for w in warnings) else "EMPTY"
        else:
            status = "EMPTY"
        return SearchResponse(
            status=status,
            results=[],
            warnings=warnings,
            query=query,
            knowledge_base_ids=[kb.id for kb in target_kbs],
        )

    overall_status = "PARTIAL" if warnings else "SUCCESS"
    return SearchResponse(
        status=overall_status,
        results=sorted(results, key=lambda r: r.score, reverse=True)[:limit],
        warnings=warnings,
        query=query,
        knowledge_base_ids=[kb.id for kb in target_kbs],
    )


def _extract_search_items(search_data: Any) -> list[dict[str, Any]]:
    """Extract result items from WeKnora search response shapes."""
    if isinstance(search_data, list):
        return [item for item in search_data if isinstance(item, dict)]
    if not isinstance(search_data, dict):
        return []
    for key in ("results", "data", "items", "hits"):
        if key in search_data and isinstance(search_data[key], list):
            return [item for item in search_data[key] if isinstance(item, dict)]
    return []


def _match_type_label(raw: Any) -> str:
    """Convert WeKnora match_type to a readable label."""
    if isinstance(raw, int):
        labels = {0: "embedding", 1: "keyword", 2: "nearby", 4: "parent_chunk"}
        return labels.get(raw, f"type_{raw}")
    if isinstance(raw, str) and raw:
        return raw
    return "hybrid"
    return []
