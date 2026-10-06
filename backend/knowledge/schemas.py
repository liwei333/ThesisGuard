"""Knowledge API Pydantic schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeErrorCode(StrEnum):
    """Stable Knowledge API error codes."""

    KNOWLEDGE_BASE_NOT_FOUND = "KNOWLEDGE_BASE_NOT_FOUND"
    KNOWLEDGE_DOCUMENT_NOT_FOUND = "KNOWLEDGE_DOCUMENT_NOT_FOUND"
    KNOWLEDGE_DUPLICATE_DOCUMENT = "KNOWLEDGE_DUPLICATE_DOCUMENT"
    KNOWLEDGE_VALIDATION_ERROR = "KNOWLEDGE_VALIDATION_ERROR"
    KNOWLEDGE_PERSISTENCE_CONFLICT = "KNOWLEDGE_PERSISTENCE_CONFLICT"
    KNOWLEDGE_IDEMPOTENCY_CONFLICT = "KNOWLEDGE_IDEMPOTENCY_CONFLICT"
    KNOWLEDGE_WEKNORA_UNAVAILABLE = "KNOWLEDGE_WEKNORA_UNAVAILABLE"
    KNOWLEDGE_WEKNORA_NOT_CONFIGURED = "KNOWLEDGE_WEKNORA_NOT_CONFIGURED"
    KNOWLEDGE_IMPORT_TASK_NOT_FOUND = "KNOWLEDGE_IMPORT_TASK_NOT_FOUND"
    KNOWLEDGE_INVALID_STATE_TRANSITION = "KNOWLEDGE_INVALID_STATE_TRANSITION"
    KNOWLEDGE_DOMAIN_ERROR = "KNOWLEDGE_DOMAIN_ERROR"


class KnowledgeErrorDetail(BaseModel):
    """Stable Knowledge API error detail."""

    code: KnowledgeErrorCode
    message: str


class KnowledgeErrorResponse(BaseModel):
    """Stable Knowledge API error response."""

    detail: KnowledgeErrorDetail


class KnowledgeCategoryEnum(StrEnum):
    """Knowledge base categories for MVP."""

    TRADING_METHOD = "TRADING_METHOD"
    COMPANY_INDUSTRY = "COMPANY_INDUSTRY"
    POLICY_DOCUMENT = "POLICY_DOCUMENT"
    PERSONAL_REVIEW = "PERSONAL_REVIEW"


# ---- Request schemas ----

class KnowledgeBaseCreateRequest(BaseModel):
    """Request to create a knowledge base."""

    name: str = Field(min_length=1, max_length=256)
    description: str | None = Field(default=None, max_length=2000)
    category: KnowledgeCategoryEnum = KnowledgeCategoryEnum.COMPANY_INDUSTRY


class DocumentUploadRequest(BaseModel):
    """Metadata accompanying a document upload (multipart form)."""

    title: str | None = Field(default=None, max_length=512)
    published_at: datetime | None = None
    instrument_id: str | None = None
    metadata: dict | None = None


class DocumentSubmitRequest(BaseModel):
    """Request to submit a document to WeKnora for processing."""

    idempotency_key: str = Field(min_length=1, max_length=128)


class InstrumentLinkRequest(BaseModel):
    """Request to link an instrument to a knowledge base."""

    instrument_id: str


class KnowledgeSearchRequest(BaseModel):
    """Knowledge search request."""

    query: str = Field(min_length=1, max_length=1000)
    knowledge_base_ids: list[str] | None = Field(default=None, max_length=20)
    instrument_id: str | None = None
    limit: int = Field(default=10, ge=1, le=50)


# ---- Response schemas ----

class KnowledgeBaseRead(BaseModel):
    """Knowledge base response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    category: str
    status: str
    weknora_kb_id: str | None = None
    document_count: int
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentRead(BaseModel):
    """Knowledge document response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    knowledge_base_id: str
    source_document_version_id: str | None = None
    title: str
    content_hash: str
    media_type: str
    file_size_bytes: int
    processing_status: str
    retry_count: int
    last_error: str | None = None
    weknora_document_id: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ImportTaskRead(BaseModel):
    """Import task response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    knowledge_document_id: str
    status: str
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class SearchResultRead(BaseModel):
    """One search result item."""

    ref_id: str
    knowledge_base_id: str
    source_document_version_id: str | None = None
    title: str
    excerpt: str
    score: float
    score_type: str
    published_at: datetime | None = None
    instrument_id: str | None = None
    chunk_id: str | None = None
    provider_document_id: str | None = None
    content_hash: str | None = None
    locator_precision: str
    warnings: list[str]


class KnowledgeSearchResponse(BaseModel):
    """Knowledge search response."""

    status: str
    results: list[SearchResultRead]
    warnings: list[str]
    query: str
    knowledge_base_ids: list[str]
