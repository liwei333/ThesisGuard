"""Knowledge domain query helpers."""

from __future__ import annotations

from backend.knowledge.models import (
    KnowledgeBase,
    KnowledgeDocument,
    KnowledgeImportTask,
    KnowledgeInstrumentLink,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_knowledge_base(
    db: AsyncSession, kb_id: str
) -> KnowledgeBase | None:
    """Return a KnowledgeBase by ID."""
    return await db.get(KnowledgeBase, kb_id)


async def list_knowledge_bases(db: AsyncSession) -> list[KnowledgeBase]:
    """Return all knowledge bases ordered by creation time descending."""
    result = await db.execute(
        select(KnowledgeBase).order_by(KnowledgeBase.created_at.desc())
    )
    return list(result.scalars().all())


async def get_knowledge_document(
    db: AsyncSession, doc_id: str
) -> KnowledgeDocument | None:
    """Return a KnowledgeDocument by ID."""
    return await db.get(KnowledgeDocument, doc_id)


async def list_knowledge_documents(
    db: AsyncSession, kb_id: str
) -> list[KnowledgeDocument]:
    """Return documents in a knowledge base."""
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.knowledge_base_id == kb_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    return list(result.scalars().all())


async def find_document_by_hash(
    db: AsyncSession, kb_id: str, content_hash: str
) -> KnowledgeDocument | None:
    """Find a document by its content hash within a knowledge base."""
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.knowledge_base_id == kb_id,
            KnowledgeDocument.content_hash == content_hash,
        )
    )
    return result.scalar_one_or_none()


async def get_import_task_by_idempotency(
    db: AsyncSession, document_id: str, idempotency_key: str
) -> KnowledgeImportTask | None:
    """Return an import task by document and idempotency key."""
    result = await db.execute(
        select(KnowledgeImportTask).where(
            KnowledgeImportTask.knowledge_document_id == document_id,
            KnowledgeImportTask.idempotency_key == idempotency_key,
        )
    )
    return result.scalar_one_or_none()


async def list_knowledge_base_instrument_ids(
    db: AsyncSession, kb_id: str
) -> list[str]:
    """Return instrument IDs linked to a knowledge base."""
    result = await db.execute(
        select(KnowledgeInstrumentLink.instrument_id).where(
            KnowledgeInstrumentLink.knowledge_base_id == kb_id,
        )
    )
    return list(result.scalars().all())


async def list_knowledge_bases_by_instrument(
    db: AsyncSession, instrument_id: str
) -> list[KnowledgeBase]:
    """Return knowledge bases linked to an instrument."""
    result = await db.execute(
        select(KnowledgeBase)
        .join(KnowledgeInstrumentLink)
        .where(KnowledgeInstrumentLink.instrument_id == instrument_id)
        .order_by(KnowledgeBase.created_at.desc())
    )
    return list(result.scalars().all())
