"""WeKnora HTTP adapter.

Communicates with the WeKnora knowledge service over HTTP.
Handles: knowledge base CRUD, document upload/status, and retrieval search.

This adapter is purely a communication layer — it does no business logic
validation. Callers must handle domain semantics.

Reference upstream: https://github.com/Tencent/WeKnora
Locked API snapshot: bccb4b151bae403508da77fbb174efc79dc47c1a
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
                return {"status": WeKnoraStatus.READY, "details": response.json()}
            return {
                "status": WeKnoraStatus.UNAVAILABLE,
                "http_status": response.status_code,
            }
    except httpx.RequestError as exc:
        logger.warning("WeKnora health check failed: %s", exc)
        return {"status": WeKnoraStatus.UNAVAILABLE, "error": str(exc)}


async def create_knowledge_base(name: str, description: str | None = None) -> dict[str, Any]:
    """Create a knowledge base in WeKnora. Returns the created KB record."""
    base_url = _build_base_url()
    payload: dict[str, Any] = {"name": name}
    if description:
        payload["description"] = description

    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-bases",
            json=payload,
        )
        if response.status_code not in (200, 201):
            raise WeKnoraError(
                f"WeKnora create KB failed: {response.text}",
                status_code=response.status_code,
            )
        return response.json()  # type: ignore[no-any-return]


async def list_knowledge_bases() -> list[dict[str, Any]]:
    """List all knowledge bases in WeKnora."""
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(f"{base_url}/api/v1/knowledge-bases")
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora list KBs failed: {response.text}",
                status_code=response.status_code,
            )
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "data" in data:
            return list(data["data"])
        return []


async def get_knowledge_base(kb_id: str) -> dict[str, Any]:
    """Get one knowledge base detail."""
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(f"{base_url}/api/v1/knowledge-bases/{kb_id}")
        if response.status_code == 404:
            return {}
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora get KB failed: {response.text}",
                status_code=response.status_code,
            )
        return response.json()  # type: ignore[no-any-return]


async def upload_document(
    kb_id: str,
    filename: str,
    file_content: bytes,
    content_type: str = "application/octet-stream",
) -> dict[str, Any]:
    """Upload a document to a WeKnora knowledge base."""
    base_url = _build_base_url()
    files = {"file": (filename, file_content, content_type)}

    async with httpx.AsyncClient(timeout=settings.WEKNORA_UPLOAD_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/documents",
            files=files,
        )
        if response.status_code not in (200, 201):
            raise WeKnoraError(
                f"WeKnora upload failed: {response.text}",
                status_code=response.status_code,
            )
        return response.json()  # type: ignore[no-any-return]


async def get_document_status(kb_id: str, document_id: str) -> dict[str, Any]:
    """Get processing status of a document."""
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/documents/{document_id}"
        )
        if response.status_code == 404:
            return {}
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora get document status failed: {response.text}",
                status_code=response.status_code,
            )
        return response.json()  # type: ignore[no-any-return]


async def list_documents(kb_id: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """List documents in a knowledge base."""
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.get(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/documents",
            params={"limit": limit, "offset": offset},
        )
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora list documents failed: {response.text}",
                status_code=response.status_code,
            )
        data = response.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "documents", "items"):
                if key in data and isinstance(data[key], list):
                    return list(data[key])
        return []


async def hybrid_search(
    kb_id: str,
    query: str,
    limit: int = 10,
    **filters: Any,
) -> dict[str, Any]:
    """Run hybrid search (vector + keyword) within a knowledge base."""
    base_url = _build_base_url()
    payload: dict[str, Any] = {
        "query": query,
        "limit": limit,
        "kb_id": kb_id,
    }
    if filters:
        payload["filters"] = filters

    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.post(
            f"{base_url}/api/v1/knowledge-search",
            json=payload,
        )
        if response.status_code != 200:
            raise WeKnoraError(
                f"WeKnora search failed: {response.text}",
                status_code=response.status_code,
            )
        return response.json()  # type: ignore[no-any-return]


async def delete_document(kb_id: str, document_id: str) -> bool:
    """Delete/retire a document from a knowledge base."""
    base_url = _build_base_url()
    async with httpx.AsyncClient(timeout=settings.WEKNORA_TIMEOUT) as client:
        response = await client.delete(
            f"{base_url}/api/v1/knowledge-bases/{kb_id}/documents/{document_id}"
        )
        if response.status_code in (200, 204):
            return True
        if response.status_code == 404:
            return False
        raise WeKnoraError(
            f"WeKnora delete document failed: {response.text}",
            status_code=response.status_code,
        )
