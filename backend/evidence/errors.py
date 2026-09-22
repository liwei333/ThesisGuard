"""Stable Evidence domain errors for WP-04 service commands."""

from __future__ import annotations

from typing import Any


class EvidenceDomainError(Exception):
    """Base class for stable Evidence domain errors."""

    code = "EVIDENCE_DOMAIN_ERROR"

    def __init__(
        self,
        message: str,
        *,
        expected_version: int | None = None,
        current_version: int | None = None,
        **details: Any,
    ) -> None:
        self.message = message
        self.expected_version = expected_version
        self.current_version = current_version
        self.details = details
        super().__init__(message)


class EvidenceSourceDocumentNotFound(EvidenceDomainError):
    code = "EVIDENCE_SOURCE_DOCUMENT_NOT_FOUND"


class EvidenceSourceVersionNotFound(EvidenceDomainError):
    code = "EVIDENCE_SOURCE_VERSION_NOT_FOUND"


class EvidenceVersionNotFound(EvidenceDomainError):
    code = "EVIDENCE_VERSION_NOT_FOUND"


class EvidenceVersionConflict(EvidenceDomainError):
    code = "EVIDENCE_VERSION_CONFLICT"


class EvidenceIdempotencyConflict(EvidenceDomainError):
    code = "EVIDENCE_IDEMPOTENCY_CONFLICT"


class EvidenceDuplicateSourceVersion(EvidenceDomainError):
    code = "EVIDENCE_DUPLICATE_SOURCE_VERSION"


class EvidenceInvalidStateTransition(EvidenceDomainError):
    code = "EVIDENCE_INVALID_STATE_TRANSITION"


class EvidenceInvalidSourceLocator(EvidenceDomainError):
    code = "EVIDENCE_INVALID_SOURCE_LOCATOR"


class EvidenceInvalidSourceGrade(EvidenceDomainError):
    code = "EVIDENCE_INVALID_SOURCE_GRADE"


class EvidenceInvalidSourceType(EvidenceDomainError):
    code = "EVIDENCE_INVALID_SOURCE_TYPE"


class EvidenceInvalidProvenance(EvidenceDomainError):
    code = "EVIDENCE_INVALID_PROVENANCE"


class EvidenceInvalidCorroborationLink(EvidenceDomainError):
    code = "EVIDENCE_INVALID_CORROBORATION_LINK"


class EvidenceInvalidDerivationLink(EvidenceDomainError):
    code = "EVIDENCE_INVALID_DERIVATION_LINK"


class EvidenceValidationError(EvidenceDomainError):
    code = "EVIDENCE_VALIDATION_ERROR"


class EvidencePersistenceConflict(EvidenceDomainError):
    code = "EVIDENCE_PERSISTENCE_CONFLICT"
