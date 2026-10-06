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
)
from backend.knowledge.weknora_client import (
    create_knowledge_base as weknora_create_kb,
)
from backend.knowledge.weknora_client import (
    hybrid_search as weknora_search,
)
from backend.knowledge.weknora_client import (
    upload_document as weknora_upload,
)
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

    # Persist raw file in MinIO
    object_key = f"knowledge/{knowledge_base_id}/{content_hash}/{filename}"
    minio_storage.put_object(
        key=object_key,
        data=file_content,
        content_type=media_type,
    )

    # Register source document + version via existing Evidence services
    source = await register_source_document(
        db,
        publisher_key=publisher_key,
        publisher_name=publisher_name,
        source_type=source_type,
        title=title or filename,
        created_by_actor=created_by_actor,
        idempotency_key=idempotency_key or _stable_hash(
            {"kb": knowledge_base_id, "file": filename, "hash": content_hash}
        ),
    )
    source_version = await append_source_document_version(
        db,
        source_document_id=source.id,
        expected_version=0 if not source.versions else source.versions[-1].version,
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


async def submit_document_to_weknora(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
    idempotency_key: str,
) -> KnowledgeImportTask:
    """Submit a document to WeKnora for processing."""
    if not _weknora_available():
        raise KnowledgeWeKnoraNotConfigured(
            "WeKnora is not configured or disabled"
        )

    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
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

    file_bytes = minio_storage.get_object(doc.object_key)
    if file_bytes is None:
        raise KnowledgeValidationError(
            f"Raw file not found in storage: {doc.object_key}"
        )

    task = KnowledgeImportTask(
        knowledge_document_id=knowledge_document_id,
        idempotency_key=idempotency_key,
        request_hash=_stable_hash(
            {"doc": knowledge_document_id, "kb": kb.weknora_kb_id}
        ),
        status="PENDING",
    )
    doc.processing_status = "SUBMITTING"

    try:
        async with db.begin_nested():
            db.add(task)
            await db.flush()
            # Submit to WeKnora outside the DB transaction
            try:
                upload_result = await weknora_upload(
                    kb_id=kb.weknora_kb_id,
                    filename=doc.title,
                    file_content=file_bytes,
                    content_type=doc.media_type,
                )
                task.status = "COMPLETED"
                task.completed_at = utc_now()
                weknora_doc_id = upload_result.get("id") or upload_result.get("document_id")
                doc.weknora_document_id = weknora_doc_id
                doc.processing_status = "PROCESSING"
            except WeKnoraError as exc:
                task.status = "FAILED"
                task.error_message = exc.message
                doc.processing_status = "FAILED"
                doc.last_error = exc.message
                doc.retry_count += 1
                logger.warning("WeKnora upload failed for doc %s: %s", doc.id, exc)
    except IntegrityError as exc:
        raise KnowledgePersistenceConflict(
            "Import task write violated constraints"
        ) from exc

    return task


async def retire_document(
    db: AsyncSession,
    *,
    knowledge_document_id: str,
) -> KnowledgeDocument:
    """Retire a document — excluded from new search, history preserved."""
    doc = await get_knowledge_document(db, knowledge_document_id)
    if doc is None:
        raise KnowledgeDocumentNotFound(
            f"Document {knowledge_document_id} not found",
            knowledge_document_id=knowledge_document_id,
        )
    if doc.processing_status == "RETIRED":
        raise KnowledgeInvalidStateTransition(
            "Document is already retired",
            from_status=doc.processing_status,
        )

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
    """Search knowledge bases and return citation-backed excerpts."""
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
    if knowledge_base_ids:
        target_kbs = []
        for kb_id in knowledge_base_ids:
            kb = await get_knowledge_base(db, kb_id)
            if kb is not None and kb.status == "READY" and kb.weknora_kb_id:
                target_kbs.append(kb)
    elif instrument_id:
        from backend.knowledge.repositories import list_knowledge_bases_by_instrument
        target_kbs = await list_knowledge_bases_by_instrument(db, instrument_id)
        target_kbs = [kb for kb in target_kbs if kb.status == "READY" and kb.weknora_kb_id]
    else:
        all_kbs = await list_knowledge_bases(db)
        target_kbs = [kb for kb in all_kbs if kb.status == "READY" and kb.weknora_kb_id]

    if not target_kbs:
        return SearchResponse(
            status="EMPTY",
            results=[],
            warnings=[],
            query=query,
            knowledge_base_ids=[],
        )

    results: list[SearchResultItem] = []
    warnings: list[str] = []

    for kb in target_kbs:
        try:
            if not kb.weknora_kb_id:
                continue
            search_data = await weknora_search(
                kb_id=kb.weknora_kb_id,
                query=query,
                limit=limit,
            )
            raw_items = _extract_search_items(search_data)
            for item in raw_items:
                # Map provider document back to our document
                mapped_doc = None
                if item.get("document_id"):
                    from sqlalchemy import select as sa_select
                    result = await db.execute(
                        sa_select(KnowledgeDocument).where(
                            KnowledgeDocument.weknora_document_id == item["document_id"]
                        )
                    )
                    mapped_doc = result.scalar_one_or_none()

                if mapped_doc and mapped_doc.processing_status == "RETIRED":
                    continue  # Skip retired documents

                ref_id = mapped_doc.id if mapped_doc else f"weknora:{kb.id}:{item.get('chunk_id', '')}"
                source_version_id = (
                    mapped_doc.source_document_version_id if mapped_doc else None
                )
                content_hash = mapped_doc.content_hash if mapped_doc else None

                results.append(
                    SearchResultItem(
                        ref_id=ref_id,
                        knowledge_base_id=kb.id,
                        source_document_version_id=source_version_id,
                        title=item.get("title", kb.name),
                        excerpt=item.get("content", item.get("text", "")),
                        score=item.get("score", 0.0),
                        score_type=item.get("score_type", "hybrid"),
                        published_at=mapped_doc.published_at if mapped_doc else None,
                        instrument_id=instrument_id,
                        chunk_id=item.get("chunk_id"),
                        provider_document_id=item.get("document_id"),
                        content_hash=content_hash,
                        locator_precision=item.get("locator_precision", "CHUNK"),
                        warnings=item.get("warnings", []),
                    )
                )
        except WeKnoraError as exc:
            warnings.append(f"Search failed for KB {kb.name}: {exc.message}")
            logger.warning("WeKnora search failed for KB %s: %s", kb.id, exc)

    if not results:
        status = "PARTIAL" if warnings else "EMPTY"
        return SearchResponse(
            status=status,
            results=[],
            warnings=warnings,
            query=query,
            knowledge_base_ids=[kb.id for kb in target_kbs],
        )

    return SearchResponse(
        status="SUCCESS",
        results=sorted(results, key=lambda r: r.score, reverse=True)[:limit],
        warnings=warnings,
        query=query,
        knowledge_base_ids=[kb.id for kb in target_kbs],
    )


def _extract_search_items(search_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract result items from various WeKnora response shapes."""
    if isinstance(search_data, list):
        return list(search_data)
    if not isinstance(search_data, dict):
        return []
    for key in ("results", "data", "items", "hits"):
        if key in search_data and isinstance(search_data[key], list):
            return list(search_data[key])
    return []
