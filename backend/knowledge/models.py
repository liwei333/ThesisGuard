"""Knowledge domain SQLAlchemy models.

Knowledge base metadata, document mapping, import task tracking,
and instrument associations. Raw document bytes stay in MinIO;
parsing/retrieval state lives in WeKnora; PostgreSQL is the
system of record for mapping and lifecycle status.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.common.db.session import Base
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Knowledge base categories for MVP document classification
KNOWLEDGE_CATEGORIES: tuple[str, ...] = (
    "TRADING_METHOD",
    "COMPANY_INDUSTRY",
    "POLICY_DOCUMENT",
    "PERSONAL_REVIEW",
)

# Processing lifecycle for a document within WeKnora
DOCUMENT_PROCESSING_STATUSES: tuple[str, ...] = (
    "PENDING",      # accepted, queued for WeKnora submission
    "SUBMITTING",   # async submit in flight
    "PROCESSING",   # WeKnora parsing/indexing
    "READY",        # indexed and searchable
    "FAILED",       # processing failed, retryable
    "RETIRED",      # excluded from new search, history preserved
)

# Import task outcomes
IMPORT_TASK_STATUSES: tuple[str, ...] = (
    "PENDING",
    "IN_PROGRESS",
    "COMPLETED",
    "FAILED",
)


def _quoted_values(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class KnowledgeBase(Base):
    """Thesis-side identity mapped to one WeKnora knowledge base.

    One ThesisGuard knowledge base maps to exactly one WeKnora KB ID.
    Category and metadata are managed on the Thesis side; WeKnora only
    receives the document bytes and returns retrieval results.
    """

    __tablename__ = "knowledge_base"
    __table_args__ = (
        UniqueConstraint("weknora_kb_id", name="uq_knowledge_base_weknora_kb_id"),
        CheckConstraint(
            f"category IN ({_quoted_values(KNOWLEDGE_CATEGORIES)})",
            name="ck_knowledge_base_category",
        ),
        CheckConstraint(
            "(weknora_kb_id IS NOT NULL) OR (status = 'NOT_CONFIGURED')",
            name="ck_knowledge_base_weknora_mapping",
        ),
        Index("ix_knowledge_base_category", "category"),
        Index("ix_knowledge_base_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="NOT_CONFIGURED"
    )
    weknora_kb_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    weknora_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    documents: Mapped[list[KnowledgeDocument]] = relationship(
        back_populates="knowledge_base",
        order_by="KnowledgeDocument.created_at.desc()",
    )
    instrument_links: Mapped[list[KnowledgeInstrumentLink]] = relationship(
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )


class KnowledgeDocument(Base):
    """One Thesis source document mapped to one WeKnora document.

    The raw file lives in MinIO (object_key). WeKnora holds a
    parsed/indexed copy. This row tracks the processing lifecycle
    and the mapping between Thesis source identity and WeKnora IDs.
    """

    __tablename__ = "knowledge_document"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_base_id",
            "weknora_document_id",
            name="uq_knowledge_document_weknora_id",
        ),
        CheckConstraint(
            f"processing_status IN ({_quoted_values(DOCUMENT_PROCESSING_STATUSES)})",
            name="ck_knowledge_document_processing_status",
        ),
        CheckConstraint(
            "source_document_version_id IS NOT NULL OR object_key IS NOT NULL",
            name="ck_knowledge_document_source_present",
        ),
        Index("ix_knowledge_document_kb_id", "knowledge_base_id"),
        Index("ix_knowledge_document_processing_status", "processing_status"),
        Index("ix_knowledge_document_source_version", "source_document_version_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    knowledge_base_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_base.id", ondelete="RESTRICT"),
        nullable=False,
    )
    source_document_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("source_document_version.id", ondelete="RESTRICT"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    weknora_document_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    index_generation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    knowledge_base: Mapped[KnowledgeBase] = relationship(back_populates="documents")
    import_tasks: Mapped[list[KnowledgeImportTask]] = relationship(
        back_populates="document",
        order_by="KnowledgeImportTask.created_at.desc()",
    )


class KnowledgeImportTask(Base):
    """Append-only record of an async import/index operation.

    Used for idempotency, status tracking, and late-arrival reconciliation.
    """

    __tablename__ = "knowledge_import_task"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_document_id",
            "idempotency_key",
            name="uq_knowledge_import_task_idempotency",
        ),
        CheckConstraint(
            f"status IN ({_quoted_values(IMPORT_TASK_STATUSES)})",
            name="ck_knowledge_import_task_status",
        ),
        Index("ix_knowledge_import_task_document", "knowledge_document_id"),
        Index("ix_knowledge_import_task_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    knowledge_document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_document.id", ondelete="CASCADE"),
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    weknora_task_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="import_tasks")


class KnowledgeInstrumentLink(Base):
    """Association between a knowledge base and an instrument.

    Enables instrument-scoped retrieval: search results are filtered
    to knowledge bases linked to the target instrument.
    """

    __tablename__ = "knowledge_instrument_link"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_base_id",
            "instrument_id",
            name="uq_knowledge_instrument_link",
        ),
        Index("ix_knowledge_instrument_link_instrument", "instrument_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    knowledge_base_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
    )
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
    )
    link_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    knowledge_base: Mapped[KnowledgeBase] = relationship(back_populates="instrument_links")
    instrument: Mapped[Instrument] = relationship()
