"""ThesisGuard Dramatiq worker entry point."""

from typing import Any

import dramatiq
from backend.common.config import settings
from dramatiq.brokers.redis import RedisBroker

# Configure Dramatiq broker
redis_broker = RedisBroker(url=settings.redis_queue_url_resolved)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=3, time_limit=60000)
def system_health_task() -> dict[str, Any]:
    """Test task that verifies system health.

    This task can be dispatched by the API and will be consumed by the worker.
    Returns a dict with system status information.
    """
    import asyncio

    from backend.common.health import get_system_status

    # Run the async health check in a sync context
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(get_system_status())
        return result
    finally:
        loop.close()


@dramatiq.actor(max_retries=3, time_limit=300000)
def echo_task(message: str = "hello") -> dict[str, str]:
    """Simple echo task for testing."""
    return {"echo": message, "status": "completed"}


def run_worker() -> None:
    """Run the Dramatiq worker."""
    from dramatiq.worker import Worker

    worker = Worker(redis_broker, worker_threads=settings.WORKER_CONCURRENCY)
    worker.start()


if __name__ == "__main__":
    run_worker()
