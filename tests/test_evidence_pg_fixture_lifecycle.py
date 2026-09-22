"""Infrastructure fault injection; deterministic tests never connect to PostgreSQL."""

from __future__ import annotations

import asyncio
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, cast

import asyncpg
import pytest

from tests import test_evidence_services as service_tests


class FakeAdmin:
    """Model CREATE acknowledgement and exact catalog identity without a server."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self.created: list[str] = []
        self.dropped: list[str] = []
        self.identity: dict[str, Any] | None = None

    async def connect(self, **kwargs: Any) -> FakeAdmin:
        self.events.append("connect")
        return self

    async def execute(self, query: str, *args: Any) -> str:
        if query.startswith("CREATE DATABASE"):
            name = query.split('"')[1]
            self.created.append(name)
            self.identity = {"oid": 1234, "owner": "thesisguard", "owner_oid": 10}
            self.events.append("create")
            return "CREATE DATABASE"
        if query.startswith("DROP DATABASE"):
            self.dropped.append(query.split('"')[1])
            self.identity = None
            self.events.append("drop")
            return "DROP DATABASE"
        raise AssertionError("Unexpected or unsafe SQL: " + query)

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        if "FROM pg_database" in query:
            return self.identity
        return {"current_database": "postgres", "current_user": "thesisguard"}

    async def fetchval(self, query: str, *args: Any) -> Any:
        if "pg_stat_activity" in query:
            return 0
        if "pg_roles" in query:
            return True
        raise AssertionError(query)

    async def close(self) -> None:
        self.events.append("close")


def fixture_generator(request: pytest.FixtureRequest) -> Any:
    raw = cast(Any, service_tests.pg_sessionmaker).__wrapped__
    return raw(request) if "request" in inspect.signature(raw).parameters else raw()


async def test_migration_failure_releases_confirmed_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    admin = FakeAdmin()
    primary = subprocess.CalledProcessError(17, ["alembic", "upgrade", "head"])

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if "upgrade" in argv:
            raise primary
        if "heads" in argv:
            return subprocess.CompletedProcess(argv, 0, "000000000004 (head)\n", "")
        if "-c" in argv:
            return subprocess.CompletedProcess(
                argv, 0, json.dumps({"alembic": "/opt/miniconda3/bin/alembic"}), ""
            )
        return subprocess.CompletedProcess(argv, 0, "tool version", "")

    monkeypatch.setenv("TG_EVIDENCE_PG_LEDGER", str(tmp_path / "resources.jsonl"))
    monkeypatch.setattr(asyncpg, "connect", admin.connect)
    monkeypatch.setattr(subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError) as caught:
        await anext(fixture_generator(request))
    assert caught.value is primary
    assert len(admin.created) == 1
    assert admin.dropped == admin.created, "migration setup must release the acknowledged exact DB"
    assert admin.events[-1] == "close"


class InjectedFailure(RuntimeError):
    """Declared infrastructure fault, never a domain/migration correctness claim."""


class FakeEngine:
    def __init__(self, admin: FakeAdmin, fail: bool = False) -> None:
        self.admin = admin
        self.fail = fail

    async def dispose(self) -> None:
        self.admin.events.append("dispose")
        if self.fail:
            raise InjectedFailure("dispose")


def install_infrastructure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, fault: str = ""
) -> tuple[FakeAdmin, Path, InjectedFailure]:
    from tests import evidence_pg_fixture as lifecycle

    admin = FakeAdmin()
    ledger = tmp_path / "resources.jsonl"
    primary = InjectedFailure(fault)
    engine = FakeEngine(admin, fail=fault == "dispose")
    original_execute = admin.execute
    original_fetchrow = admin.fetchrow
    original_fetchval = admin.fetchval
    original_close = admin.close

    async def execute(query: str, *args: Any) -> str:
        if query.startswith("CREATE DATABASE") and fault == "create_rejected":
            raise asyncpg.InsufficientPrivilegeError("declared server rejection")
        if query.startswith("CREATE DATABASE") and fault == "create_uncertain":
            await original_execute(query, *args)
            raise ConnectionResetError("declared lost acknowledgement")
        if query.startswith("DROP DATABASE") and fault == "drop":
            raise primary
        return await original_execute(query, *args)

    async def fetchrow(query: str, *args: Any) -> dict[str, Any] | None:
        row = await original_fetchrow(query, *args)
        if "FROM pg_database" in query and "dispose" in admin.events and row:
            if fault == "oid_drift":
                return {**row, "oid": 9999}
            if fault == "owner_drift":
                return {**row, "owner": "other", "owner_oid": 99}
        if fault == "confirm" and "create" in admin.events and "FROM pg_database" in query:
            raise primary
        if fault == "target" and "current_database()" in query:
            return {"current_database": "thesisguard", "current_user": "thesisguard"}
        return row

    async def fetchval(query: str, *args: Any) -> Any:
        if "pg_stat_activity" in query and fault == "external_connection":
            return 1
        if "pg_stat_activity" in query and fault == "autovacuum_connection":
            return 0 if "backend_type = 'client backend'" in query else 1
        return await original_fetchval(query, *args)

    async def close() -> None:
        await original_close()
        if fault == "admin_close":
            raise primary

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if "upgrade" in argv and fault == "migration":
            raise primary
        if "heads" in argv:
            if fault == "heads":
                raise primary
            stdout = "000000000004 (head)\n"
        elif "-c" in argv:
            stdout = json.dumps(
                {"alembic": "different" if fault == "child" else "/opt/miniconda3/bin/alembic"}
            )
        else:
            stdout = "tool version"
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    def engine_factory(*args: Any, **kwargs: Any) -> FakeEngine:
        if fault == "engine":
            raise primary
        return engine

    def sessionmaker_factory(*args: Any, **kwargs: Any) -> Any:
        if fault == "sessionmaker":
            raise primary
        assert kwargs == {"expire_on_commit": False, "autoflush": False}
        return object()

    monkeypatch.setenv("TG_EVIDENCE_PG_LEDGER", str(ledger))
    monkeypatch.setattr(admin, "execute", execute)
    monkeypatch.setattr(admin, "fetchrow", fetchrow)
    monkeypatch.setattr(admin, "fetchval", fetchval)
    monkeypatch.setattr(admin, "close", close)
    monkeypatch.setattr(lifecycle.asyncpg, "connect", admin.connect)
    monkeypatch.setattr(lifecycle.subprocess, "run", run)
    monkeypatch.setattr(
        lifecycle.shutil,
        "which",
        lambda *args, **kwargs: None if fault == "tool" else "/opt/miniconda3/bin/alembic",
    )
    monkeypatch.setattr(lifecycle, "create_async_engine", engine_factory)
    monkeypatch.setattr(lifecycle, "async_sessionmaker", sessionmaker_factory)
    return admin, ledger, primary


def records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


@pytest.mark.parametrize("fault", ["tool", "child", "heads", "target"])
async def test_preflight_failure_creates_zero_databases(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest, fault: str
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path, fault=fault)
    with pytest.raises((RuntimeError, InjectedFailure)):
        await anext(fixture_generator(request))
    assert admin.created == []
    assert admin.dropped == []
    assert records(ledger)[0]["event"] == "attempt"
    assert not any(row["event"] == "create_sent" for row in records(ledger))


@pytest.mark.parametrize("fault", ["create_rejected", "create_uncertain", "confirm"])
async def test_unconfirmed_create_never_adopts_or_drops_a_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest, fault: str
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path, fault=fault)
    with pytest.raises((asyncpg.InsufficientPrivilegeError, ConnectionResetError, InjectedFailure)):
        await anext(fixture_generator(request))
    events = records(ledger)
    failure = next(row for row in events if row["event"] == "create_failed")
    assert failure["status"] == ("NOT_CREATED" if fault == "create_rejected" else "INDETERMINATE")
    assert admin.dropped == []
    assert admin.events[-1] == "close"
    assert not any(row["event"] == "created" for row in events)


@pytest.mark.parametrize("fault", ["migration", "engine", "sessionmaker"])
async def test_setup_exception_releases_exact_owned_database_and_preserves_primary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest, fault: str
) -> None:
    admin, ledger, primary = install_infrastructure(monkeypatch, tmp_path, fault=fault)
    with pytest.raises(InjectedFailure) as caught:
        await anext(fixture_generator(request))
    assert caught.value is primary
    assert admin.dropped == admin.created
    assert len(admin.created) == 1
    assert admin.events[-1] == "close"
    assert any(row["event"] == "dropped" for row in records(ledger))
    if fault == "sessionmaker":
        assert admin.events.index("dispose") < admin.events.index("drop")
    assert not getattr(primary, "__notes__", [])


@pytest.mark.parametrize("body_fault", [False, True])
async def test_normal_and_body_exception_release_before_finishing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
    body_fault: bool,
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path)
    generator = fixture_generator(request)
    await anext(generator)
    if body_fault:
        primary = InjectedFailure("test body")
        with pytest.raises(InjectedFailure) as caught:
            await generator.athrow(primary)
        assert caught.value is primary
        assert not getattr(primary, "__notes__", [])
    else:
        await generator.aclose()
    assert admin.dropped == admin.created
    assert admin.events.index("dispose") < admin.events.index("drop")
    events = records(ledger)
    confirmed = next(row for row in events if row["event"] == "created")
    dropped = next(row for row in events if row["event"] == "dropped")
    assert confirmed["oid"] == dropped["oid"] == 1234
    assert confirmed["owner"] == dropped["owner"] == "thesisguard"
    assert events[-1]["event"] == "cleanup_admin_closed"


async def test_internal_autovacuum_does_not_block_owned_database_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path, fault="autovacuum_connection")
    generator = fixture_generator(request)
    await anext(generator)
    await generator.aclose()

    assert admin.dropped == admin.created
    checked = next(row for row in records(ledger) if row["event"] == "cleanup_checked")
    assert checked["connections"] == 0


@pytest.mark.parametrize(
    "fault", ["drop", "dispose", "external_connection", "oid_drift", "owner_drift"]
)
@pytest.mark.parametrize("body_fault", [False, True])
async def test_cleanup_errors_are_explicit_and_never_mask_primary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
    fault: str,
    body_fault: bool,
) -> None:
    from tests.evidence_pg_fixture import EvidencePGCleanupError

    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path, fault=fault)
    generator = fixture_generator(request)
    await anext(generator)
    if body_fault:
        primary = InjectedFailure("test body")
        with pytest.raises(InjectedFailure) as caught:
            await generator.athrow(primary)
        assert caught.value is primary
        assert any("cleanup failed" in note for note in primary.__notes__)
    else:
        with pytest.raises(EvidencePGCleanupError, match="cleanup failed"):
            await generator.aclose()
    assert admin.dropped == []
    assert records(ledger)[-1]["event"] == "cleanup_failed"
    assert len(admin.created) == 1
    if fault != "dispose":
        assert admin.events[-1] == "close"


async def test_setup_admin_close_failure_does_not_expand_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    admin, ledger, primary = install_infrastructure(monkeypatch, tmp_path, fault="admin_close")
    with pytest.raises(InjectedFailure) as caught:
        await anext(fixture_generator(request))
    assert caught.value is primary
    assert admin.dropped == []
    assert records(ledger)[-1]["event"] == "cleanup_failed"
    assert any("cleanup failed" in note for note in primary.__notes__)


async def test_run_node_and_attempt_provenance_are_independent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from tests.evidence_pg_fixture import disposable_sessionmaker

    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path)
    for run, node in [("run-one", "node-one"), ("run-two", "node-two")]:
        monkeypatch.setenv("TG_EVIDENCE_PG_RUN_ID", run)
        async with disposable_sessionmaker(service_tests.DEFAULT_ADMIN_DATABASE_URL, node=node):
            pass
    attempts = [row for row in records(ledger) if row["event"] == "attempt"]
    assert [(row["run_id"], row["node"]) for row in attempts] == [
        ("run-one", "node-one"),
        ("run-two", "node-two"),
    ]
    assert len({row["name"] for row in attempts}) == 2
    assert len({row["attempt_id"] for row in attempts}) == 2
    assert admin.dropped == admin.created


# Real cases are deliberately opt-in and separately selectable with -k real_postgres.
# They call the actual pg_sessionmaker async generator without registering the
# 378 business tests as a pytest plugin or collecting/executing that suite.
@pytest.mark.parametrize("scenario", ["normal", "migration_fault", "engine_fault", "body_fault"])
async def test_real_postgres_resource_lifecycle(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest, scenario: str
) -> None:
    import os

    from sqlalchemy import text

    from tests import evidence_pg_fixture as lifecycle

    if os.environ.get("TG_RUN_PG_FIXTURE_LIFECYCLE_REAL") != "1":
        pytest.skip("real disposable DB operations require explicit opt-in")
    ledger_path = Path(os.environ["TG_EVIDENCE_PG_LEDGER"])
    existing = records(ledger_path)
    sent = [row for row in existing if row.get("event") == "create_sent"]
    assert len(sent) < 4, "task-wide real CREATE budget exhausted; no additional CREATE permitted"
    assert not any(row.get("event") == "cleanup_failed" for row in existing)
    plan_path = Path(
        "/Users/qianduoduo/Desktop/AI_app/ThesisGuard/docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json"
    )
    plan = json.loads(await asyncio.to_thread(plan_path.read_text))
    expected = {row["name"]: (row["oid"], row["owner"]) for row in plan["per_name"]}

    async def catalog() -> list[dict[str, Any]]:
        from sqlalchemy.engine import make_url

        url = make_url(service_tests.DEFAULT_ADMIN_DATABASE_URL)
        conn = await asyncpg.connect(
            user=url.username,
            password=url.password,
            host="127.0.0.1",
            port=15432,
            database="postgres",
            timeout=10,
            command_timeout=10,
            server_settings={"default_transaction_read_only": "on"},
        )
        try:
            return [
                dict(row)
                for row in await conn.fetch(
                    "SELECT d.datname AS name, d.oid::bigint AS oid, r.rolname AS owner "
                    "FROM pg_database d JOIN pg_roles r ON r.oid=d.datdba ORDER BY d.datname"
                )
            ]
        finally:
            await conn.close()

    before = await catalog()
    before_map = {row["name"]: (row["oid"], row["owner"]) for row in before}
    assert {name: before_map.get(name) for name in expected} == expected
    audit = lifecycle.Ledger(
        ledger_path, {"run_id": os.environ["TG_EVIDENCE_PG_RUN_ID"], "node": request.node.nodeid}
    )
    audit.record("catalog_before", databases=before, historical_unknown_preserved=45)
    declared = InjectedFailure(scenario)
    original_run = lifecycle.run_tool

    async def run_tool(argv: list[str], env: dict[str, str], *, seconds: int = 10) -> str:
        if scenario == "migration_fault" and "upgrade" in argv:
            raise subprocess.CalledProcessError(19, argv)
        return await original_run(argv, env, seconds=seconds)

    def engine_fault(*args: Any, **kwargs: Any) -> Any:
        raise declared

    if scenario == "migration_fault":
        monkeypatch.setattr(lifecycle, "run_tool", run_tool)
    if scenario == "engine_fault":
        monkeypatch.setattr(lifecycle, "create_async_engine", engine_fault)
    audit.record("declared_scenario", scenario=scenario, fault_injection=scenario != "normal")
    generator = fixture_generator(request)
    if scenario == "migration_fault":
        with pytest.raises(subprocess.CalledProcessError) as migration_error:
            await anext(generator)
        assert migration_error.value.returncode == 19
        assert not getattr(migration_error.value, "__notes__", [])
    elif scenario == "engine_fault":
        with pytest.raises(InjectedFailure) as caught:
            await anext(generator)
        assert caught.value is declared
        assert not getattr(declared, "__notes__", [])
    else:
        maker = await anext(generator)
        assert maker.kw["expire_on_commit"] is False and maker.kw["autoflush"] is False
        async with maker() as session:
            assert await session.scalar(text("SELECT 1")) == 1
            await session.rollback()
        if scenario == "body_fault":
            with pytest.raises(InjectedFailure) as caught:
                await generator.athrow(declared)
            assert caught.value is declared
            assert not getattr(declared, "__notes__", [])
        else:
            await generator.aclose()
    events = records(ledger_path)[len(existing) :]
    created = [row for row in events if row["event"] == "created"]
    dropped = [row for row in events if row["event"] == "dropped"]
    assert len(created) == len(dropped) == 1
    for field in ("run_id", "attempt_id", "node", "name", "oid", "owner", "owner_oid"):
        assert created[0][field] == dropped[0][field]
    assert not any(row["event"] in {"cleanup_failed", "create_failed"} for row in events)
    after = await catalog()
    audit.record("catalog_after", databases=after, historical_unknown_preserved=45)
    assert after == before
    assert created[0]["name"] not in {row["name"] for row in after}


async def test_create_is_preceded_by_durable_run_node_target_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path)
    original_execute = admin.execute

    async def execute(query: str, *args: Any) -> str:
        if query.startswith("CREATE DATABASE"):
            persisted = records(ledger)
            assert [row["event"] for row in persisted] == [
                "attempt",
                "tools_checked",
                "target_checked",
                "create_sent",
            ]
            first = persisted[0]
            assert first["node"] == request.node.nodeid
            assert first["name"] == query.split('"')[1]
            assert (first["host"], first["port"]) == ("127.0.0.1", 15432)
            assert first["run_id"] and first["attempt_id"]
        return await original_execute(query, *args)

    monkeypatch.setattr(admin, "execute", execute)
    generator = fixture_generator(request)
    await anext(generator)
    await generator.aclose()
    persisted = records(ledger)
    created = next(row for row in persisted if row["event"] == "created")
    assert created["status"] == "CONFIRMED"
    assert (created["oid"], created["owner"], created["owner_oid"]) == (1234, "thesisguard", 10)
    assert "DATABASE_URL" not in ledger.read_text()
    assert "password" not in ledger.read_text()


@pytest.mark.parametrize("invalid_ledger", ["missing", "relative", "unwritable"])
async def test_no_durable_ledger_means_zero_create(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
    invalid_ledger: str,
) -> None:
    admin, _, _ = install_infrastructure(monkeypatch, tmp_path)
    if invalid_ledger == "missing":
        monkeypatch.delenv("TG_EVIDENCE_PG_LEDGER")
    else:
        monkeypatch.setenv(
            "TG_EVIDENCE_PG_LEDGER",
            "relative.jsonl"
            if invalid_ledger == "relative"
            else str(tmp_path / "absent" / "resources.jsonl"),
        )
    with pytest.raises((ValueError, FileNotFoundError)):
        await anext(fixture_generator(request))
    assert admin.created == admin.dropped == []
    assert admin.events == []


@pytest.mark.parametrize("create_error", [asyncpg.AdminShutdownError, asyncpg.PostgresError])
async def test_shutdown_or_unclassified_create_reply_is_indeterminate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    request: pytest.FixtureRequest,
    create_error: type[asyncpg.PostgresError],
) -> None:
    admin, ledger, _ = install_infrastructure(monkeypatch, tmp_path)
    original_execute = admin.execute

    async def execute(query: str, *args: Any) -> str:
        result = await original_execute(query, *args)
        if query.startswith("CREATE DATABASE"):
            raise create_error("declared shutdown/unclassified reply")
        return result

    monkeypatch.setattr(admin, "execute", execute)
    with pytest.raises(create_error):
        await anext(fixture_generator(request))
    assert admin.dropped == []
    failure = next(row for row in records(ledger) if row["event"] == "create_failed")
    assert (failure["status"], failure["ownership"]) == ("INDETERMINATE", "UNKNOWN")


async def test_create_error_is_preserved_if_failure_recording_also_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, request: pytest.FixtureRequest
) -> None:
    from tests.evidence_pg_fixture import Ledger

    admin, _, _ = install_infrastructure(monkeypatch, tmp_path, fault="create_rejected")
    original_record = Ledger.record

    def record(self: Ledger, event: str, **details: Any) -> None:
        if event == "create_failed":
            raise OSError("declared ledger failure after CREATE rejection")
        original_record(self, event, **details)

    monkeypatch.setattr(Ledger, "record", record)
    with pytest.raises(asyncpg.InsufficientPrivilegeError) as caught:
        await anext(fixture_generator(request))
    assert any("recording failed" in note for note in caught.value.__notes__)
    assert admin.created == admin.dropped == []
    assert admin.events[-1] == "close"
