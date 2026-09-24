from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg


HOST = "127.0.0.1"
PORT = 15432
DATABASE = "postgres"
USER = "thesisguard"
RESIDUAL = "tg_wp04_service_53ea9a765404436e8fc6a6ecf2f51187"


OBSERVATION_SQL = """
SELECT
  current_database(),
  current_user,
  version(),
  current_setting('server_version_num')::integer,
  pg_backend_pid(),
  (
    SELECT COALESCE(
      json_agg(
        json_build_object(
          'name', d.datname,
          'oid', d.oid,
          'owner', pg_get_userbyid(d.datdba),
          'owner_oid', d.datdba
        ) ORDER BY d.datname
      ),
      '[]'::json
    )
    FROM pg_database AS d
  ),
  (
    SELECT count(*)
    FROM pg_stat_activity AS a
    WHERE a.pid <> pg_backend_pid()
      AND a.backend_type = 'client backend'
      AND a.state = 'active'
  ),
  (
    SELECT count(*)
    FROM pg_stat_activity AS a
    WHERE a.pid <> pg_backend_pid()
      AND a.backend_type = 'client backend'
      AND a.datname LIKE 'tg_wp04_service_%'
  )
"""


class ObserverError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def read_env_value(path: Path, key: str) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        candidate, value = line.split("=", 1)
        if candidate.strip() == key:
            result = value.strip().strip('"').strip("'")
            if not result:
                raise ObserverError(f"required credential key {key} is empty")
            return result
    raise ObserverError(f"required credential key {key} is missing")


def canonical_catalog(rows: list[dict[str, Any]]) -> bytes:
    ordered = sorted(rows, key=lambda row: row["name"])
    return json.dumps(
        ordered, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def catalog_sha256(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_catalog(rows)).hexdigest()


def compare_historical(
    expected: list[dict[str, Any]], actual: list[dict[str, Any]]
) -> dict[str, Any]:
    expected_by_name = {row["name"]: row for row in expected}
    actual_by_name = {row["name"]: row for row in actual}
    missing = sorted(set(expected_by_name) - set(actual_by_name))
    mismatches: list[dict[str, Any]] = []
    exact_match_count = 0
    fields = ("name", "oid", "owner", "owner_oid")
    for name, wanted in sorted(expected_by_name.items()):
        found = actual_by_name.get(name)
        if found is None:
            continue
        differences = {
            field: {"expected": wanted[field], "actual": found.get(field)}
            for field in fields
            if wanted[field] != found.get(field)
        }
        if differences:
            mismatches.append({"name": name, "differences": differences})
        else:
            exact_match_count += 1
    return {
        "comparison_fields": list(fields),
        "expected_count": len(expected),
        "observed_count": sum(1 for name in expected_by_name if name in actual_by_name),
        "exact_match_count": exact_match_count,
        "missing": missing,
        "mismatches": mismatches,
    }


def load_plan(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("per_name")
    excluded = payload.get("excluded_other_database_names")
    if not isinstance(rows, list) or len(rows) != 45:
        raise ObserverError("cleanup plan does not contain exactly 45 identities")
    if not isinstance(excluded, list):
        raise ObserverError("cleanup plan excluded names are missing")
    expected = [
        {
            "name": row["name"],
            "oid": row["oid"],
            "owner": row["owner"],
            "owner_oid": 10,
        }
        for row in rows
    ]
    return expected, sorted(excluded)


def connect(password: str) -> psycopg.Connection[Any]:
    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=password,
        connect_timeout=5,
        autocommit=True,
    )


def observe(connection: psycopg.Connection[Any]) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(OBSERVATION_SQL)
        row = cursor.fetchone()
    if row is None:
        raise ObserverError("read-only observation returned no row")
    catalog = row[5]
    if not isinstance(catalog, list):
        raise ObserverError("catalog has unexpected type")
    normalized: list[dict[str, Any]] = []
    for item in catalog:
        if not isinstance(item, dict):
            raise ObserverError("catalog row has unexpected type")
        normalized.append(
            {
                "name": str(item["name"]),
                "oid": int(item["oid"]),
                "owner": str(item["owner"]),
                "owner_oid": int(item["owner_oid"]),
            }
        )
    return {
        "observed_at_utc": utc_now(),
        "current_database": row[0],
        "current_user": row[1],
        "server_version": row[2],
        "server_version_num": int(row[3]),
        "server_major_version": int(row[3]) // 10000,
        "observer_backend_pid": int(row[4]),
        "catalog_row_count": len(normalized),
        "catalog_sha256": catalog_sha256(normalized),
        "catalog": normalized,
        "external_active_client_count": int(row[6]),
        "task_prefix_external_session_count": int(row[7]),
    }


def preflight(env_path: Path, plan_path: Path) -> dict[str, Any]:
    password = read_env_value(env_path, "POSTGRES_PASSWORD")
    expected, excluded = load_plan(plan_path)
    with connect(password) as connection:
        sample = observe(connection)
    comparison = compare_historical(expected, sample["catalog"])
    names = {row["name"] for row in sample["catalog"]}
    expected_names = {row["name"] for row in expected}
    additional = sorted(names - expected_names - set(excluded))
    residual_present = RESIDUAL in names
    criteria = all(
        (
            sample["current_database"] == DATABASE,
            sample["current_user"] == USER,
            sample["server_major_version"] == 17,
            comparison["expected_count"] == 45,
            comparison["exact_match_count"] == 45,
            not comparison["missing"],
            not comparison["mismatches"],
            not residual_present,
        )
    )
    return {
        "mode": "preflight",
        "connection_target": {"host": HOST, "port": PORT, "database": DATABASE},
        "postgresql_connection_count": 1,
        "identity": {
            key: sample[key]
            for key in (
                "current_database",
                "current_user",
                "server_version",
                "server_version_num",
                "server_major_version",
                "observer_backend_pid",
            )
        },
        "catalog_row_count": sample["catalog_row_count"],
        "catalog_sha256": sample["catalog_sha256"],
        "catalog": sample["catalog"],
        "historical_unknown_comparison": comparison,
        "historical_individual_database_connections": 0,
        "r5_residual": {"name": RESIDUAL, "present": residual_present},
        "external_active_client_count": sample["external_active_client_count"],
        "task_prefix_external_session_count": sample[
            "task_prefix_external_session_count"
        ],
        "additional_databases": [
            {"name": name, "classification": "EXTERNAL_OR_CONCURRENT_UNKNOWN"}
            for name in additional
        ],
        "criteria_satisfied": criteria,
    }


def summarize_stability(
    samples: list[dict[str, Any]], invocation_count: int
) -> dict[str, Any]:
    row_counts = {sample["catalog_row_count"] for sample in samples}
    hashes = {sample["catalog_sha256"] for sample in samples}
    duration = samples[-1]["elapsed_seconds"] if samples else 0.0
    criteria = all(
        (
            invocation_count == 1,
            len(samples) >= 7,
            duration >= 30.0,
            len(row_counts) == 1,
            len(hashes) == 1,
            all(sample["external_active_client_count"] == 0 for sample in samples),
            all(
                sample["task_prefix_external_session_count"] == 0
                for sample in samples
            ),
        )
    )
    return {
        "invocation_count": invocation_count,
        "started": invocation_count == 1,
        "completed": len(samples) >= 7 and duration >= 30.0,
        "sample_count": len(samples),
        "duration_seconds": duration,
        "catalog_row_counts": sorted(row_counts),
        "catalog_sha256_values": sorted(hashes),
        "max_external_active_client_count": max(
            (sample["external_active_client_count"] for sample in samples), default=0
        ),
        "max_task_prefix_external_session_count": max(
            (
                sample["task_prefix_external_session_count"]
                for sample in samples
            ),
            default=0,
        ),
        "criteria_satisfied": criteria,
    }


def stability_window(env_path: Path) -> dict[str, Any]:
    password = read_env_value(env_path, "POSTGRES_PASSWORD")
    samples: list[dict[str, Any]] = []
    with connect(password) as connection:
        started = time.monotonic()
        for offset in (0, 5, 10, 15, 20, 25, 30):
            remaining = started + offset - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            sample = observe(connection)
            sample.pop("catalog")
            sample["elapsed_seconds"] = round(time.monotonic() - started, 6)
            samples.append(sample)
    summary = summarize_stability(samples, invocation_count=1)
    return {
        "mode": "stability-window",
        "connection_target": {"host": HOST, "port": PORT, "database": DATABASE},
        "postgresql_connection_count": 1,
        "samples": samples,
        "summary": summary,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--stability", action="store_true")
    parser.add_argument("--env-path", type=Path, required=True)
    parser.add_argument("--plan-path", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.preflight:
            if args.plan_path is None:
                raise ObserverError("--plan-path is required for preflight")
            payload = preflight(args.env_path, args.plan_path)
            print(encode_json(payload), end="")
            return 0 if payload["criteria_satisfied"] else 3
        payload = stability_window(args.env_path)
        print(encode_json(payload), end="")
        return 0 if payload["summary"]["criteria_satisfied"] else 4
    except Exception as exc:
        print(
            encode_json(
                {
                    "status": "ERROR",
                    "error_type": type(exc).__name__,
                    "message": "read-only PostgreSQL observation failed",
                }
            ),
            end="",
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
