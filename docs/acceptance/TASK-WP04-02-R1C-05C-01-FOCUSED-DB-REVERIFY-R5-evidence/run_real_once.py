from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.engine import make_url

from tests.test_evidence_services import DEFAULT_ADMIN_DATABASE_URL


EVIDENCE = Path(__file__).resolve().parent
CANDIDATE = Path(
    "/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/"
    "codex-wp04-02-evidence-domain-service"
)
PYTHONPATH = f"{CANDIDATE}:/opt/homebrew/lib/python3.12/site-packages"
PATH_VALUE = (
    "/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:"
    "/usr/bin:/bin:/usr/sbin:/sbin"
)
SELECTORS = [
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit",
    "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only",
    "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay",
]
URL_USERINFO = re.compile(r"([A-Za-z][A-Za-z0-9+.-]*://)[^\s/@]+(?::[^\s/@]*)?@")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(name: str, payload: object) -> None:
    (EVIDENCE / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def redact(value: str) -> str:
    url = make_url(DEFAULT_ADMIN_DATABASE_URL)
    sensitive = [DEFAULT_ADMIN_DATABASE_URL, url.password or ""]
    result = value
    for item in sensitive:
        if item:
            result = result.replace(item, "<REDACTED>")
    return URL_USERINFO.sub(r"\1<REDACTED>@", result)


def stop_observer(process: subprocess.Popen[str], stop_path: Path) -> tuple[str, str, int]:
    stop_path.write_text("stop\n", encoding="utf-8")
    try:
        stdout, stderr = process.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        process.terminate()
        stdout, stderr = process.communicate(timeout=10)
    return redact(stdout), redact(stderr), process.returncode


def main() -> int:
    run_id = secrets.token_hex(16)
    observer_nonce = secrets.token_hex(16)
    ledger = (EVIDENCE / "resources.jsonl").resolve()
    timeline = (EVIDENCE / "runtime-catalog-timeline.jsonl").resolve()
    ready = (EVIDENCE / "runtime-observer-ready.json").resolve()
    stop = (EVIDENCE / "runtime-observer.stop").resolve()
    for path in (ledger, timeline, ready, stop):
        if path.exists():
            raise RuntimeError(f"fresh path required: {path.name}")

    base_env = {
        "HOME": "/Users/qianduoduo",
        "USER": "qianduoduo",
        "LANG": "en_US.UTF-8",
        "PATH": PATH_VALUE,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": PYTHONPATH,
    }
    observer_env = {
        **base_env,
        "TG_R5_OBSERVER_NONCE": observer_nonce,
        "TG_R5_OBSERVER_TIMELINE": str(timeline),
        "TG_R5_OBSERVER_READY": str(ready),
        "TG_R5_OBSERVER_STOP": str(stop),
        "TG_R5_BASELINE_CATALOG": str((EVIDENCE / "full-catalog-before.json").resolve()),
    }
    observer_source = EVIDENCE / "runtime_catalog_observer.py"
    observer = subprocess.Popen(
        ["/opt/homebrew/bin/python3.12", str(observer_source)],
        cwd=str(CANDIDATE),
        env=observer_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 20
    while not ready.exists() and observer.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if not ready.exists():
        stdout, stderr, observer_rc = stop_observer(observer, stop)
        (EVIDENCE / "runtime-observer.stdout.txt").write_text(stdout, encoding="utf-8")
        (EVIDENCE / "runtime-observer.stderr.txt").write_text(stderr, encoding="utf-8")
        write_json(
            "real-pytest.meta.json",
            {
                "started": False,
                "invocation_count": 0,
                "reason": "runtime_observer_not_ready",
                "observer_returncode": observer_rc,
                "run_id": run_id,
                "observer_nonce": observer_nonce,
            },
        )
        return 2
    ready_data = json.loads(ready.read_text(encoding="utf-8"))
    if not ready_data.get("baseline_equal"):
        stdout, stderr, observer_rc = stop_observer(observer, stop)
        (EVIDENCE / "runtime-observer.stdout.txt").write_text(stdout, encoding="utf-8")
        (EVIDENCE / "runtime-observer.stderr.txt").write_text(stderr, encoding="utf-8")
        write_json(
            "real-pytest.meta.json",
            {
                "started": False,
                "invocation_count": 0,
                "reason": "runtime_observer_initial_catalog_drift",
                "observer_returncode": observer_rc,
                "run_id": run_id,
                "observer_nonce": observer_nonce,
                "ready": ready_data,
            },
        )
        return 3

    pytest_env = {
        **base_env,
        "TG_EVIDENCE_PG_LEDGER": str(ledger),
        "TG_EVIDENCE_PG_RUN_ID": run_id,
    }
    argv = [
        "/opt/homebrew/bin/pytest",
        "-p",
        "no:cacheprovider",
        "-x",
        "-vv",
        "-s",
        "--tb=short",
        *SELECTORS,
    ]
    started = utc_now()
    completed = subprocess.run(
        argv,
        cwd=str(CANDIDATE),
        env=pytest_env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    ended = utc_now()
    stdout, stderr, observer_rc = stop_observer(observer, stop)
    (EVIDENCE / "real-pytest.stdout.txt").write_text(
        redact(completed.stdout), encoding="utf-8"
    )
    (EVIDENCE / "real-pytest.stderr.txt").write_text(
        redact(completed.stderr), encoding="utf-8"
    )
    (EVIDENCE / "runtime-observer.stdout.txt").write_text(stdout, encoding="utf-8")
    (EVIDENCE / "runtime-observer.stderr.txt").write_text(stderr, encoding="utf-8")
    write_json(
        "real-pytest.meta.json",
        {
            "started": True,
            "invocation_count": 1,
            "executable": argv[0],
            "flags": argv[1:7],
            "selectors": SELECTORS,
            "cwd": str(CANDIDATE),
            "child_environment_keys": sorted(pytest_env),
            "forbidden_diagnostic_variables_present": False,
            "run_id": run_id,
            "observer_nonce": observer_nonce,
            "observer_initial_catalog_equal": True,
            "start_utc": started,
            "end_utc": ended,
            "returncode": completed.returncode,
            "observer_returncode": observer_rc,
        },
    )
    source_bytes = observer_source.read_bytes()
    write_json(
        "runtime-observer-source-sha256.json",
        {
            "path": "runtime_catalog_observer.py",
            "bytes": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        },
    )
    print(
        json.dumps(
            {
                "pytest_returncode": completed.returncode,
                "observer_returncode": observer_rc,
                "run_id": run_id,
            },
            sort_keys=True,
        )
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
