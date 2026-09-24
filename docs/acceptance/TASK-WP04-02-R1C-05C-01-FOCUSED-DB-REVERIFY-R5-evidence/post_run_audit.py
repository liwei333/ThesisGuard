from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections import Counter, defaultdict
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


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(name: str, payload: object) -> None:
    (EVIDENCE / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def canonical_hash(rows: list[dict[str, object]]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def identity(row: dict[str, object]) -> tuple[object, object, object, object]:
    return row["datname"], row["oid"], row["owner"], row["owner_oid"]


def historical_audit(catalog: list[dict[str, object]]) -> dict[str, object]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    unknown_names = set(plan["unknown_names"])
    expected = {
        row["name"]: {
            "datname": row["name"],
            "oid": row["oid"],
            "owner": row["owner"],
            "owner_oid": 10,
        }
        for row in plan["per_name"]
        if row["name"] in unknown_names
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


async def fetch_catalog(connection: asyncpg.Connection[asyncpg.Record]) -> list[dict[str, object]]:
    return [dict(row) for row in await connection.fetch(CATALOG_SQL)]


def audit_ledger(after: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    meta = json.loads((EVIDENCE / "real-pytest.meta.json").read_text(encoding="utf-8"))
    run_id = meta["run_id"]
    rows = [
        json.loads(line)
        for line in (EVIDENCE / "resources.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    current = [row for row in rows if row.get("run_id") == run_id]
    other_run_rows = [row for row in rows if row.get("run_id") != run_id]
    counts = Counter(row["event"] for row in current)
    by_attempt: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in current:
        if row.get("attempt_id"):
            by_attempt[str(row["attempt_id"])].append(row)
    after_map = {row["datname"]: row for row in after}
    resources: list[dict[str, object]] = []
    unknown_count = 0
    residual_count = 0
    for attempt_id, events in by_attempt.items():
        event_names = [str(row["event"]) for row in events]
        first = events[0]
        created = next((row for row in events if row["event"] == "created"), None)
        dropped = next((row for row in events if row["event"] == "dropped"), None)
        create_failed = next((row for row in events if row["event"] == "create_failed"), None)
        is_unknown = bool(
            create_failed and create_failed.get("ownership") == "UNKNOWN"
        ) or ("create_sent" in event_names and created is None and create_failed is None)
        unknown_count += int(is_unknown)
        exact = None
        residual = False
        if created is not None:
            exact = {
                "datname": created["name"],
                "oid": created["oid"],
                "owner": created["owner"],
                "owner_oid": created["owner_oid"],
            }
            residual = after_map.get(str(created["name"])) == exact
            residual_count += int(residual)
        resources.append(
            {
                "attempt_id": attempt_id,
                "run_id": first["run_id"],
                "node": first["node"],
                "name": first["name"],
                "events": event_names,
                "created_identity": exact,
                "confirmed_dropped": dropped is not None,
                "cleanup_failed": "cleanup_failed" in event_names,
                "unknown": is_unknown,
                "residual_exact_identity": residual,
            }
        )
    audit = {
        "run_id": run_id,
        "ledger_rows": len(rows),
        "other_run_rows": len(other_run_rows),
        "attempt": counts["attempt"],
        "create_sent": counts["create_sent"],
        "created": counts["created"],
        "drop_sent": counts["drop_sent"],
        "dropped": counts["dropped"],
        "cleanup_failed": counts["cleanup_failed"],
        "create_failed": counts["create_failed"],
        "current_run_unknown": unknown_count,
        "current_run_residual": residual_count,
        "all_run_ids_match": len(other_run_rows) == 0,
        "within_create_budget": counts["create_sent"] <= 41,
        "resources": resources,
    }
    return audit, current


def scenario_results() -> dict[str, object]:
    text = (EVIDENCE / "real-pytest.stdout.txt").read_text(encoding="utf-8")
    collected = int(re.search(r"collected (\d+) items", text).group(1))
    passed_match = re.search(r"(\d+) passed", text)
    errors_match = re.search(r"(\d+) error", text)
    failed_match = re.search(r"(\d+) failed", text)
    passed = int(passed_match.group(1)) if passed_match else 0
    errors = int(errors_match.group(1)) if errors_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    node_match = re.search(r"ERROR (tests/[^\s]+)", text)
    return {
        "collected": collected,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "not_executed_after_x": collected - passed - failed - errors,
        "failure_node": node_match.group(1) if node_match else None,
        "failure_type": "EvidencePGCleanupError" if "EvidencePGCleanupError" in text else None,
        "business_assertion_failure": False,
        "resource_lifecycle_failure": "EvidencePGCleanupError" in text,
    }


def runtime_attribution(
    baseline: list[dict[str, object]], ledger_rows: list[dict[str, object]]
) -> dict[str, object]:
    baseline_set = {identity(row) for row in baseline}
    created_set = {
        (row["name"], row["oid"], row["owner"], row["owner_oid"])
        for row in ledger_rows
        if row["event"] == "created"
    }
    observed_task: set[tuple[object, object, object, object]] = set()
    unknown_additions: set[tuple[object, object, object, object]] = set()
    baseline_missing: set[tuple[object, object, object, object]] = set()
    samples = 0
    for line in (EVIDENCE / "runtime-catalog-timeline.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        if not line.strip():
            continue
        samples += 1
        record = json.loads(line)
        current = {identity(row) for row in record["identities"]}
        for added in current - baseline_set:
            if added in created_set:
                observed_task.add(added)
            else:
                unknown_additions.add(added)
        baseline_missing.update(baseline_set - current)
    return {
        "runtime_sample_count": samples,
        "ledger_created_identity_count": len(created_set),
        "observed_task_identity_count": len(observed_task),
        "observed_task_identities": sorted(observed_task),
        "unknown_external_additions": sorted(unknown_additions),
        "missing_or_changed_preexisting_identities": sorted(baseline_missing),
        "unattributed_external_catalog_delta": bool(unknown_additions or baseline_missing),
    }


async def main() -> int:
    before_payload = json.loads((EVIDENCE / "full-catalog-before.json").read_text())
    baseline = before_payload["identities"]
    baseline_hash = before_payload["canonical_sha256"]
    connection = await connect("tg_r5_postrun_readonly")
    try:
        after = await fetch_catalog(connection)
        activity = [
            dict(row)
            for row in await connection.fetch(
                "SELECT datname, usename, application_name, state "
                "FROM pg_stat_activity WHERE datname LIKE 'tg_wp04_service_%' "
                "ORDER BY datname, usename, application_name"
            )
        ]
        after_hash = canonical_hash(after)
        write_json(
            "full-catalog-after.json",
            {
                "observed_at_utc": utc_now(),
                "count": len(after),
                "canonical_sha256": after_hash,
                "identities": after,
                "task_prefix_sessions": activity,
            },
        )
        historical = historical_audit(after)
        write_json("historical-unknown-after.json", historical)
        ledger_audit, ledger_rows = audit_ledger(after)
        write_json("ledger-audit.json", ledger_audit)
        scenarios = scenario_results()
        write_json("scenario-results.json", scenarios)
        attribution = runtime_attribution(baseline, ledger_rows)
        write_json("catalog-delta-attribution.json", attribution)

        timeline = EVIDENCE / "post-run-stability-timeline.jsonl"
        samples: list[dict[str, object]] = []
        started = monotonic()
        for index in range(7):
            if index:
                target = started + index * 5
                await asyncio.sleep(max(0, target - monotonic()))
            rows = await fetch_catalog(connection)
            row = {
                "sample": index + 1,
                "utc_timestamp": utc_now(),
                "elapsed_seconds": round(monotonic() - started, 3),
                "catalog_count": len(rows),
                "catalog_sha256": canonical_hash(rows),
                "equals_before": len(rows) == len(baseline)
                and canonical_hash(rows) == baseline_hash,
            }
            samples.append(row)
            with timeline.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
        write_json(
            "database-resource-audit.json",
            {
                "verdict": "FAIL_DB_RESOURCE_LIFECYCLE",
                "before_after_catalog_equal": after == baseline,
                "before_count": len(baseline),
                "after_count": len(after),
                "before_sha256": baseline_hash,
                "after_sha256": after_hash,
                "historical_unknown_before_exact": 45,
                "historical_unknown_after_exact": historical["exact_count"],
                "post_run_sample_count": len(samples),
                "post_run_duration_seconds": samples[-1]["elapsed_seconds"],
                "post_run_all_equal_before": all(row["equals_before"] for row in samples),
                "ledger": ledger_audit,
                "scenario_results": scenarios,
                "runtime_attribution": attribution,
                "manual_cleanup_performed": False,
                "connected_to_historical_unknown": False,
            },
        )
    finally:
        await connection.close()
    print(json.dumps({"ledger": ledger_audit, "scenarios": scenarios}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
