"""System health check services."""

import asyncio
import functools
from typing import Dict, Any

from sqlalchemy import text

from backend.common.config import settings
from backend.common.db.session import async_engine
from backend.common.redis_client import redis_client
from backend.common.storage import storage


def with_timeout(seconds: float):
    """Decorator that adds a timeout to an async function."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                return {"status": "error", "message": "Connection timed out"}
        return wrapper
    return decorator


@with_timeout(3.0)
async def check_postgres() -> Dict[str, Any]:
    """Check PostgreSQL connectivity."""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await result.scalar()
        return {"status": "ok", "message": "Connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        r = redis_client.cache
        r.ping()
        return {"status": "ok", "message": "Connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_minio() -> Dict[str, Any]:
    """Check MinIO connectivity."""
    try:
        storage.client.list_buckets()
        return {"status": "ok", "message": "Service accessible"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_worker() -> Dict[str, Any]:
    """Check if worker queue (Redis) is reachable."""
    try:
        import redis as sync_redis
        queue_url = settings.redis_queue_url_resolved
        r = sync_redis.Redis.from_url(
            queue_url,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2,
        )
        r.ping()
        return {"status": "ok", "message": "Queue accessible"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


async def get_system_status() -> Dict[str, Any]:
    """Get complete system status."""
    # Run all checks concurrently
    results = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_minio(),
        check_worker(),
    )

    services = ["postgres", "redis", "object_storage", "worker"]
    status_map = {}
    all_ok = True

    for service, result in zip(services, results):
        status_map[service] = result
        if result["status"] != "ok":
            all_ok = False

    return {
        "status": "healthy" if all_ok else "degraded",
        "api": {"status": "ok", "version": settings.APP_VERSION},
        "services": status_map,
    }
