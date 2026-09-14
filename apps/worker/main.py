"""ThesisGuard Dramatiq worker entry point.

Dramatiq worker 进程，从 Redis 队列消费任务。
使用 RedisBroker 将任务消息投递到 redis_queue_url_resolved（DB/2）。
每个 actor 配置了 max_retries 和 time_limit，超时或失败自动重试。

注意：Dramatiq actor 函数在同步上下文中执行，调用异步代码
（如 get_system_status）需要手动创建 event loop。
"""

from typing import Any

import dramatiq
from backend.common.config import settings
from dramatiq.brokers.redis import RedisBroker

# 配置 Redis 消息代理，使用独立的逻辑 DB /2 避免与缓存冲突
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

    # Dramatiq actor 是同步函数，需要创建独立 event loop 运行异步健康检查
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

    # 启动 worker 进程，worker_threads 并发消费
    worker = Worker(redis_broker, worker_threads=settings.WORKER_CONCURRENCY)
    worker.start()


if __name__ == "__main__":
    run_worker()
