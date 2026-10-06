"""Stable Knowledge domain errors."""


class KnowledgeDomainError(Exception):
    """Base class for Knowledge domain errors."""

    code = "KNOWLEDGE_DOMAIN_ERROR"

    def __init__(self, message: str, **details: object) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class KnowledgeBaseNotFound(KnowledgeDomainError):
    code = "KNOWLEDGE_BASE_NOT_FOUND"


class KnowledgeDocumentNotFound(KnowledgeDomainError):
    code = "KNOWLEDGE_DOCUMENT_NOT_FOUND"


class KnowledgeDuplicateDocument(KnowledgeDomainError):
    code = "KNOWLEDGE_DUPLICATE_DOCUMENT"


class KnowledgeValidationError(KnowledgeDomainError):
    code = "KNOWLEDGE_VALIDATION_ERROR"


class KnowledgePersistenceConflict(KnowledgeDomainError):
    code = "KNOWLEDGE_PERSISTENCE_CONFLICT"


class KnowledgeIdempotencyConflict(KnowledgeDomainError):
    code = "KNOWLEDGE_IDEMPOTENCY_CONFLICT"


class KnowledgeWeKnoraUnavailable(KnowledgeDomainError):
    """Raised when WeKnora service is unreachable or returns an error."""

    code = "KNOWLEDGE_WEKNORA_UNAVAILABLE"


class KnowledgeWeKnoraNotConfigured(KnowledgeDomainError):
    """Raised when WeKnora integration has not been configured."""

    code = "KNOWLEDGE_WEKNORA_NOT_CONFIGURED"


class KnowledgeImportTaskNotFound(KnowledgeDomainError):
    code = "KNOWLEDGE_IMPORT_TASK_NOT_FOUND"


class KnowledgeInvalidStateTransition(KnowledgeDomainError):
    code = "KNOWLEDGE_INVALID_STATE_TRANSITION"
