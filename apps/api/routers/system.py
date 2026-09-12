"""System status endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.db.session import get_db
from backend.common.health import get_system_status

router = APIRouter(tags=["system"])


class ServiceStatus(BaseModel):
    status: str
    message: str


class SystemStatusResponse(BaseModel):
    status: str
    api: dict
    services: dict


@router.get("/system/status", response_model=SystemStatusResponse)
async def system_status():
    """Comprehensive system status check.

    Returns status of all core services: postgres, redis, object_storage, worker.
    """
    return await get_system_status()


@router.get("/system/status/postgres")
async def postgres_status(db: AsyncSession = Depends(get_db)):
    """PostgreSQL specific status."""
    from backend.common.health import check_postgres

    return await check_postgres()


@router.get("/system/status/redis")
async def redis_status():
    """Redis specific status."""
    from backend.common.health import check_redis

    return await check_redis()


@router.get("/system/status/storage")
async def storage_status():
    """MinIO/Object Storage specific status."""
    from backend.common.health import check_minio

    return await check_minio()
