from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

import asyncpg
from sqlalchemy.engine import make_url

from tests.test_evidence_services import DEFAULT_ADMIN_DATABASE_URL


EVIDENCE = Path(__file__).resolve().parent
PLAN = Path(
    "/private/tmp/thesisguard-r5-verify.qabgRt/historical-main/docs/acceptance/"
    "TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/"
    "phase-a-20260916-exact-cleanup-plan.json"
)
CATALOG_SQL = """SELECT d.datname, d.oid::bigint AS oid, r.rolname AS owner,
    d.datdba::bigint AS owner_oid
FROM pg_database d JOIN pg_roles r ON r.oid = d.datdba ORDER BY d.datname"""
ACTIVITY_SQL = """SELECT
    count(*) FILTER (
        WHERE pid <> pg_backend_pid()
          AND backend_type = 'client backend'
          AND state = 'active'
    )::int AS external_active,
    count(*) FILTER (
        WHERE pid <> pg_backend_pid()
          AND datname LIKE 'tg_wp04_service_%'
    )::int AS external_tg_sessions
FROM pg_stat_activity"""


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(name: str, payload: object) -> None:
    (EVIDENCE / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def canonical_hash(rows: list[dict[str, object]]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


async def fetch_catalog(connection: asyncpg.Connection[asyncpg.Record]) -> list[dict[str, object]]:
    return [dict(row) for row in await connection.fetch(CATALOG_SQL)]


def historical_audit(catalog: list[dict[str, object]]) -> dict[str, object]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    expected = {
        row["name"]: {
            "datname": row["name"],
            "oid": row["oid"],
            "owner": row["owner"],
            "owner_oid": 10,
        }
        for row in plan["per_name"]
        if row["name"] in set(plan["unknown_names"])
    }
    actual = {row["datname"]: row for row in catalog}
    missing = sorted(set(expected) - set(actual))
    mismatches = [
        {"name": name, "expected": expected[name], "actual": actual.get(name)}
        for name in sorted(expected)
        if name in actual and actual[name] != expected[name]
    ]
    exact = [expected[name] for name in sorted(expected) if actual.get(name) == expected[name]]
    return {
        "expected_count": 45,
        "plan_unknown_count": len(plan["unknown_names"]),
        "exact_count": len(exact),
        "missing": missing,
        "mismatches": mismatches,
        "identities": exact,
        "passed": len(exact) == 45 and not missing and not mismatches,
    }


async def connect(application_name: str) -> asyncpg.Connection[asyncpg.Record]:
    url = make_url(DEFAULT_ADMIN_DATABASE_URL)
    return await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database=url.database,
        server_settings={"application_name": application_name},
    )


async def main() -> int:
    nonce = secrets.token_hex(16)
    baseline_connection = await connect(f"tg_r5_baseline_{nonce}")
    try:
        baseline = await fetch_catalog(baseline_connection)
    finally:
        await baseline_connection.close()
    baseline_hash = canonical_hash(baseline)
    write_json(
        "full-catalog-before.json",
        {
            "observed_at_utc": utc_now(),
            "count": len(baseline),
            "canonical_sha256": baseline_hash,
            "identities": baseline,
        },
    )
    history = historical_audit(baseline)
    write_json("historical-unknown-before.json", history)
    if not history["passed"]:
        write_json(
            "preflight-quiescence-summary.json",
            {
                "passed": False,
                "reason": "historical_unknown_mismatch",
                "sample_count": 0,
                "duration_seconds": 0,
                "real_pytest_started": False,
                "create_count": 0,
            },
        )
        return 2

    observer = await connect(f"tg_r5_quiescence_{nonce}")
    timeline = EVIDENCE / "preflight-quiescence-timeline.jsonl"
    samples: list[dict[str, object]] = []
    started = monotonic()
    passed = True
    reason = None
    try:
        for index in range(25):
            if index:
                target = started + index * 5
                await asyncio.sleep(max(0, target - monotonic()))
            catalog = await fetch_catalog(observer)
            activity = await observer.fetchrow(ACTIVITY_SQL)
            assert activity is not None
            row = {
                "sample": index + 1,
                "utc_timestamp": utc_now(),
                "elapsed_seconds": round(monotonic() - started, 3),
                "catalog_count": len(catalog),
                "catalog_sha256": canonical_hash(catalog),
                "external_active_client_backends": activity["external_active"],
                "external_tg_sessions": activity["external_tg_sessions"],
            }
            samples.append(row)
            with timeline.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
            if (
                row["catalog_count"] != len(baseline)
                or row["catalog_sha256"] != baseline_hash
                or row["external_active_client_backends"] != 0
                or row["external_tg_sessions"] != 0
            ):
                passed = False
                reason = "catalog_or_activity_drift"
                break
            if (index + 1) % 5 == 0:
                print(
                    f"quiescence progress: {index + 1}/25 samples, "
                    f"elapsed={row['elapsed_seconds']}s, catalog={len(catalog)}, "
                    f"sha256={baseline_hash}"
                )
    finally:
        await observer.close()

    duration = samples[-1]["elapsed_seconds"] if samples else 0
    summary = {
        "passed": passed and len(samples) >= 25 and float(duration) >= 120,
        "reason": reason,
        "observer_nonce": nonce,
        "sample_count": len(samples),
        "duration_seconds": duration,
        "interval_seconds": 5,
        "baseline_catalog_count": len(baseline),
        "baseline_catalog_sha256": baseline_hash,
        "first_sample": samples[0] if samples else None,
        "last_sample": samples[-1] if samples else None,
        "all_catalog_identities_equal": all(
            row["catalog_count"] == len(baseline)
            and row["catalog_sha256"] == baseline_hash
            for row in samples
        ),
        "all_external_active_zero": all(
            row["external_active_client_backends"] == 0 for row in samples
        ),
        "all_external_tg_sessions_zero": all(
            row["external_tg_sessions"] == 0 for row in samples
        ),
        "real_pytest_started": False,
        "create_count": 0,
    }
    write_json("preflight-quiescence-summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
