"""Bounded lifecycle and durable provenance for the Evidence service test database.

TG_EVIDENCE_PG_LEDGER must name an explicit writable, absolute JSONL path.
No historical residue is adopted. An unacknowledged CREATE is indeterminate;
only this context's acknowledged CREATE plus exact catalog identity permits DROP.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import asyncpg
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_SQL = """SELECT d.oid::bigint AS oid, r.rolname AS owner,
    d.datdba::bigint AS owner_oid FROM pg_database d
    JOIN pg_roles r ON r.oid = d.datdba WHERE d.datname = $1"""


class EvidencePGCleanupError(RuntimeError):
    """An owned resource could not be safely released; execution must stop."""


class Ledger:
    def __init__(self, path: Path, context: dict[str, Any]) -> None:
        if not path.is_absolute():
            raise ValueError("TG_EVIDENCE_PG_LEDGER must be an absolute path")
        self.path = path
        self.context = context

    def record(self, event: str, **details: Any) -> None:
        row = {**self.context, "time": datetime.now(UTC).isoformat(), "event": event, **details}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())


async def run_tool(argv: list[str], env: dict[str, str], *, seconds: int = 10) -> str:
    result = await asyncio.to_thread(
        subprocess.run,
        argv,
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=seconds,
    )
    return str(result.stdout).strip()


async def preflight(env: dict[str, str], ledger: Ledger) -> str:
    alembic = shutil.which("alembic", path=env.get("PATH"))
    if alembic is None or not Path(alembic).is_absolute():
        raise RuntimeError("Alembic is not discoverable in the command-local PATH")
    python_version = await run_tool([sys.executable, "--version"], env)
    pytest_version = await run_tool(["/opt/homebrew/bin/pytest", "--version"], env)
    child = json.loads(
        await run_tool(
            [
                sys.executable,
                "-c",
                "import json,shutil; print(json.dumps({'alembic':shutil.which('alembic')}))",
            ],
            env,
        )
    )
    if child.get("alembic") != alembic:
        raise RuntimeError("Alembic discovery differs in the actual child environment")
    alembic_version = await run_tool([alembic, "--version"], env)
    heads = await run_tool([alembic, "-c", "migrations/alembic.ini", "heads"], env)
    if len(heads.splitlines()) != 1 or not heads.endswith("(head)"):
        raise RuntimeError("Expected one Alembic head before creating any database")
    ledger.record(
        "tools_checked",
        python=sys.executable,
        python_version=python_version,
        pytest="/opt/homebrew/bin/pytest",
        pytest_version=pytest_version,
        alembic=alembic,
        child_alembic=child["alembic"],
        alembic_version=alembic_version,
        heads=heads,
    )
    return alembic


@asynccontextmanager
async def disposable_sessionmaker(
    admin_database_url: str, *, node: str
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    url = make_url(admin_database_url)
    if (
        (url.drivername, url.host, url.port, url.database)
        != ("postgresql+asyncpg", "127.0.0.1", 15432, "postgres")
        or not url.username
        or url.query
    ):
        raise ValueError("Only the existing 127.0.0.1:15432/postgres admin target is allowed")
    ledger_path = os.environ.get("TG_EVIDENCE_PG_LEDGER")
    if not ledger_path or not node:
        raise ValueError(
            "An explicit TG_EVIDENCE_PG_LEDGER and pytest node are required before CREATE"
        )
    attempt = uuid4().hex
    name = f"tg_wp04_service_{attempt}"
    ledger = Ledger(
        Path(ledger_path),
        {
            "run_id": os.environ.get("TG_EVIDENCE_PG_RUN_ID") or uuid4().hex,
            "attempt_id": attempt,
            "node": node,
            "name": name,
            "host": url.host,
            "port": url.port,
            "admin_database": url.database,
        },
    )
    # This durable event precedes every tool/connection/CREATE attempt.
    ledger.record("attempt", status="PRE_ATTEMPT")
    env = {
        **os.environ,
        "DATABASE_URL": url.set(database=name).render_as_string(hide_password=False),
    }
    connect_kwargs = {
        "user": url.username,
        "password": url.password,
        "host": url.host,
        "port": url.port,
        "database": url.database,
        "timeout": 10,
        "command_timeout": 10,
    }
    admin: Any = None
    engine: Any = None
    identity: dict[str, Any] | None = None
    primary: BaseException | None = None
    phase = "preflight"
    try:
        alembic = await preflight(env, ledger)
        phase = "admin_preflight"
        admin = await asyncpg.connect(**connect_kwargs)
        target = await admin.fetchrow("SELECT current_database(), current_user")
        if (
            not target
            or target["current_database"] != "postgres"
            or target["current_user"] != url.username
        ):
            raise RuntimeError("Connected admin database/role differs from the declared target")
        can_create = await admin.fetchval(
            "SELECT rolcreatedb OR rolsuper FROM pg_roles WHERE rolname = current_user"
        )
        if not can_create or await admin.fetchrow(IDENTITY_SQL, name) is not None:
            raise RuntimeError("CREATE permission missing or generated exact name already exists")
        ledger.record("target_checked", status="ABSENT", owner=url.username)
        phase = "create"
        ledger.record("create_sent")
        try:
            status = await admin.execute(f'CREATE DATABASE "{name}"')
        except BaseException as exc:
            # A server rejection is definitive; connection-class errors/lost replies are not.
            sqlstate = exc.sqlstate if isinstance(exc, asyncpg.PostgresError) else None
            definitive = bool(sqlstate) and not str(sqlstate).startswith(("08", "57"))
            try:
                ledger.record(
                    "create_failed",
                    status="NOT_CREATED" if definitive else "INDETERMINATE",
                    ownership="NONE" if definitive else "UNKNOWN",
                    error_type=type(exc).__name__,
                )
            except Exception as log_error:
                exc.add_note(
                    f"CREATE failure recording failed: {type(log_error).__name__}; target={name}"
                )
            raise
        if status != "CREATE DATABASE":
            ledger.record("create_failed", status="INDETERMINATE", ownership="UNKNOWN")
            raise RuntimeError("CREATE acknowledgement is indeterminate; no automatic DROP")
        phase = "confirm"
        row = await admin.fetchrow(IDENTITY_SQL, name)
        if not row:
            ledger.record("create_failed", status="INDETERMINATE", ownership="UNKNOWN")
            raise RuntimeError(
                "Acknowledged CREATE has no exact catalog identity; no automatic DROP"
            )
        identity = dict(row)
        ledger.record("created", status="CONFIRMED", **identity)
        await admin.close()
        admin = None
        ledger.record("admin_closed", stage="setup")
        phase = "migration"
        await run_tool(
            [alembic, "-c", "migrations/alembic.ini", "upgrade", "head"], env, seconds=60
        )
        ledger.record("migrated")
        phase = "engine"
        engine = create_async_engine(env["DATABASE_URL"], pool_pre_ping=True)
        phase = "sessionmaker"
        maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
        ledger.record("ready")
        phase = "test_body"
        yield maker
    except BaseException as exc:
        # aclose() is normal fixture teardown, not a primary test failure.
        if isinstance(exc, GeneratorExit):
            raise
        primary = exc
        # Error types/codes are sufficient here; exception text may contain credentials.
        try:
            ledger.record("primary_error", phase=phase, error_type=type(exc).__name__)
            if phase == "confirm" and identity is None:
                ledger.record("create_failed", status="INDETERMINATE", ownership="UNKNOWN")
        except Exception as log_error:
            exc.add_note(f"Provenance recording failed: {type(log_error).__name__}; target={name}")
        raise
    finally:
        errors: list[str] = []

        async def close_resource(resource: Any, method: str, event: str) -> None:
            try:
                await asyncio.wait_for(getattr(resource, method)(), timeout=10)
                ledger.record(event)
            except BaseException as exc:
                errors.append(f"{event}:{type(exc).__name__}")

        if engine is not None:
            await close_resource(engine, "dispose", "engine_disposed")
        if admin is not None:
            await close_resource(admin, "close", "admin_closed")
        if identity is not None and not errors:
            cleanup: Any = None
            try:
                cleanup = await asyncpg.connect(**connect_kwargs)
                current = await cleanup.fetchrow(IDENTITY_SQL, name)
                if current is None or dict(current) != identity:
                    raise EvidencePGCleanupError("Exact name/OID/owner changed; DROP forbidden")
                connections = await cleanup.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = $1", name
                )
                ledger.record("cleanup_checked", **identity, connections=connections)
                if connections != 0:
                    raise EvidencePGCleanupError(
                        "Target has unreleased/external connections; DROP forbidden"
                    )
                ledger.record("drop_sent", **identity)
                status = await cleanup.execute(f'DROP DATABASE "{name}"')
                if (
                    status != "DROP DATABASE"
                    or await cleanup.fetchrow(IDENTITY_SQL, name) is not None
                ):
                    raise EvidencePGCleanupError("DROP outcome not confirmed")
                ledger.record("dropped", status="ABSENT", **identity)
            except BaseException as exc:
                errors.append(f"database_cleanup:{type(exc).__name__}")
            finally:
                if cleanup is not None:
                    await close_resource(cleanup, "close", "cleanup_admin_closed")
        if errors:
            detail = f"Evidence PostgreSQL cleanup failed; target={name}; ledger={ledger.path}; errors={errors}"
            try:
                ledger.record("cleanup_failed", errors=errors, **(identity or {}))
            except Exception as log_error:
                detail += f"; ledger_error={type(log_error).__name__}"
            if primary is not None:
                primary.add_note(detail)
            else:
                raise EvidencePGCleanupError(detail)
