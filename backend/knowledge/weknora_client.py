"""WeKnora HTTP adapter.

Communicates with the WeKnora knowledge service over HTTP.
All routes verified against local source at bccb4b15 (v0.8.2+102).

Auth: X-API-Key header or Authorization: Bearer <key>.

Verified route contract (from local source):
  POST   /api/v1/knowledge-bases                       Create KB
  GET    /api/v1/knowledge-bases                       List KBs
  GET    /api/v1/knowledge-bases/:id                   Get KB detail
  POST   /api/v1/knowledge-bases/:id/knowledge/file   Upload file (multipart)
  GET    /api/v1/knowledge-bases/:id/knowledge         List documents (paginated)
  GET    /api/v1/knowledge/:id                         Get document detail
  GET    /api/v1/knowledge/:id/spans                   Get parse stages
  GET    /api/v1/knowledge/:id/download                Download original file
  POST   /api/v1/knowledge-bases/:id/hybrid-search     Hybrid search
  GET    /api/v1/health                                Health check

Response envelope: { "success": true, "data": <payload> }
Search params: { "query_text": "...", "match_count": N }
SearchResult fields: id, content, knowledge_id, knowledge_title, chunk_index,
  score, match_type, start_at, end_at, knowledge_base_id, source_locators
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from backend.common.config import settings

logger = logging.getLogger(__name__)


class WeKnoraStatus:
    """Service status constants returned by the adapter layer."""

    DISABLED = "DISABLED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    UNAVAILABLE = "UNAVAILABLE"
    READY = "READY"


class WeKnoraError(Exception):
    """Raised when WeKnora returns an error or is unreachable."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _build_base_url() -> str:
    """Build the WeKnora base URL from settings."""
    host = settings.WEKNORA_HOST
    port = settings.WEKNORA_PORT
    base_path = settings.WEKNORA_BASE_PATH
    return f"http://{host}:{port}{base_path}"


def _build_headers() -> dict[str, str]:
    """Build auth headers for WeKnora requests."""
    headers = {"Content-Type": "application/json"}
    if settings.WEKNORA_API_KEY:
        headers["X-API-Key"] = settings.WEKNORA_API_KEY
    return headers


def _unwrap_data(response_data: Any) -> Any:
    """Unwrap the { "success": true, "data": ... } envelope."""
    if isinstance(response_data, dict) and "data" in response_data:
        return response_data["data"]
    return response_data


async def health_check() -> dict[str, Any]:
    """Check WeKnora service health."""
    if not settings.WEKNORA_ENABLED:
        return {"status": WeKnoraStatus.DISABLED}
    if not settings.WEKNORA_HOST:
        return {"status": WeKnoraStatus.NOT_CONFIGURED}

    base_url = _build_base_url()
    try:
        async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                return {"status": WeKnoraStatus.READY, "details": response.json()}  # type: ignore[no-any-return]
            return {
                "status": WeKnoraStatus.UNAVAILABLE,
                "http_status": response.status_code,
            }
    except httpx.RequestError as exc:
        logger.warning("WeKnora health check failed: %s", exc)
        return {"status": WeKnoraStatus.UNAVAILABLE, "error": str(exc)}


async def create_knowledge_base(name: str, description: str | None = None) -> dict[str, Any]:
    """Create a knowledge base in WeKnora.

    Actual route: POST /api/v1/knowledge-bases
    Request body types.KnowledgeBase — at minimum requires Name.
    Response: { "success": true, "data": <KB with .ID> }
    """
    base_url = _build_base_url()
    payload: dict[str, Any] = {"name": name, "type": "document"}
    if description:
        payload["description"] = description

    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-bases",
            json=payload,
            headers=_build_headers(),
        )
        if response.status_code not in (200, 201):
            raise WeKnoraError(
                f"WeKnora create KB failed: {response.text}",
                status_code=response.status_code,
            )
        data = _unwrap_data(response.json())  # type: ignore[no-any-return]
        if isinstance(data, dict) and "id" in data:
            return data
        if isinstance(data, dict) and "ID" in data:
            return data
        raise WeKnoraError(f"WeKnora create KB returned no ID: {data}")


async def list_knowledge_bases() -> list[dict[str, Any]]:
    """List all knowledge bases.

    Route: GET /api/v1/knowledge-bases
    Response: { "success": true, "data": [<KB>, ...] }
    """
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge-bases",
            headers=_build_headers(),
        )
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora list KBs failed: {response.text}",
                status_code=response.status_code,
            )
        data = _unwrap_data(response.json())  # type: ignore[no-any-return]
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("items", "knowledge_bases"):
                if key in data and isinstance(data[key], list):
                    return list(data[key])
        return []


async def get_knowledge_base(kb_id: str) -> dict[str, Any]:
    """Get one knowledge base detail.

    Route: GET /api/v1/knowledge-bases/:id
    """
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}",
            headers=_build_headers(),
        )
        if response.status_code == 404:
            return {}
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora get KB failed: {response.text}",
                status_code=response.status_code,
            )
        return _unwrap_data(response.json())  # type: ignore[no-any-return]


async def upload_document(
    kb_id: str,
    filename: str,
    file_content: bytes,
    content_type: str = "application/octet-stream",
) -> dict[str, Any]:
    """Upload a document to a WeKnora knowledge base.

    Route: POST /api/v1/knowledge-bases/:id/knowledge/file (multipart/form-data)
    Form field: "file" (binary)
    Response: { "success": true, "data": <Knowledge with .ID> }
    """
    base_url = _build_base_url()
    headers = _build_headers()
    del headers["Content-Type"]  # Let httpx set multipart boundary
    files = {"file": (filename, file_content, content_type)}

    async with httpx.AsyncClient(timeout=settings.WEKNORA_UPLOAD_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/knowledge/file",
            files=files,
            headers=headers,
        )
        if response.status_code not in (200, 201):
            raise WeKnoraError(
                f"WeKnora upload failed: {response.text}",
                status_code=response.status_code,
            )
        data = _unwrap_data(response.json())  # type: ignore[no-any-return]
        if isinstance(data, dict):
            return data
        raise WeKnoraError(f"WeKnora upload returned unexpected shape: {data}")


async def get_document_status(kb_id: str, knowledge_id: str) -> dict[str, Any]:
    """Get document processing status.

    Route: GET /api/v1/knowledge/:id
    Response: { "success": true, "data": <Knowledge with .ParseStatus> }
    """
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge/{knowledge_id}",
            headers=_build_headers(),
        )
        if response.status_code == 404:
            return {}
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora get document status failed: {response.text}",
                status_code=response.status_code,
            )
        return _unwrap_data(response.json())  # type: ignore[no-any-return]


async def list_documents(
    kb_id: str,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List documents in a knowledge base (paginated).

    Route: GET /api/v1/knowledge-bases/:id/knowledge?page=N&page_size=N
    Response: { "success": true, "data": [<Knowledge>], "total": N, "page": N, "page_size": N }
    """
    base_url = _build_base_url()
    page = (offset // limit) + 1
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/knowledge",
            params={"page": page, "page_size": limit},
            headers=_build_headers(),
        )
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora list documents failed: {response.text}",
                status_code=response.status_code,
            )
        return _unwrap_data(response.json())  # type: ignore[no-any-return]


async def hybrid_search(
    kb_id: str,
    query: str,
    limit: int = 10,
    **extra: Any,
) -> list[dict[str, Any]]:
    """Run hybrid search (vector + keyword) within a knowledge base.

    Route: POST /api/v1/knowledge-bases/:id/hybrid-search
    Request body (types.SearchParams): { "query_text": "...", "match_count": N }
    Response: { "success": true, "data": { "results": [<SearchResult>] } }
    """
    base_url = _build_base_url()
    payload: dict[str, Any] = {
        "query_text": query,
        "match_count": limit,
    }
    if extra:
        payload.update(extra)

    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/hybrid-search",
            json=payload,
            headers=_build_headers(),
        )
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora search failed: {response.text}",
                status_code=response.status_code,
            )
        data = _unwrap_data(response.json())  # type: ignore[no-any-return]
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("results", "data", "items"):
                if key in data and isinstance(data[key], list):
                    return list(data[key])
        return []


async def get_document_content(kb_id: str, knowledge_id: str) -> bytes | None:
    """Get the original document file content from WeKnora.

    Route: GET /api/v1/knowledge/:id/download
    This is a fallback; Thesis also stores raw bytes in MinIO.
    """
    base_url = _build_base_url()
    headers = _build_headers()
    headers["Accept"] = "application/octet-stream"
    async with httpx.AsyncClient(timeout=settings.WEKNORA_UPLOAD_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge/{knowledge_id}/download",
            headers=headers,
        )
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora download failed: {response.status_code}",
                status_code=response.status_code,
            )
        return bytes(response.content)
