"""System health check services."""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from backend.common.config import settings
from backend.common.db.session import async_engine
from backend.common.redis_client import redis_client
from backend.common.storage import storage
from sqlalchemy import text

HealthResult = dict[str, Any]
HealthCheck = Callable[..., Awaitable[HealthResult]]
F = TypeVar("F", bound=HealthCheck)


def with_timeout(seconds: float) -> Callable[[F], F]:
    """Decorator that adds a timeout to an async function."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> HealthResult:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except TimeoutError:
                return {"status": "error", "message": "Connection timed out"}

        return cast(F, wrapper)

    return decorator


@with_timeout(3.0)
async def check_postgres() -> HealthResult:
    """Check PostgreSQL connectivity."""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        return {"status": "ok", "message": "Connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_redis() -> HealthResult:
    """Check Redis connectivity."""
    try:
        r = redis_client.cache
        r.ping()
        return {"status": "ok", "message": "Connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_minio() -> HealthResult:
    """Check MinIO connectivity."""
    try:
        storage.client.list_buckets()
        return {"status": "ok", "message": "Service accessible"}
    except Exception as e:
        return {"status": "error", "message": str(e)[:100]}


@with_timeout(3.0)
async def check_worker() -> HealthResult:
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


async def get_system_status() -> dict[str, Any]:
    """Get complete system status."""
    # Run all checks concurrently
    results = await asyncio.gather(
        check_postgres(),
        check_redis(),
        check_minio(),
        check_worker(),
    )

    services = ["postgres", "redis", "object_storage", "worker"]
    status_map: dict[str, HealthResult] = {}
    all_ok = True

    for service, result in zip(services, results, strict=True):
        status_map[service] = result
        if result["status"] != "ok":
            all_ok = False

    return {
        "status": "healthy" if all_ok else "degraded",
        "api": {"status": "ok", "version": settings.APP_VERSION},
        "services": status_map,
    }
