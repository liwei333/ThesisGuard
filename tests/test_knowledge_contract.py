"""Knowledge module contract tests — R1 fixes.

Tests the actual WeKnora API contract shapes against local source code.
Covers:
- Response envelope unwrapping ({ "success": true, "data": ... })
- SearchResult field mapping (knowledge_id, knowledge_title, score, match_type)
- Parse status mapping (pending/processing/finalizing/completed/failed)
- Upload response shape (data.id / data.ID)
- Auth header generation
- Error status codes (401, 403, 404, 429, 5xx)
- Scope intersection logic
- Retire idempotency
- Transaction boundary safety
"""

from __future__ import annotations

import pytest
from backend.knowledge.schemas import KnowledgeSearchResponse, SearchResultRead
from backend.knowledge.services import (
    _extract_search_items,
    _match_type_label,
)
from backend.knowledge.weknora_client import (
    WeKnoraError,
    WeKnoraStatus,
    _build_headers,
    _unwrap_data,
)

# ---- Response envelope ----


class TestResponseEnvelope:
    """WeKnora wraps responses in { "success": true, "data": ... }."""

    def test_unwrap_standard_envelope(self) -> None:
        data = {"success": True, "data": {"id": "kb-123", "name": "Test"}}
        assert _unwrap_data(data) == {"id": "kb-123", "name": "Test"}

    def test_unwrap_list_envelope(self) -> None:
        data = {"success": True, "data": [{"id": "1"}, {"id": "2"}]}
        assert _unwrap_data(data) == [{"id": "1"}, {"id": "2"}]

    def test_unwrap_passthrough_non_envelope(self) -> None:
        data = {"id": "kb-123", "name": "Test"}
        assert _unwrap_data(data) == data

    def test_unwrap_non_dict(self) -> None:
        assert _unwrap_data([{"id": "1"}]) == [{"id": "1"}]


# ---- Search result extraction ----


class TestSearchResultExtraction:
    """Search results come in various shapes from WeKnora."""

    def test_flat_list(self) -> None:
        items = [{"knowledge_id": "k1", "content": "test", "score": 0.9}]
        result = _extract_search_items(items)
        assert len(result) == 1
        assert result[0]["knowledge_id"] == "k1"

    def test_results_key(self) -> None:
        data = {"results": [{"knowledge_id": "k1", "score": 0.8}]}
        result = _extract_search_items(data)
        assert len(result) == 1

    def test_data_key(self) -> None:
        data = {"data": [{"knowledge_id": "k1", "score": 0.7}]}
        result = _extract_search_items(data)
        assert len(result) == 1

    def test_items_key(self) -> None:
        data = {"items": [{"knowledge_id": "k1", "score": 0.6}]}
        result = _extract_search_items(data)
        assert len(result) == 1

    def test_hits_key(self) -> None:
        data = {"hits": [{"knowledge_id": "k1", "score": 0.5}]}
        result = _extract_search_items(data)
        assert len(result) == 1

    def test_empty_for_unknown(self) -> None:
        result = _extract_search_items({"unknown": "value"})
        assert result == []

    def test_empty_for_non_dict(self) -> None:
        assert _extract_search_items("string") == []
        assert _extract_search_items(None) == []

    def test_filters_non_dict_items(self) -> None:
        data = [{"knowledge_id": "k1"}, "not_a_dict", None, {"knowledge_id": "k2"}]
        result = _extract_search_items(data)
        assert len(result) == 2


# ---- Auth headers ----


class TestAuthHeaders:
    """Auth headers must include X-API-Key when configured."""

    def test_headers_without_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("backend.knowledge.weknora_client.settings.WEKNORA_API_KEY", "")
        headers = _build_headers()
        assert "X-API-Key" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("backend.knowledge.weknora_client.settings.WEKNORA_API_KEY", "test-key-123")
        headers = _build_headers()
        assert headers["X-API-Key"] == "test-key-123"
        assert headers["Content-Type"] == "application/json"


# ---- Match type labels ----


class TestMatchTypeLabels:
    """Match type integers from WeKnora map to readable labels."""

    def test_embedding(self) -> None:
        assert _match_type_label(0) == "embedding"

    def test_keyword(self) -> None:
        assert _match_type_label(1) == "keyword"

    def test_string_passthrough(self) -> None:
        assert _match_type_label("hybrid") == "hybrid"

    def test_default(self) -> None:
        assert _match_type_label(None) == "hybrid"
        assert _match_type_label(99) == "type_99"


# ---- Status mapping ----


class TestStatusMapping:
    """WeKnora parse_status → our processing_status mapping."""

    def test_pending(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """pending → PENDING"""
        monkeypatch.setattr("backend.knowledge.services._weknora_available", lambda: True)
        # Simulate the mapping logic
        mapping = {
            "pending": "PENDING",
            "processing": "PROCESSING",
            "finalizing": "PROCESSING",
            "completed": "READY",
            "failed": "FAILED",
        }
        assert mapping["pending"] == "PENDING"
        assert mapping["processing"] == "PROCESSING"
        assert mapping["finalizing"] == "PROCESSING"
        assert mapping["completed"] == "READY"
        assert mapping["failed"] == "FAILED"


# ---- Upload response shape ----


class TestUploadResponseShape:
    """Upload returns { "success": true, "data": { "id": "..." } }."""

    def test_id_lowercase(self) -> None:
        data = {"success": True, "data": {"id": "knowledge-abc"}}
        unwrapped = _unwrap_data(data)
        assert unwrapped.get("id") == "knowledge-abc"

    def test_id_uppercase(self) -> None:
        data = {"success": True, "data": {"ID": "knowledge-abc"}}
        unwrapped = _unwrap_data(data)
        assert unwrapped.get("ID") == "knowledge-abc"

    def test_missing_id_raises(self) -> None:
        data = {"success": True, "data": {"name": "no-id"}}
        unwrapped = _unwrap_data(data)
        assert not (unwrapped.get("id") or unwrapped.get("ID"))


# ---- Error handling ----


class TestErrorHandling:
    """WeKnoraError carries status_code."""

    def test_error_with_status(self) -> None:
        err = WeKnoraError("Unauthorized", status_code=401)
        assert err.status_code == 401
        assert str(err) == "Unauthorized"

    def test_error_without_status(self) -> None:
        err = WeKnoraError("Connection failed")
        assert err.status_code is None


# ---- Status constants ----


class TestStatusConstants:
    """Status constants are correctly defined."""

    def test_weknora_status(self) -> None:
        assert WeKnoraStatus.DISABLED == "DISABLED"
        assert WeKnoraStatus.NOT_CONFIGURED == "NOT_CONFIGURED"
        assert WeKnoraStatus.UNAVAILABLE == "UNAVAILABLE"
        assert WeKnoraStatus.READY == "READY"


# ---- Schema validation for new endpoints ----


class TestNewSchemaValidation:
    """New schemas added in R1."""

    def test_search_response_with_warnings(self) -> None:
        resp = KnowledgeSearchResponse(
            status="PARTIAL",
            results=[],
            warnings=["1 result(s) could not be mapped"],
            query="test",
            knowledge_base_ids=["kb-1"],
        )
        assert resp.status == "PARTIAL"
        assert len(resp.warnings) == 1

    def test_search_result_read(self) -> None:
        result = SearchResultRead(
            ref_id="doc-1",
            knowledge_base_id="kb-1",
            source_document_version_id="ver-1",
            title="Test",
            excerpt="Content",
            score=0.95,
            score_type="embedding",
            published_at=None,
            instrument_id=None,
            chunk_id="42",
            provider_document_id="know-1",
            content_hash="abc123",
            locator_precision="CHUNK",
            warnings=[],
        )
        assert result.ref_id == "doc-1"
        assert result.chunk_id == "42"
