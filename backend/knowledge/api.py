"""Knowledge API endpoints.

HTTP layer for knowledge base CRUD, document upload, search,
and instrument association. All writes go through the domain service.
"""

from __future__ import annotations

from typing import Annotated

from backend.common.db.session import get_db
from backend.knowledge.errors import (
    KnowledgeBaseNotFound,
    KnowledgeDocumentNotFound,
    KnowledgeDomainError,
    KnowledgeDuplicateDocument,
    KnowledgeIdempotencyConflict,
    KnowledgeInvalidStateTransition,
    KnowledgePersistenceConflict,
    KnowledgeValidationError,
    KnowledgeWeKnoraNotConfigured,
    KnowledgeWeKnoraUnavailable,
)
from backend.knowledge.schemas import (
    DocumentSubmitRequest,
    ImportTaskRead,
    InstrumentLinkRequest,
    KnowledgeBaseCreateRequest,
    KnowledgeBaseRead,
    KnowledgeDocumentRead,
    KnowledgeErrorCode,
    KnowledgeErrorDetail,
    KnowledgeErrorResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    SearchResultRead,
)
from backend.knowledge.services import (
    create_knowledge_base,
    get_document_content,
    get_knowledge_base_by_id,
    get_knowledge_documents,
    link_instrument_to_knowledge_base,
    list_all_knowledge_bases,
    retire_document,
    search_knowledge,
    submit_document_to_weknora,
    upload_knowledge_document,
)
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

KB_NOT_FOUND_RESPONSE = {
    "model": KnowledgeErrorResponse,
    "description": "Knowledge base not found",
}
DOC_NOT_FOUND_RESPONSE = {
    "model": KnowledgeErrorResponse,
    "description": "Knowledge document not found",
}
KB_CONFLICT_RESPONSE = {
    "model": KnowledgeErrorResponse,
    "description": "Knowledge write conflict",
}


def knowledge_http_exception(error: KnowledgeDomainError) -> HTTPException:
    """Map Knowledge domain errors to HTTP responses."""
    try:
        error_code = KnowledgeErrorCode(error.code)
    except ValueError:
        error_code = KnowledgeErrorCode.KNOWLEDGE_DOMAIN_ERROR

    detail = KnowledgeErrorDetail(code=error_code, message=str(error))

    if isinstance(error, KnowledgeBaseNotFound | KnowledgeDocumentNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, (KnowledgeDuplicateDocument | KnowledgeIdempotencyConflict, KnowledgeInvalidStateTransition)):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(error, KnowledgeValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(error, KnowledgePersistenceConflict):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(error, (KnowledgeWeKnoraUnavailable, KnowledgeWeKnoraNotConfigured)):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = KnowledgeErrorDetail(
            code=KnowledgeErrorCode.KNOWLEDGE_DOMAIN_ERROR,
            message="Knowledge domain operation failed",
        )

    return HTTPException(
        status_code=status_code,
        detail=detail.model_dump(mode="json", exclude_none=True),
    )


# ---- Knowledge Base CRUD ----


@router.post(
    "/bases",
    response_model=KnowledgeBaseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_base_endpoint(
    payload: KnowledgeBaseCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseRead:
    """Create a knowledge base."""
    try:
        kb = await create_knowledge_base(
            db,
            name=payload.name,
            description=payload.description,
            category=payload.category.value,
        )
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return KnowledgeBaseRead.model_validate(kb)


@router.get("/bases", response_model=list[KnowledgeBaseRead])
async def list_knowledge_bases_endpoint(
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeBaseRead]:
    """List all knowledge bases."""
    bases = await list_all_knowledge_bases(db)
    return [KnowledgeBaseRead.model_validate(kb) for kb in bases]


@router.get(
    "/bases/{kb_id}",
    response_model=KnowledgeBaseRead,
    responses={404: KB_NOT_FOUND_RESPONSE},
)
async def get_knowledge_base_endpoint(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseRead:
    """Get one knowledge base."""
    try:
        kb = await get_knowledge_base_by_id(db, kb_id)
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return KnowledgeBaseRead.model_validate(kb)


# ---- Document upload ----


@router.post(
    "/bases/{kb_id}/documents",
    response_model=KnowledgeDocumentRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: KB_NOT_FOUND_RESPONSE,
        409: KB_CONFLICT_RESPONSE,
    },
)
async def upload_document_endpoint(
    kb_id: str,
    file: UploadFile = File(...),
    title: Annotated[str | None, Form()] = None,
    published_at: Annotated[str | None, Form()] = None,
    instrument_id: Annotated[str | None, Form()] = None,
    idempotency_key: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentRead:
    """Upload a document to a knowledge base.

    The raw file is persisted in MinIO; source document and version
    records are created via the Evidence domain service.
    """
    content = await file.read()
    from datetime import datetime as dt

    pub_dt = None
    if published_at:
        try:
            pub_dt = dt.fromisoformat(published_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid published_at format (expected ISO 8601)",
            ) from exc

    try:
        doc = await upload_knowledge_document(
            db,
            knowledge_base_id=kb_id,
            filename=file.filename or "unnamed",
            file_content=content,
            media_type=file.content_type or "application/octet-stream",
            title=title,
            published_at=pub_dt,
            instrument_id=instrument_id,
            idempotency_key=idempotency_key or "",
        )
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return KnowledgeDocumentRead.model_validate(doc)


@router.get(
    "/bases/{kb_id}/documents",
    response_model=list[KnowledgeDocumentRead],
)
async def list_documents_endpoint(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeDocumentRead]:
    """List documents in a knowledge base."""
    docs = await get_knowledge_documents(db, kb_id)
    return [KnowledgeDocumentRead.model_validate(doc) for doc in docs]


# ---- WeKnora processing ----


@router.post(
    "/documents/{doc_id}/sync",
    response_model=KnowledgeDocumentRead,
    responses={404: DOC_NOT_FOUND_RESPONSE},
)
async def sync_document_status_endpoint(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentRead:
    """Poll WeKnora for the real processing status of a document.

    Used by the frontend to refresh status after upload/submit.
    """
    from backend.knowledge.services import sync_document_status
    try:
        doc = await sync_document_status(db, knowledge_document_id=doc_id)
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return KnowledgeDocumentRead.model_validate(doc)


@router.post(
    "/documents/{doc_id}/submit",
    response_model=ImportTaskRead,
    responses={
        404: DOC_NOT_FOUND_RESPONSE,
        409: KB_CONFLICT_RESPONSE,
    },
)
async def submit_document_endpoint(
    doc_id: str,
    payload: DocumentSubmitRequest,
    db: AsyncSession = Depends(get_db),
) -> ImportTaskRead:
    """Submit a document to WeKnora for parsing/indexing."""
    try:
        task = await submit_document_to_weknora(
            db,
            knowledge_document_id=doc_id,
            idempotency_key=payload.idempotency_key,
        )
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return ImportTaskRead.model_validate(task)


@router.post(
    "/documents/{doc_id}/retire",
    response_model=KnowledgeDocumentRead,
    responses={404: DOC_NOT_FOUND_RESPONSE, 409: KB_CONFLICT_RESPONSE},
)
async def retire_document_endpoint(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentRead:
    """Retire a document — excluded from new search, history preserved."""
    try:
        doc = await retire_document(db, knowledge_document_id=doc_id)
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return KnowledgeDocumentRead.model_validate(doc)


# ---- Instrument association ----


@router.post(
    "/bases/{kb_id}/instruments",
    status_code=status.HTTP_201_CREATED,
    responses={404: KB_NOT_FOUND_RESPONSE},
)
async def link_instrument_endpoint(
    kb_id: str,
    payload: InstrumentLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Link an instrument to a knowledge base for scoped retrieval."""
    try:
        link = await link_instrument_to_knowledge_base(
            db,
            knowledge_base_id=kb_id,
            instrument_id=payload.instrument_id,
        )
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error
    return {"id": link.id, "knowledge_base_id": kb_id, "instrument_id": payload.instrument_id}


# ---- Search ----


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_endpoint(
    payload: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeSearchResponse:
    """Search knowledge bases and return citation-backed excerpts.

    Results always reference Thesis source documents; WeKnora chunk IDs
    are auxiliary tracking only. No result automatically becomes Evidence.
    """
    try:
        response = await search_knowledge(
            db,
            query=payload.query,
            knowledge_base_ids=payload.knowledge_base_ids,
            instrument_id=payload.instrument_id,
            limit=payload.limit,
        )
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error

    return KnowledgeSearchResponse(
        status=response.status,
        results=[
            SearchResultRead(
                ref_id=item.ref_id,
                knowledge_base_id=item.knowledge_base_id,
                source_document_version_id=item.source_document_version_id,
                title=item.title,
                excerpt=item.excerpt,
                score=item.score,
                score_type=item.score_type,
                published_at=item.published_at,
                instrument_id=item.instrument_id,
                chunk_id=item.chunk_id,
                provider_document_id=item.provider_document_id,
                content_hash=item.content_hash,
                locator_precision=item.locator_precision,
                warnings=item.warnings,
            )
            for item in response.results
        ],
        warnings=response.warnings,
        query=response.query,
        knowledge_base_ids=response.knowledge_base_ids,
    )


# ---- Document content (原文查看) ----


@router.get(
    "/documents/{doc_id}/content",
    responses={404: DOC_NOT_FOUND_RESPONSE},
)
async def get_document_content_endpoint(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream the original document content for viewing.

    Source: MinIO primary, WeKnora fallback.
    The object_key is validated server-side — clients cannot request arbitrary keys.
    """
    try:
        result = await get_document_content(db, knowledge_document_id=doc_id)
    except KnowledgeDomainError as error:
        raise knowledge_http_exception(error) from error

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document content not found",
        )

    content_bytes, filename = result
    import io

    return StreamingResponse(
        io.BytesIO(content_bytes),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
