"""Focused regression tests for the code-review repair batch.

These tests intentionally avoid external services where a pure/unit-level
assertion is sufficient. Database-backed assertions remain in the existing
PostgreSQL suites and are reported separately when the services are absent.
"""

import signal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from apps.worker import main as worker_main
from backend.common.config import Settings
from backend.common.storage import StorageClient
from backend.instrument import services as instrument_services
from backend.watchlist.schemas import WatchlistUpdateRequest
from botocore.exceptions import ClientError
from pydantic import ValidationError


class _FakeWorker:
    def __init__(self, start_error: BaseException | None = None) -> None:
        self.start_error = start_error
        self.start_calls = 0
        self.stop_calls = 0
        self.join_calls = 0

    def start(self) -> None:
        self.start_calls += 1
        if self.start_error is not None:
            raise self.start_error

    def stop(self) -> None:
        self.stop_calls += 1

    def join(self) -> None:
        self.join_calls += 1


class _FakeSignal:
    def __init__(self) -> None:
        self.handlers: dict[int, object] = {
            signal.SIGTERM: "original-term",
            signal.SIGINT: "original-int",
        }

    def signal(self, signum: int, handler: object) -> object:
        previous = self.handlers[signum]
        self.handlers[signum] = handler
        return previous


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
def test_worker_stays_idle_until_shutdown_signal(signum: int) -> None:
    """An idle worker waits for shutdown instead of relying on join()."""
    worker = _FakeWorker()
    signal_api = _FakeSignal()

    def wait_for_shutdown(event) -> None:
        assert not event.is_set()
        handler = signal_api.handlers[signum]
        assert callable(handler)
        handler(signum, None)
        assert event.is_set()

    worker_main.run_worker(
        worker_factory=lambda: worker,
        wait_for_shutdown=wait_for_shutdown,
        signal_api=signal_api,
    )

    assert worker.start_calls == 1
    assert worker.stop_calls == 1
    assert worker.join_calls == 0


def test_repeated_shutdown_signals_stop_worker_only_once() -> None:
    """Repeated shutdown requests are safe and idempotent."""
    worker = _FakeWorker()
    signal_api = _FakeSignal()

    def wait_for_shutdown(event) -> None:
        for signum in (signal.SIGTERM, signal.SIGTERM, signal.SIGINT):
            handler = signal_api.handlers[signum]
            assert callable(handler)
            handler(signum, None)
        assert event.is_set()

    worker_main.run_worker(
        worker_factory=lambda: worker,
        wait_for_shutdown=wait_for_shutdown,
        signal_api=signal_api,
    )

    assert worker.stop_calls == 1


@pytest.mark.parametrize("exception", [KeyboardInterrupt, SystemExit])
def test_worker_exception_cleanup_is_shared_and_restores_signals(exception: type[BaseException]) -> None:
    """Interrupt-style exits stop a started worker and restore signal handlers."""
    worker = _FakeWorker()
    signal_api = _FakeSignal()
    original_handlers = dict(signal_api.handlers)

    def wait_for_shutdown(_event) -> None:
        raise exception()

    with pytest.raises(exception):
        worker_main.run_worker(
            worker_factory=lambda: worker,
            wait_for_shutdown=wait_for_shutdown,
            signal_api=signal_api,
        )

    assert worker.stop_calls == 1
    assert signal_api.handlers == original_handlers


def test_worker_start_failure_does_not_stop_or_wait_and_restores_signals() -> None:
    """A worker that never started must not receive an unnecessary stop call."""
    worker = _FakeWorker(start_error=RuntimeError("start failed"))
    signal_api = _FakeSignal()
    original_handlers = dict(signal_api.handlers)
    wait_calls = 0

    def wait_for_shutdown(_event) -> None:
        nonlocal wait_calls
        wait_calls += 1

    with pytest.raises(RuntimeError, match="start failed"):
        worker_main.run_worker(
            worker_factory=lambda: worker,
            wait_for_shutdown=wait_for_shutdown,
            signal_api=signal_api,
        )

    assert worker.start_calls == 1
    assert worker.stop_calls == 0
    assert wait_calls == 0
    assert signal_api.handlers == original_handlers


def test_production_settings_reject_development_secret() -> None:
    """Production configuration cannot silently use the development secret."""
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            APP_ENV="production",
            SECRET_KEY="dev-secret-key-change-in-production",
            API_DEBUG=False,
        )


def test_compose_requires_secrets_and_binds_dev_ports_to_loopback() -> None:
    """The development Compose profile must not publish services publicly."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "POSTGRES_PASSWORD:?" in compose
    assert "MINIO_SECRET_KEY:?" in compose
    assert '"127.0.0.1:${POSTGRES_HOST_PORT:-15432}:5432"' in compose
    assert '"127.0.0.1:6379:6379"' in compose
    assert 'API_DEBUG: ${API_DEBUG:-false}' in compose


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("600519.SH", ("600519", "SSE")),
        ("SZ.301128", ("301128", "SZSE")),
        ("300260:SZE", ("300260", "SZSE")),
        ("FOMC", ("FOMC", None)),
    ],
)
def test_instrument_query_parses_symbol_and_exchange(query: str, expected: tuple[str, str | None]) -> None:
    """Qualified symbols resolve by the stable symbol/exchange identity."""
    assert instrument_services.parse_instrument_query(query) == expected


def test_watchlist_update_rejects_unknown_status() -> None:
    """Watchlist state is a closed domain value, not arbitrary text."""
    with pytest.raises(ValidationError):
        WatchlistUpdateRequest(research_status="NOT_A_STATUS")


def test_storage_does_not_turn_access_denied_into_not_found() -> None:
    """MinIO authorization failures must remain distinguishable from 404."""
    client = MagicMock()
    client.get_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "denied"}},
        "GetObject",
    )
    storage = StorageClient()
    storage._client = client

    with pytest.raises(ClientError):
        storage.get_object("private/report.pdf")


def test_task_error_response_does_not_echo_exception_text(client) -> None:
    """API task errors expose a stable safe message, never broker details."""
    with patch("apps.api.routers.tasks.echo_task") as mock_task:
        mock_task.send.side_effect = Exception("redis://:super-secret@host:6379/2")

        response = client.post("/api/v1/tasks/echo", json={"message": "hello"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Task queue unavailable"
    assert "super-secret" not in response.text
