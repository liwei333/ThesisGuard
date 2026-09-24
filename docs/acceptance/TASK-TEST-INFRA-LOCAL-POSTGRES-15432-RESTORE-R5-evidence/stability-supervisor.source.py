#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import postgres_observer as observer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_child_and_record(
    command: list[str],
    *,
    outcome_path: Path,
    invocation_id: str,
    task_id: str,
) -> int:
    started = utc_now()
    completed = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=90,
    )
    stdout_expected = completed.stdout in {b"FORMAL_OBSERVER_OK\n", b""}
    outcome: dict[str, Any] = {
        "schema_version": observer.SCHEMA_VERSION,
        "task_id": task_id,
        "invocation_id": invocation_id,
        "started_at_utc": started,
        "completed_at_utc": utc_now(),
        "status": "OBSERVER_EXITED",
        "child_return_code": completed.returncode,
        "stdout_fixed_status_valid": stdout_expected,
        "stderr_empty": completed.stderr == b"",
        "raw_output_retained": False,
    }
    observer.atomic_publish_json(outcome_path, outcome)
    return completed.returncode


def formal_supervise(
    *,
    observer_source: Path,
    env_path: Path,
    evidence_dir: Path,
    invocation_id: str,
    preflight_catalog_hash: str,
) -> int:
    paths = {
        "invocation": evidence_dir / "stability-invocation.json",
        "timeline": evidence_dir / "stability-timeline.jsonl",
        "completion": evidence_dir / "stability-completion.json",
        "outcome": evidence_dir / "stability-process-outcome.json",
        "failure": evidence_dir / "stability-failure.json",
    }
    existing = [name for name, path in paths.items() if path.exists() or path.is_symlink()]
    if existing:
        raise FileExistsError("formal artifact path already exists")
    invocation = {
        "schema_version": observer.SCHEMA_VERSION,
        "task_id": observer.TASK_ID,
        "invocation_id": invocation_id,
        "declared_at_utc": utc_now(),
        "invocation_count": 1,
        "clock_mode": "real-monotonic",
        "synthetic_clock_allowed": False,
        "expected_offsets_seconds": list(observer.OFFSETS),
        "paths": {name: path.name for name, path in paths.items()},
    }
    observer.atomic_publish_json(paths["invocation"], invocation)
    command = [
        sys.executable,
        str(observer_source),
        "--mode",
        "formal",
        "--env-path",
        str(env_path),
        "--evidence-dir",
        str(evidence_dir),
        "--invocation-id",
        invocation_id,
        "--preflight-catalog-hash",
        preflight_catalog_hash,
    ]
    return_code = run_child_and_record(
        command,
        outcome_path=paths["outcome"],
        invocation_id=invocation_id,
        task_id=observer.TASK_ID,
    )
    if return_code != 0:
        observer.atomic_publish_json(
            paths["failure"],
            observer.safe_failure_payload(invocation_id, "FORMAL_OBSERVER_NONZERO"),
        )
    return return_code


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observer-source", required=True, type=Path)
    parser.add_argument("--env-path", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--invocation-id", required=True)
    parser.add_argument("--preflight-catalog-hash", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = formal_supervise(
            observer_source=args.observer_source,
            env_path=args.env_path,
            evidence_dir=args.evidence_dir,
            invocation_id=args.invocation_id,
            preflight_catalog_hash=args.preflight_catalog_hash,
        )
    except (FileExistsError, OSError, observer.ObserverError):
        return 2
    if result == 0:
        print("SUPERVISOR_OK", flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
