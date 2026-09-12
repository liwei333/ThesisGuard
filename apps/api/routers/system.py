"""System status endpoints."""

from typing import Any

from backend.common.db.session import get_db
from backend.common.health import get_system_status
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["system"])


class ServiceStatus(BaseModel):
    status: str
    message: str


class SystemStatusResponse(BaseModel):
    status: str
    api: dict[str, Any]
    services: dict[str, Any]


@router.get("/system/status", response_model=SystemStatusResponse)
async def system_status() -> dict[str, Any]:
    """Comprehensive system status check.

    Returns status of all core services: postgres, redis, object_storage, worker.
    """
    return await get_system_status()


@router.get("/system/status/postgres")
async def postgres_status(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """PostgreSQL specific status."""
    from backend.common.health import check_postgres

    return await check_postgres()


@router.get("/system/status/redis")
async def redis_status() -> dict[str, Any]:
    """Redis specific status."""
    from backend.common.health import check_redis

    return await check_redis()


@router.get("/system/status/storage")
async def storage_status() -> dict[str, Any]:
    """MinIO/Object Storage specific status."""
    from backend.common.health import check_minio

    return await check_minio()
