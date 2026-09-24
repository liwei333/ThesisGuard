#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable

import closure_helper as closure


TASK_ID = closure.REPAIR_TASK_ID
SCHEMA_VERSION = 1
HOST = "127.0.0.1"
PORT = 15432
DATABASE = "postgres"
USER = "thesisguard"
RESIDUAL = "tg_wp04_service_53ea9a765404436e8fc6a6ecf2f51187"
OFFSETS = (0, 5, 10, 15, 20, 25, 30)

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


class EvidenceValidationError(ObserverError):
    pass


class SyntheticInterruption(ObserverError):
    pass


class TimelineParseError(EvidenceValidationError):
    def __init__(self, message: str, complete_records: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.complete_records = complete_records


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_existing_file(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_publish_json(path: Path, payload: dict[str, Any]) -> None:
    closure.publish_json_no_clobber(path, payload)


def durable_write_json_line(handle: BinaryIO, record: dict[str, Any]) -> None:
    data = canonical_json_bytes(record) + b"\n"
    handle.write(data)
    handle.flush()
    os.fsync(handle.fileno())


def write_records_durably(
    path: Path,
    records: Iterable[dict[str, Any]],
    *,
    interrupt_after: int | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        for index, record in enumerate(records, start=1):
            durable_write_json_line(handle, record)
            if interrupt_after is not None and index == interrupt_after:
                raise SyntheticInterruption("synthetic interruption after durable record")
    fsync_directory(path.parent)


def parse_timeline(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    records: list[dict[str, Any]] = []
    if data and not data.endswith(b"\n"):
        for raw in data.split(b"\n")[:-1]:
            if not raw:
                continue
            try:
                value = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise TimelineParseError("malformed complete JSONL record", records) from exc
            if not isinstance(value, dict):
                raise TimelineParseError("JSONL record is not an object", records)
            records.append(value)
        raise TimelineParseError("truncated final JSONL record", records)
    for raw in data.splitlines():
        if not raw:
            raise TimelineParseError("blank JSONL record", records)
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TimelineParseError("malformed JSONL record", records) from exc
        if not isinstance(value, dict):
            raise TimelineParseError("JSONL record is not an object", records)
        records.append(value)
    return records


def require_clock_mode(*, mode: str, clock_mode: str) -> str:
    if mode == "formal" and clock_mode != "real-monotonic":
        raise ObserverError("formal mode requires real-monotonic clock")
    if mode == "dry-run" and clock_mode not in {"synthetic", "real-monotonic"}:
        raise ObserverError("unsupported dry-run clock mode")
    return clock_mode


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceValidationError(f"{label} unreadable") from exc
    if not isinstance(value, dict):
        raise EvidenceValidationError(f"{label} is not an object")
    return value


def validate_artifacts(
    *,
    timeline_path: Path,
    completion_path: Path,
    outcome_path: Path,
    invocation_id: str,
    preflight_catalog_hash: str,
    prewindow_gate_index_sha256: str | None = None,
) -> dict[str, Any]:
    if not timeline_path.is_file():
        raise EvidenceValidationError("timeline missing")
    if not completion_path.is_file():
        raise EvidenceValidationError("completion missing")
    if not outcome_path.is_file():
        raise EvidenceValidationError("process outcome missing")
    records = parse_timeline(timeline_path)
    marker = _load_json_object(completion_path, "completion")
    process = _load_json_object(outcome_path, "process outcome")
    sequences = [row.get("sequence_number") for row in records]
    invocation_ids = [row.get("invocation_id") for row in records]
    elapsed = [row.get("monotonic_elapsed_seconds") for row in records]
    row_counts = {row.get("catalog_row_count") for row in records}
    hashes = {row.get("catalog_canonical_sha256") for row in records}
    databases = {row.get("current_database") for row in records}
    users = {row.get("current_user") for row in records}
    majors = {row.get("postgresql_major_version") for row in records}
    external = [row.get("external_active_client_count") for row in records]
    task_sessions = [row.get("task_prefix_external_session_count") for row in records]
    gate_hashes = [row.get("prewindow_gate_index_sha256") for row in records]
    duration = float(elapsed[-1]) if elapsed else 0.0
    checks = {
        "exact_sample_count": len(records) == 7,
        "exact_sequence": sequences == list(range(7)),
        "timeline_invocation": invocation_ids == [invocation_id] * 7,
        "duration": duration >= 30.0,
        "catalog_row_count_stable": len(row_counts) == 1,
        "catalog_hash_stable": hashes == {preflight_catalog_hash},
        "external_active_zero": external == [0] * 7,
        "task_prefix_sessions_zero": task_sessions == [0] * 7,
        "database_identity": databases == {DATABASE},
        "user_identity": users == {USER},
        "major_version": majors == {17},
        "completion_invocation": marker.get("invocation_id") == invocation_id,
        "completion_sample_count": marker.get("sample_count") == len(records),
        "completion_duration": marker.get("duration_seconds") == duration,
        "completion_row_counts": marker.get("catalog_row_counts") == sorted(row_counts),
        "completion_hashes": marker.get("catalog_canonical_sha256_values") == sorted(hashes),
        "completion_external": marker.get("max_external_active_client_count") == max(external, default=0),
        "completion_task_sessions": marker.get("max_task_prefix_external_session_count") == max(task_sessions, default=0),
        "completion_criteria": marker.get("criteria_satisfied") is True,
        "outcome_invocation": process.get("invocation_id") == invocation_id,
        "child_return_code": process.get("child_return_code") == 0,
    }
    if prewindow_gate_index_sha256 is not None:
        checks.update(
            {
                "timeline_gate_index_binding": gate_hashes == [prewindow_gate_index_sha256] * 7,
                "completion_gate_index_binding": marker.get("prewindow_gate_index_sha256") == prewindow_gate_index_sha256,
                "outcome_gate_index_binding": process.get("prewindow_gate_index_sha256") == prewindow_gate_index_sha256,
            }
        )
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise EvidenceValidationError("artifact validation failed: " + ",".join(failed))
    return {
        "criteria_satisfied": True,
        "sample_count": len(records),
        "sequence_numbers": sequences,
        "duration_seconds": duration,
        "catalog_row_counts": sorted(row_counts),
        "catalog_canonical_sha256_values": sorted(hashes),
        "max_external_active_client_count": max(external, default=0),
        "max_task_prefix_external_session_count": max(task_sessions, default=0),
        "checks": checks,
    }


def build_completion(
    records: list[dict[str, Any]], invocation_id: str, prewindow_gate_index_sha256: str | None = None
) -> dict[str, Any]:
    row_counts = sorted({int(row["catalog_row_count"]) for row in records})
    hashes = sorted({str(row["catalog_canonical_sha256"]) for row in records})
    duration = float(records[-1]["monotonic_elapsed_seconds"]) if records else 0.0
    criteria = all(
        (
            len(records) == 7,
            [row["sequence_number"] for row in records] == list(range(7)),
            all(row["invocation_id"] == invocation_id for row in records),
            duration >= 30.0,
            len(row_counts) == 1,
            len(hashes) == 1,
            all(row["current_database"] == DATABASE for row in records),
            all(row["current_user"] == USER for row in records),
            all(row["postgresql_major_version"] == 17 for row in records),
            all(row["external_active_client_count"] == 0 for row in records),
            all(row["task_prefix_external_session_count"] == 0 for row in records),
        )
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "invocation_id": invocation_id,
        "completed_at_utc": utc_now(),
        "sample_count": len(records),
        "duration_seconds": duration,
        "catalog_row_counts": row_counts,
        "catalog_canonical_sha256_values": hashes,
        "max_external_active_client_count": max(
            (int(row["external_active_client_count"]) for row in records), default=0
        ),
        "max_task_prefix_external_session_count": max(
            (int(row["task_prefix_external_session_count"]) for row in records), default=0
        ),
        "criteria_satisfied": criteria,
    }
    if prewindow_gate_index_sha256 is not None:
        result["prewindow_gate_index_sha256"] = prewindow_gate_index_sha256
    return result


def publish_completion_after_timeline_fsync(
    timeline_path: Path, completion_path: Path, payload: dict[str, Any]
) -> None:
    fsync_existing_file(timeline_path)
    atomic_publish_json(completion_path, payload)


def safe_failure_payload(
    invocation_id: str, error_code: str, _error: BaseException | None = None
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "invocation_id": invocation_id,
        "observed_at_utc": utc_now(),
        "error_code": error_code,
        "message": "observer failed; raw exception intentionally withheld",
    }


def emit_status(token: str) -> None:
    allowed = {"DRY_RUN_OK", "PREFLIGHT_OK", "FORMAL_OBSERVER_OK"}
    if token not in allowed:
        raise ObserverError("unapproved status token")
    print(token, flush=True)


def read_env_value(path: Path, key: str) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        candidate, value = line.split("=", 1)
        if candidate.strip() == key:
            result = value.strip().strip('"').strip("'")
            if result:
                return result
            raise ObserverError("required credential is empty")
    raise ObserverError("required credential is missing")


def canonical_catalog(rows: list[dict[str, Any]]) -> bytes:
    normalized = sorted(rows, key=lambda row: str(row["name"]))
    return canonical_json_bytes(normalized)


def catalog_sha256(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_catalog(rows)).hexdigest()


def load_expected_identities(plan_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = payload.get("per_name")
    excluded = payload.get("excluded_other_database_names")
    if not isinstance(rows, list) or len(rows) != 45 or not isinstance(excluded, list):
        raise ObserverError("historical identity plan has unexpected structure")
    expected = [
        {
            "name": str(row["name"]),
            "oid": int(row["oid"]),
            "owner": str(row["owner"]),
            "owner_oid": 10,
        }
        for row in rows
    ]
    return expected, sorted(str(value) for value in excluded)


def compare_historical(
    expected: list[dict[str, Any]], actual: list[dict[str, Any]]
) -> dict[str, Any]:
    expected_by_name = {row["name"]: row for row in expected}
    actual_by_name = {row["name"]: row for row in actual}
    missing = sorted(set(expected_by_name) - set(actual_by_name))
    mismatches: list[dict[str, Any]] = []
    exact = 0
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
            exact += 1
    return {
        "expected_count": len(expected),
        "observed_count": sum(name in actual_by_name for name in expected_by_name),
        "exact_match_count": exact,
        "missing": missing,
        "mismatches": mismatches,
        "comparison_fields": list(fields),
    }


def connect_read_only(password: str) -> Any:
    import psycopg

    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=password,
        connect_timeout=5,
        autocommit=True,
        options="-c default_transaction_read_only=on",
        application_name="thesisguard_r5_read_only_observer",
    )


def observe(connection: Any, *, include_catalog: bool) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute(OBSERVATION_SQL)
        row = cursor.fetchone()
    if row is None or not isinstance(row[5], list):
        raise ObserverError("observation returned unexpected structure")
    catalog = [
        {
            "name": str(item["name"]),
            "oid": int(item["oid"]),
            "owner": str(item["owner"]),
            "owner_oid": int(item["owner_oid"]),
        }
        for item in row[5]
    ]
    result: dict[str, Any] = {
        "observed_at_utc": utc_now(),
        "current_database": str(row[0]),
        "current_user": str(row[1]),
        "postgresql_version": str(row[2]),
        "postgresql_version_num": int(row[3]),
        "postgresql_major_version": int(row[3]) // 10000,
        "observer_backend_pid": int(row[4]),
        "catalog_row_count": len(catalog),
        "catalog_canonical_sha256": catalog_sha256(catalog),
        "external_active_client_count": int(row[6]),
        "task_prefix_external_session_count": int(row[7]),
    }
    if include_catalog:
        result["catalog"] = catalog
    return result


def run_preflight(env_path: Path, plan_path: Path, output_path: Path) -> dict[str, Any]:
    password = read_env_value(env_path, "POSTGRES_PASSWORD")
    expected, excluded = load_expected_identities(plan_path)
    with connect_read_only(password) as connection:
        observed = observe(connection, include_catalog=True)
    catalog = observed["catalog"]
    comparison = compare_historical(expected, catalog)
    actual_names = {row["name"] for row in catalog}
    expected_names = {row["name"] for row in expected}
    additional = sorted(actual_names - expected_names - set(excluded))
    residual_present = RESIDUAL in actual_names
    criteria = all(
        (
            observed["current_database"] == DATABASE,
            observed["current_user"] == USER,
            observed["postgresql_major_version"] == 17,
            comparison["expected_count"] == 45,
            comparison["exact_match_count"] == 45,
            not comparison["missing"],
            not comparison["mismatches"],
            not residual_present,
            not additional,
            observed["external_active_client_count"] == 0,
            observed["task_prefix_external_session_count"] == 0,
        )
    )
    result = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "mode": "read-only-preflight",
        "observed_at_utc": observed["observed_at_utc"],
        "connection_target": {"host": HOST, "port": PORT, "database": DATABASE},
        "postgresql_connection_count": 1,
        "identity": {
            key: observed[key]
            for key in (
                "current_database",
                "current_user",
                "postgresql_version",
                "postgresql_version_num",
                "postgresql_major_version",
                "observer_backend_pid",
            )
        },
        "catalog_row_count": observed["catalog_row_count"],
        "catalog_canonical_sha256": observed["catalog_canonical_sha256"],
        "catalog": catalog,
        "historical_unknown_comparison": comparison,
        "historical_individual_database_connections": 0,
        "r5_residual": {"name": RESIDUAL, "present": residual_present},
        "additional_databases": additional,
        "additional_database_count": len(additional),
        "external_active_client_count": observed["external_active_client_count"],
        "task_prefix_external_session_count": observed[
            "task_prefix_external_session_count"
        ],
        "criteria_satisfied": criteria,
    }
    atomic_publish_json(output_path, result)
    return result


def run_formal(
    *,
    env_path: Path,
    evidence_dir: Path,
    invocation_id: str,
    preflight_catalog_hash: str,
    prewindow_gate_index_sha256: str,
) -> dict[str, Any]:
    require_clock_mode(mode="formal", clock_mode="real-monotonic")
    timeline = evidence_dir / "stability-timeline.jsonl"
    completion_path = evidence_dir / "stability-completion.json"
    if timeline.exists() or timeline.is_symlink() or completion_path.exists() or completion_path.is_symlink():
        raise FileExistsError("formal timeline or completion path already exists")
    password = read_env_value(env_path, "POSTGRES_PASSWORD")
    records: list[dict[str, Any]] = []
    started = time.monotonic()
    with connect_read_only(password) as connection, timeline.open("xb") as handle:
        for sequence, offset in enumerate(OFFSETS):
            remaining = started + offset - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            observed = observe(connection, include_catalog=False)
            record = {
                "schema_version": SCHEMA_VERSION,
                "task_id": TASK_ID,
                "invocation_id": invocation_id,
                "prewindow_gate_index_sha256": prewindow_gate_index_sha256,
                "sequence_number": sequence,
                "scheduled_offset_seconds": offset,
                "monotonic_elapsed_seconds": round(time.monotonic() - started, 6),
                "observed_at_utc": observed["observed_at_utc"],
                "current_database": observed["current_database"],
                "current_user": observed["current_user"],
                "postgresql_major_version": observed["postgresql_major_version"],
                "observer_backend_pid": observed["observer_backend_pid"],
                "catalog_row_count": observed["catalog_row_count"],
                "catalog_canonical_sha256": observed["catalog_canonical_sha256"],
                "external_active_client_count": observed[
                    "external_active_client_count"
                ],
                "task_prefix_external_session_count": observed[
                    "task_prefix_external_session_count"
                ],
            }
            durable_write_json_line(handle, record)
            records.append(record)
    fsync_directory(evidence_dir)
    marker = build_completion(records, invocation_id, prewindow_gate_index_sha256)
    if marker["catalog_canonical_sha256_values"] != [preflight_catalog_hash]:
        marker["criteria_satisfied"] = False
    if not marker["criteria_satisfied"]:
        raise EvidenceValidationError("formal stability criteria not satisfied")
    publish_completion_after_timeline_fsync(timeline, completion_path, marker)
    return marker


def _synthetic_record(invocation_id: str, sequence: int, digest: str, gate_hash: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "invocation_id": invocation_id,
        "prewindow_gate_index_sha256": gate_hash,
        "sequence_number": sequence,
        "scheduled_offset_seconds": sequence * 5,
        "monotonic_elapsed_seconds": float(sequence * 5),
        "observed_at_utc": f"2026-09-23T00:00:{sequence * 5:02d}+00:00",
        "current_database": DATABASE,
        "current_user": USER,
        "postgresql_major_version": 17,
        "observer_backend_pid": 1,
        "catalog_row_count": 49,
        "catalog_canonical_sha256": digest,
        "external_active_client_count": 0,
        "task_prefix_external_session_count": 0,
    }


def dry_run(root: Path) -> dict[str, Any]:
    require_clock_mode(mode="dry-run", clock_mode="synthetic")
    root.mkdir(parents=True, exist_ok=False)
    invocation_id = "synthetic-dry-run"
    digest = "d" * 64
    gate_hash = "e" * 64
    records = [_synthetic_record(invocation_id, index, digest, gate_hash) for index in range(7)]
    timeline = root / "stability-timeline.jsonl"
    completion_path = root / "stability-completion.json"
    outcome_path = root / "stability-process-outcome.json"
    write_records_durably(timeline, records)
    publish_completion_after_timeline_fsync(
        timeline, completion_path, build_completion(records, invocation_id, gate_hash)
    )
    atomic_publish_json(
        outcome_path,
        {
            "schema_version": SCHEMA_VERSION,
            "task_id": TASK_ID,
            "invocation_id": invocation_id,
            "prewindow_gate_index_sha256": gate_hash,
            "child_return_code": 0,
            "status": "SYNTHETIC_ONLY",
        },
    )
    validation = validate_artifacts(
        timeline_path=timeline,
        completion_path=completion_path,
        outcome_path=outcome_path,
        invocation_id=invocation_id,
        preflight_catalog_hash=digest,
        prewindow_gate_index_sha256=gate_hash,
    )
    return {
        "mode": "synthetic-no-side-effect-dry-run",
        "clock_mode": "synthetic",
        "criteria_satisfied": validation["criteria_satisfied"],
        "sample_count": validation["sample_count"],
        "docker_calls": 0,
        "postgresql_connections": 0,
        "network_connections": 0,
        "open_calls": 0,
        "docker_start_calls": 0,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dry-run", "preflight", "formal"), required=True)
    parser.add_argument("--env-path", type=Path)
    parser.add_argument("--plan-path", type=Path)
    parser.add_argument("--output-path", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--invocation-id")
    parser.add_argument("--preflight-catalog-hash")
    parser.add_argument("--prewindow-gate-index-sha256")
    parser.add_argument("--dry-run-root", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.mode == "dry-run":
            if args.dry_run_root is None:
                raise ObserverError("dry-run root required")
            dry_run(args.dry_run_root)
            emit_status("DRY_RUN_OK")
            return 0
        if args.mode == "preflight":
            if args.env_path is None or args.plan_path is None or args.output_path is None:
                raise ObserverError("preflight arguments missing")
            result = run_preflight(args.env_path, args.plan_path, args.output_path)
            if not result["criteria_satisfied"]:
                return 3
            emit_status("PREFLIGHT_OK")
            return 0
        if any(
            value is None
            for value in (
                args.env_path,
                args.evidence_dir,
                args.invocation_id,
                args.preflight_catalog_hash,
                args.prewindow_gate_index_sha256,
            )
        ):
            raise ObserverError("formal arguments missing")
        run_formal(
            env_path=args.env_path,
            evidence_dir=args.evidence_dir,
            invocation_id=args.invocation_id,
            preflight_catalog_hash=args.preflight_catalog_hash,
            prewindow_gate_index_sha256=args.prewindow_gate_index_sha256,
        )
        emit_status("FORMAL_OBSERVER_OK")
        return 0
    except (ObserverError, FileExistsError, OSError, ValueError):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
