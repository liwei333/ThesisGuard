"""Credential-safe, read-only PostgreSQL catalog observer for the R4 verifier."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import asyncpg
from sqlalchemy.engine import make_url

from tests.test_evidence_services import DEFAULT_ADMIN_DATABASE_URL


EXPECTED_DRIVER = "postgresql+asyncpg"
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 15432
EXPECTED_DATABASE = "postgres"
EXPECTED_HISTORICAL_OWNER_OID = 10


CATALOG_SQL = """
SELECT d.datname AS name,
       d.oid::bigint AS oid,
       r.rolname AS owner,
       d.datdba::bigint AS owner_oid,
       count(a.pid)::bigint AS connections
FROM pg_database AS d
JOIN pg_roles AS r ON r.oid = d.datdba
LEFT JOIN pg_stat_activity AS a ON a.datname = d.datname
GROUP BY d.datname, d.oid, r.rolname, d.datdba
ORDER BY d.datname
"""


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temp, path)


async def _snapshot(output: Path, plan_path: Path) -> None:
    url = make_url(DEFAULT_ADMIN_DATABASE_URL)
    if (
        url.drivername,
        url.host,
        url.port,
        url.database,
    ) != (EXPECTED_DRIVER, EXPECTED_HOST, EXPECTED_PORT, EXPECTED_DATABASE):
        raise RuntimeError("candidate default PostgreSQL target differs from the authorized target")
    if not url.username or url.password is None or url.query:
        raise RuntimeError("candidate default PostgreSQL configuration is not safely usable")

    connection = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database=url.database,
        timeout=10,
        command_timeout=10,
        server_settings={"application_name": "thesisguard_r4_read_only_observer"},
    )
    try:
        target = await connection.fetchrow(
            "SELECT current_database() AS database, current_user AS role, "
            "current_setting('server_version') AS server_version"
        )
        can_create = await connection.fetchval(
            "SELECT rolcreatedb OR rolsuper FROM pg_roles WHERE rolname = current_user"
        )
        catalog = [dict(row) for row in await connection.fetch(CATALOG_SQL)]
    finally:
        await connection.close()

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    expected = {
        item["name"]: {
            "name": item["name"],
            "oid": item["oid"],
            "owner": item["owner"],
            "owner_oid": EXPECTED_HISTORICAL_OWNER_OID,
        }
        for item in plan["per_name"]
    }
    actual = {row["name"]: row for row in catalog}
    comparisons = []
    for name in sorted(expected):
        observed = actual.get(name)
        observed_identity = (
            None
            if observed is None
            else {key: observed[key] for key in ("name", "oid", "owner", "owner_oid")}
        )
        comparisons.append(
            {
                "name": name,
                "expected": expected[name],
                "observed": observed_identity,
                "matches": observed_identity == expected[name],
                "connections": None if observed is None else observed["connections"],
            }
        )

    payload = {
        "observed_at_utc": datetime.now(UTC).isoformat(),
        "target": {
            "driver": url.drivername,
            "host": url.host,
            "port": url.port,
            "admin_database": target["database"],
            "current_user": target["role"],
            "server_version": target["server_version"],
            "can_create_database": bool(can_create),
        },
        "catalog": catalog,
        "historical_unknown": {
            "expected_count": 45,
            "observed_count": len(comparisons),
            "all_identity_matches": all(item["matches"] for item in comparisons),
            "comparisons": comparisons,
        },
    }
    _atomic_json(output, payload)
    print(
        json.dumps(
            {
                "database": target["database"],
                "role": target["role"],
                "can_create_database": bool(can_create),
                "catalog_count": len(catalog),
                "historical_unknown_count": len(comparisons),
                "historical_unknown_all_identity_matches": all(
                    item["matches"] for item in comparisons
                ),
            },
            sort_keys=True,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    try:
        asyncio.run(_snapshot(args.output.resolve(), args.plan.resolve()))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error_type": type(exc).__name__}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
