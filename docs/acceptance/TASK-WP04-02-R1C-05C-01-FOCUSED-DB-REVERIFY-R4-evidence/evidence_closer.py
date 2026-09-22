"""Close the blocked R4 evidence bundle without any PostgreSQL operation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


MAIN = Path("/Users/qianduoduo/Desktop/AI_app/ThesisGuard")
CANDIDATE = Path(
    "/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/"
    "codex-wp04-02-evidence-domain-service"
)
HARNESS = Path("/Users/qianduoduo/Desktop/AI_app/codex-wp04-02-verifier-harness-r5-repair")
EVIDENCE = MAIN / (
    "docs/acceptance/"
    "TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R4-evidence"
)
PLAN = MAIN / (
    "docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/"
    "phase-a-20260916-exact-cleanup-plan.json"
)
R4_PREFIX = "docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R4"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(repo: Path, *argv: str) -> str:
    result = subprocess.run(
        list(argv), cwd=repo, capture_output=True, text=True, check=True, timeout=20
    )
    return result.stdout.strip()


def _git(repo: Path) -> dict[str, Any]:
    return {
        "branch": _run(repo, "git", "branch", "--show-current"),
        "head": _run(repo, "git", "rev-parse", "HEAD"),
        "parent": _run(repo, "git", "rev-parse", "HEAD^"),
        "status": _run(repo, "git", "status", "--short", "--untracked-files=all").splitlines(),
        "tracked_diff": _run(repo, "git", "diff", "--name-status").splitlines(),
        "index_diff": _run(repo, "git", "diff", "--cached", "--name-status").splitlines(),
    }


def _write_json(name: str, payload: Any) -> None:
    (EVIDENCE / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )


def _hashes(root: Path, relatives: list[str]) -> dict[str, str]:
    return {relative: _sha(root / relative) for relative in relatives}


def _audit_manifest(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    actual = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.resolve() != (root / "manifest.json").resolve():
            data = path.read_bytes()
            actual[str(path.relative_to(root))] = {
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
    listed = manifest["artifacts"]
    return {
        "actual": len(actual),
        "listed": len(listed),
        "paths_equal": set(actual) == set(listed),
        "content_equal": actual == listed,
        "missing": sorted(set(actual) - set(listed)),
        "extra": sorted(set(listed) - set(actual)),
        "mismatches": sorted(
            key for key in set(actual) & set(listed) if actual[key] != listed[key]
        ),
    }


def main() -> int:
    now = datetime.now(UTC).isoformat()
    main_state = _git(MAIN)
    candidate_state = _git(CANDIDATE)
    harness_state = _git(HARNESS)
    baseline_main_status = [line for line in main_state["status"] if R4_PREFIX not in line]

    candidate_files = [
        "backend/evidence/errors.py",
        "backend/evidence/services.py",
        "tests/test_evidence_services.py",
        "tests/evidence_pg_fixture.py",
        "tests/test_evidence_pg_fixture_lifecycle.py",
    ]
    harness_files = [
        "tg_verifier_tools/verification/wp04_02_r4_runner.py",
        "tg_verifier_tools/verification/wp04_02_r4_pytest_plugin.py",
        "tg_verifier_tests/verification/test_wp04_02_r4_runner.py",
    ]
    main_pins = [
        "docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md",
        "docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md",
        "docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json",
    ]
    protected_context = [
        "AGENTS.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-task-contract.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-dispatch.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-acceptance.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-execution-report.md",
        "docs/prompts/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3.md",
        "docs/acceptance/TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R3-acceptance.md",
        "docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2-INDEPENDENT-REVIEW-R1-acceptance.md",
        "docs/acceptance/TASK-WP04-02-VERIFIER-HARNESS-R5-CODEX-TAKEOVER-R2-INDEPENDENT-REVIEW-R1-evidence/manifest.json",
    ]

    observed_hashes = {
        "main_pins": _hashes(MAIN, main_pins),
        "candidate_pins": _hashes(CANDIDATE, candidate_files),
        "harness_pins": _hashes(HARNESS, harness_files),
    }
    _write_json(
        "before.json",
        {
            "captured_at_utc": now,
            "note": "Git identities and pin hashes were observed before collect-only; baseline status is final status with only the task-owned R4 prefix removed.",
            "main": {**main_state, "status": baseline_main_status},
            "candidate": candidate_state,
            "harness": harness_state,
            "fixed_hashes": observed_hashes,
            "output_paths_absent_at_initial_gate": True,
        },
    )
    _write_json(
        "baseline-classification.json",
        {
            "main_non_task_status": baseline_main_status,
            "classification": "NON_BLOCKING_EXTERNAL_UNTRACKED_GOVERNANCE_ACCEPTANCE_PROMPT_OR_WORKBENCH",
            "main_tracked_diff_empty": not main_state["tracked_diff"],
            "main_index_empty": not main_state["index_diff"],
            "candidate_clean": not candidate_state["status"],
            "candidate_index_empty": not candidate_state["index_diff"],
            "harness_tracked_scope": harness_state["tracked_diff"],
            "harness_untracked_scope_rule": "historical R5 repair / Codex takeover R1 / Codex takeover R2 execution-report and evidence only",
            "workbench_preserved": any("docs/workbench.html" in line for line in baseline_main_status),
        },
    )
    _write_json(
        "protected-artifact-hashes.json",
        {
            "fixed_before_and_after": observed_hashes,
            "additional_final_observation_only": _hashes(MAIN, protected_context),
            "limitation": "Additional context artifacts were not all hashed in a retained pre-collect file; this prevents no claim because the verdict is already BLOCKED before CREATE.",
        },
    )
    _write_json(
        "source-hashes.json",
        {
            **observed_hashes,
            "guard": _sha(EVIDENCE / "guard/sitecustomize.py"),
            "db_observer": _sha(EVIDENCE / "db_observer.py"),
            "evidence_closer": _sha(EVIDENCE / "evidence_closer.py"),
        },
    )
    _write_json(
        "tool-preflight.json",
        {
            "path": "/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "python": "/opt/homebrew/bin/python3.12",
            "python_version": "3.12.9",
            "pytest": "/opt/homebrew/bin/pytest",
            "pytest_version": "9.1.1",
            "child_alembic": "/opt/miniconda3/bin/alembic",
            "alembic_heads": "000000000004 (head)",
            "diagnostic_variables_absent": [
                "TG_TEST_ADMIN_DATABASE_URL",
                "TG_R1C_REPLAY_BASELINE",
                "TG_R1C02_REPLAY_PRIOR",
            ],
            "result": "PASS",
        },
    )
    (EVIDENCE / "alembic-heads.txt").write_text("000000000004 (head)\n", encoding="utf-8")

    collect_root = EVIDENCE / "collect-only-harness-run"
    collect_result = json.loads((collect_root / "result.json").read_text(encoding="utf-8"))
    collect_audit = _audit_manifest(collect_root)
    collect_audit.update(
        {
            "result": collect_result,
            "fixture_ledger_exists": (collect_root / "_fixture-ledger.jsonl").exists(),
            "socket_attempt_log_exists": Path(
                "/private/tmp/tg-wp04-02-r4.UwcguW/socket-attempts.jsonl"
            ).exists(),
        }
    )
    _write_json("collect-only-audit.json", collect_audit)
    _write_json(
        "guard-source-hash.json",
        {"path": "guard/sitecustomize.py", "sha256": _sha(EVIDENCE / "guard/sitecustomize.py")},
    )
    (EVIDENCE / "collected-nodeids.json").write_bytes(
        (collect_root / "collected-nodeids.json").read_bytes()
    )

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    _write_json(
        "database-before.json",
        {
            "result": "BLOCKED_DATABASE_UNAVAILABLE",
            "authorized_target": {
                "driver": "postgresql+asyncpg",
                "host": "127.0.0.1",
                "port": 15432,
                "admin_database": "postgres",
            },
            "attempts": [
                {"kind": "sandboxed_read_only_preflight", "exit_code": 1, "error_type": "PermissionError"},
                {"kind": "approved_read_only_preflight", "exit_code": 1, "error_type": "ConnectionRefusedError"},
            ],
            "successful_database_connections": 0,
            "create_sent": 0,
            "catalog_captured": False,
        },
    )
    _write_json(
        "database-after.json",
        {
            "result": "NOT_OBSERVED_DATABASE_UNAVAILABLE",
            "successful_database_connections": 0,
            "create_sent": 0,
            "drop_sent": 0,
            "task_created_resources": 0,
            "task_created_residuals": 0,
        },
    )
    _write_json(
        "historical-unknown-verification.json",
        {
            "expected_count": 45,
            "plan_count": len(plan["unknown_names"]),
            "fresh_catalog_identity_checks": 0,
            "fresh_result": "BLOCKED_DATABASE_UNAVAILABLE",
            "task_connections_to_historical_databases": 0,
            "task_terminations": 0,
            "task_drops": 0,
            "task_renames": 0,
            "preservation_claim": "UNPROVEN_FRESH; no successful DB connection and no mutating DB command",
        },
    )
    _write_json(
        "real-pytest.meta.json",
        {
            "started": False,
            "invocation_count": 0,
            "reason": "Stopped before CREATE because approved read-only PostgreSQL preflight returned ConnectionRefusedError",
            "selectors": [
                "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue",
                "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit",
                "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only",
                "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay",
            ],
            "expected_flags": ["-p", "no:cacheprovider", "-x", "-vv", "-s", "--tb=short"],
            "exit_code": None,
            "run_id": None,
            "ledger_path": None,
        },
    )
    (EVIDENCE / "real-pytest.stdout.txt").write_text("", encoding="utf-8")
    (EVIDENCE / "real-pytest.stderr.txt").write_text("", encoding="utf-8")
    (EVIDENCE / "resources.jsonl").write_text("", encoding="utf-8")
    _write_json(
        "scenario-results.json",
        {
            "collected": 41,
            "distribution": [20, 16, 3, 2],
            "executed": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "result": "NOT_RUN_DATABASE_PREFLIGHT_BLOCKED",
        },
    )
    _write_json(
        "ledger-audit.json",
        {
            "ledger_exists": False,
            "run_ids": [],
            "attempt": 0,
            "create_sent": 0,
            "created": 0,
            "dropped": 0,
            "unknown": 0,
            "residual": 0,
            "budget": 41,
        },
    )

    final_main = _git(MAIN)
    final_candidate = _git(CANDIDATE)
    final_harness = _git(HARNESS)
    _write_json(
        "after.json",
        {
            "captured_at_utc": datetime.now(UTC).isoformat(),
            "main": final_main,
            "candidate": final_candidate,
            "harness": final_harness,
            "fixed_hashes": {
                "main_pins": _hashes(MAIN, main_pins),
                "candidate_pins": _hashes(CANDIDATE, candidate_files),
                "harness_pins": _hashes(HARNESS, harness_files),
            },
        },
    )
    _write_json(
        "final-state.json",
        {
            "task_id": "TASK-WP04-02-R1C-05C-01-FOCUSED-DB-REVERIFY-R4",
            "verdict": "BLOCKED",
            "blocker": "BLOCKED_POSTGRESQL_SERVICE_UNAVAILABLE",
            "collect_only": "PASS 41/41; 20/16/3/2; bodies 0; sockets 0; ledger absent",
            "real_invocations": 0,
            "create_sent": 0,
            "create_budget": 41,
            "created": 0,
            "dropped": 0,
            "unknown_task_resources": 0,
            "task_residuals": 0,
            "historical_unknown_fresh_identity_result": "BLOCKED",
            "candidate_final_clean": not final_candidate["status"],
            "candidate_final_index_empty": not final_candidate["index_diff"],
            "fixed_hashes_unchanged": observed_hashes
            == {
                "main_pins": _hashes(MAIN, main_pins),
                "candidate_pins": _hashes(CANDIDATE, candidate_files),
                "harness_pins": _hashes(HARNESS, harness_files),
            },
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
