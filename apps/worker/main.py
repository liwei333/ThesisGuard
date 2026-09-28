"""ThesisGuard Dramatiq worker entry point.

Dramatiq worker 进程，从 Redis 队列消费任务。
使用 RedisBroker 将任务消息投递到 redis_queue_url_resolved（DB/2）。
每个 actor 配置了 max_retries 和 time_limit，超时或失败自动重试。

注意：Dramatiq actor 函数在同步上下文中执行，调用异步代码
（如 get_system_status）需要手动创建 event loop。
"""

import signal
import threading
from collections.abc import Callable
from types import FrameType
from typing import Any, Protocol

import dramatiq
from backend.common.config import settings
from dramatiq.brokers.redis import RedisBroker

# 配置 Redis 消息代理，使用独立的逻辑 DB /2 避免与缓存冲突
redis_broker = RedisBroker(url=settings.redis_queue_url_resolved)
dramatiq.set_broker(redis_broker)


class _Worker(Protocol):
    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...


class _SignalAPI(Protocol):
    def signal(self, signum: int, handler: Any) -> Any:
        ...


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


def _wait_for_shutdown(shutdown_event: threading.Event) -> None:
    """Keep the worker process attached until a shutdown request arrives."""
    shutdown_event.wait()


def _run_worker_lifecycle(
    worker: _Worker,
    *,
    wait_for_shutdown: Callable[[threading.Event], None],
    signal_api: _SignalAPI,
) -> None:
    """Own worker startup, signal handling, waiting, and graceful shutdown."""
    shutdown_event = threading.Event()
    worker_started = False
    stop_called = False
    previous_handlers: dict[int, Any] = {}

    def stop_worker() -> None:
        nonlocal stop_called
        if stop_called:
            return
        stop_called = True
        worker.stop()

    def request_shutdown(_signum: int, _frame: FrameType | None) -> None:
        shutdown_event.set()
        if worker_started:
            stop_worker()

    try:
        for signum in (int(signal.SIGTERM), int(signal.SIGINT)):
            previous_handlers[signum] = signal_api.signal(signum, request_shutdown)

        # Worker.start() starts Dramatiq's consumer and worker threads.  It is
        # not a process lifetime primitive and may fail before the worker owns
        # any resources that need stopping.
        worker.start()
        worker_started = True
        wait_for_shutdown(shutdown_event)
    except (KeyboardInterrupt, SystemExit):
        if worker_started:
            stop_worker()
        raise
    finally:
        for signum, previous_handler in previous_handlers.items():
            signal_api.signal(signum, previous_handler)
        if worker_started:
            stop_worker()


def run_worker(
    *,
    worker_factory: Callable[[], _Worker] | None = None,
    wait_for_shutdown: Callable[[threading.Event], None] | None = None,
    signal_api: _SignalAPI = signal,
) -> None:
    """Run the Dramatiq worker until it receives a shutdown request."""
    worker: _Worker
    if worker_factory is None:
        from dramatiq.worker import Worker

        worker = Worker(redis_broker, worker_threads=settings.WORKER_CONCURRENCY)
    else:
        worker = worker_factory()

    _run_worker_lifecycle(
        worker,
        wait_for_shutdown=wait_for_shutdown or _wait_for_shutdown,
        signal_api=signal_api,
    )


if __name__ == "__main__":
    run_worker()
