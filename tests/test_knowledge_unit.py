"""Knowledge module unit tests.

Tests that run without PostgreSQL:
- Model construction and enum validation
- Error type hierarchy
- WeKnora client status helpers
- Service input validation
- API error mapping
"""

from __future__ import annotations

import pytest

from backend.knowledge.errors import (
    KnowledgeBaseNotFound,
    KnowledgeDomainError,
    KnowledgeDocumentNotFound,
    KnowledgeDuplicateDocument,
    KnowledgeIdempotencyConflict,
    KnowledgeInvalidStateTransition,
    KnowledgePersistenceConflict,
    KnowledgeValidationError,
    KnowledgeWeKnoraNotConfigured,
    KnowledgeWeKnoraUnavailable,
)
from backend.knowledge.models import (
    DOCUMENT_PROCESSING_STATUSES,
    IMPORT_TASK_STATUSES,
    KNOWLEDGE_CATEGORIES,
    KnowledgeBase,
    KnowledgeDocument,
    KnowledgeImportTask,
    KnowledgeInstrumentLink,
)
from backend.knowledge.schemas import (
    KnowledgeBaseCreateRequest,
    KnowledgeErrorCode,
    KnowledgeSearchRequest,
)
from backend.knowledge.weknora_client import WeKnoraStatus


# ---- Error hierarchy ----


class TestKnowledgeErrors:
    """Knowledge domain errors have correct codes and inheritance."""

    def test_base_error_code(self) -> None:
        err = KnowledgeDomainError("test")
        assert err.code == "KNOWLEDGE_DOMAIN_ERROR"
        assert str(err) == "test"

    def test_not_found_codes(self) -> None:
        assert KnowledgeBaseNotFound("x").code == "KNOWLEDGE_BASE_NOT_FOUND"
        assert KnowledgeDocumentNotFound("x").code == "KNOWLEDGE_DOCUMENT_NOT_FOUND"

    def test_conflict_codes(self) -> None:
        assert KnowledgeDuplicateDocument("x").code == "KNOWLEDGE_DUPLICATE_DOCUMENT"
        assert KnowledgeIdempotencyConflict("x").code == "KNOWLEDGE_IDEMPOTENCY_CONFLICT"
        assert KnowledgePersistenceConflict("x").code == "KNOWLEDGE_PERSISTENCE_CONFLICT"

    def test_validation_code(self) -> None:
        err = KnowledgeValidationError("bad input")
        assert err.code == "KNOWLEDGE_VALIDATION_ERROR"

    def test_weknora_codes(self) -> None:
        assert KnowledgeWeKnoraUnavailable("x").code == "KNOWLEDGE_WEKNORA_UNAVAILABLE"
        assert KnowledgeWeKnoraNotConfigured("x").code == "KNOWLEDGE_WEKNORA_NOT_CONFIGURED"

    def test_invalid_transition_code(self) -> None:
        err = KnowledgeInvalidStateTransition("bad move")
        assert err.code == "KNOWLEDGE_INVALID_STATE_TRANSITION"

    def test_all_errors_are_domain_errors(self) -> None:
        errors = [
            KnowledgeBaseNotFound("x"),
            KnowledgeDocumentNotFound("x"),
            KnowledgeDuplicateDocument("x"),
            KnowledgeValidationError("x"),
            KnowledgePersistenceConflict("x"),
            KnowledgeIdempotencyConflict("x"),
            KnowledgeWeKnoraUnavailable("x"),
            KnowledgeWeKnoraNotConfigured("x"),
            KnowledgeInvalidStateTransition("x"),
        ]
        for err in errors:
            assert isinstance(err, KnowledgeDomainError)


# ---- Enum constants ----


class TestKnowledgeEnums:
    """Knowledge enums cover expected values."""

    def test_categories(self) -> None:
        assert "TRADING_METHOD" in KNOWLEDGE_CATEGORIES
        assert "COMPANY_INDUSTRY" in KNOWLEDGE_CATEGORIES
        assert "POLICY_DOCUMENT" in KNOWLEDGE_CATEGORIES
        assert "PERSONAL_REVIEW" in KNOWLEDGE_CATEGORIES

    def test_processing_statuses(self) -> None:
        assert "PENDING" in DOCUMENT_PROCESSING_STATUSES
        assert "PROCESSING" in DOCUMENT_PROCESSING_STATUSES
        assert "READY" in DOCUMENT_PROCESSING_STATUSES
        assert "FAILED" in DOCUMENT_PROCESSING_STATUSES
        assert "RETIRED" in DOCUMENT_PROCESSING_STATUSES

    def test_import_task_statuses(self) -> None:
        assert "PENDING" in IMPORT_TASK_STATUSES
        assert "COMPLETED" in IMPORT_TASK_STATUSES
        assert "FAILED" in IMPORT_TASK_STATUSES

    def test_weknora_status_constants(self) -> None:
        assert WeKnoraStatus.DISABLED == "DISABLED"
        assert WeKnoraStatus.NOT_CONFIGURED == "NOT_CONFIGURED"
        assert WeKnoraStatus.UNAVAILABLE == "UNAVAILABLE"
        assert WeKnoraStatus.READY == "READY"


# ---- WeKnora client response parsing ----


class TestWeKnoraResponseParsing:
    """Search result extraction handles multiple response shapes."""

    def test_extract_list_response(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items([{"id": "1"}, {"id": "2"}])
        assert len(items) == 2

    def test_extract_data_key(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items({"data": [{"id": "1"}]})
        assert len(items) == 1

    def test_extract_results_key(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items({"results": [{"id": "1"}, {"id": "2"}]})
        assert len(items) == 2

    def test_extract_items_key(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items({"items": [{"id": "1"}]})
        assert len(items) == 1

    def test_extract_empty_for_unknown_shape(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items({"unknown_key": "value"})
        assert items == []

    def test_extract_empty_for_non_dict(self) -> None:
        from backend.knowledge.services import _extract_search_items

        items = _extract_search_items("not a dict")
        assert items == []


# ---- Schema validation ----


class TestKnowledgeSchemas:
    """Pydantic schemas validate input correctly."""

    def test_create_base_request_valid(self) -> None:
        req = KnowledgeBaseCreateRequest(name="Test KB")
        assert req.name == "Test KB"
        assert req.category.value == "COMPANY_INDUSTRY"

    def test_create_base_request_with_description(self) -> None:
        req = KnowledgeBaseCreateRequest(
            name="My KB",
            description="A test knowledge base",
            category="TRADING_METHOD",
        )
        assert req.description == "A test knowledge base"
        assert req.category.value == "TRADING_METHOD"

    def test_create_base_request_rejects_blank_name(self) -> None:
        with pytest.raises(Exception):  # ValidationError
            KnowledgeBaseCreateRequest(name="")

    def test_search_request_valid(self) -> None:
        req = KnowledgeSearchRequest(query="test query")
        assert req.query == "test query"
        assert req.limit == 10

    def test_search_request_limit_bounds(self) -> None:
        with pytest.raises(Exception):
            KnowledgeSearchRequest(query="test", limit=0)
        with pytest.raises(Exception):
            KnowledgeSearchRequest(query="test", limit=100)

    def test_search_request_rejects_blank_query(self) -> None:
        with pytest.raises(Exception):
            KnowledgeSearchRequest(query="")

    def test_error_code_enum(self) -> None:
        assert KnowledgeErrorCode.KNOWLEDGE_BASE_NOT_FOUND.value == "KNOWLEDGE_BASE_NOT_FOUND"
        assert KnowledgeErrorCode.KNOWLEDGE_WEKNORA_NOT_CONFIGURED.value == "KNOWLEDGE_WEKNORA_NOT_CONFIGURED"
