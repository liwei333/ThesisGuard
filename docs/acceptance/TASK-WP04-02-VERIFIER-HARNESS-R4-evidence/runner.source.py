"""WP-04-02 R4 verifier harness runner.

Orchestrates structured pytest collection against the Evidence candidate branch
using the public ``pytest_collection_finish`` hook.  Saves version-controlled
evidence with SHA256 manifest.  Supports three mutually-exclusive modes:

    collect-only   (default)  — no DB, no test execution, validates node IDs
                against the 41/20/16/3/2 contract.
    self-test               — run the built-in tool self-tests.
    real-db                 — NOT authorised in this task; placeholder only.

The runner never modifies the candidate branch, never connects to PostgreSQL
in collect-only mode, and never merges main.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

# Allow running directly from the tg_verifier_tools/verification directory.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from wp04_02_r4_pytest_plugin import (  # noqa: E402
    DISTRIBUTION,
    EXPECTED_COUNT,
    EXPECTED_NODEIDS,
    validate_collection,
)


def _stage_plugin_to_temp() -> Path:
    """Copy the plugin and its package to a fresh temp directory.

    Returns the path to the temp directory containing the ``tg_verifier_tools``
    package.  Using an isolated temp dir avoids any ``__pycache__`` or
    module-name conflicts in the original worktree.
    """
    src_pkg = _HERE.parent  # .../tg_verifier_tools
    dst_root = Path(tempfile.mkdtemp(prefix="tg_r4_plugin_"))
    shutil.copytree(src_pkg, dst_root / src_pkg.name)
    # Remove any copied __pycache__ to avoid stale bytecode.
    for pycache in (dst_root / src_pkg.name).rglob("__pycache__"):
        shutil.rmtree(pycache)
    return dst_root

# ---------------------------------------------------------------------------
# Pinned baselines (verified before any non-DB operation)
# ---------------------------------------------------------------------------

CANDIDATE_SHA_PINS: dict[str, str] = {
    "backend/evidence/errors.py": "3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec",
    "backend/evidence/services.py": "7ce76b02928019347625048e7d0acb523d74168cd6bbbdf03184163ac277f959",
    "tests/test_evidence_services.py": "c54e2306b7ec9625f0498faeebd8a23ceb55c6366769ac0d944f228e2aa84851",
    "tests/evidence_pg_fixture.py": "bb84518f354f2f7752881fb529dcd6df31b58085bf32d6728c2ccf6998c3e9db",
    "tests/test_evidence_pg_fixture_lifecycle.py": "3887a89945a770ed22bac5839ff6a61e5daf47cb05a8b0105d1cfce8f3c12fc7",
}

MAIN_SHA_PINS: dict[str, str] = {
    "docs/WP04_EVIDENCE_DOMAIN_CONTRACT.md": "b179ecc6ea60ffed75f7179a2d36e47ad2b55153f6d4fa62b8be7e4926fd1288",
    "docs/WP04_EVIDENCE_CORRECTION_POLICY_ADDENDUM_2026-09-16.md": "af345e2604497171dc2d2ef13489ec3cffa1528caa5175c2ccf245b6a987a955",
    "docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md": "daf2779bda9602a7397ffc01398b940b704091a3529014775542d5e7ad66de89",
    "docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json": "635ba4aad0468c15b4360733c784d52f4430f03477a14ef8a271a1e32bada360",
}

CANDIDATE_BRANCH = "codex/wp04-02-evidence-domain-service"
CANDIDATE_COMMIT = "e942cbcc9e0b595a6c7ee46d4d74ee90ff03ad4"

# Sensitive env vars that must never appear in evidence logs.
_SENSITIVE_ENV_KEYS = {
    "TG_TEST_ADMIN_DATABASE_URL",
    "TG_R1C_REPLAY_BASELINE",
    "TG_R1C02_REPLAY_PRIOR",
    "DATABASE_URL",
    "POSTGRES_PASSWORD",
    "PGPASSWORD",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    """Return hex SHA256 of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    """Return hex SHA256 of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_env(env: dict[str, str]) -> dict[str, str]:
    """Return a copy with sensitive values replaced by ``<REDACTED>``."""
    return {k: ("<REDACTED>" if k in _SENSITIVE_ENV_KEYS else v) for k, v in sorted(env.items())}


def find_candidate_root() -> Path:
    """Locate the candidate worktree using ``git worktree list``."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("worktree ") and CANDIDATE_BRANCH in line:
            return Path(line[len("worktree ") :]).resolve()
    raise RuntimeError(
        f"Candidate worktree for branch '{CANDIDATE_BRANCH}' not found. "
        "Run `git worktree list` to verify."
    )


def verify_candidate_pins(candidate_root: Path) -> list[str]:
    """Check the five candidate SHA256 pins.  Return list of mismatches."""
    mismatches: list[str] = []
    for rel, expected in CANDIDATE_SHA_PINS.items():
        actual = sha256_file(candidate_root / rel)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected[:16]}... got {actual[:16]}...")
    return mismatches


def verify_main_pins(main_root: Path) -> list[str]:
    """Check the four main branch SHA256 pins.  Return list of mismatches."""
    mismatches: list[str] = []
    for rel, expected in MAIN_SHA_PINS.items():
        actual = sha256_file(main_root / rel)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected[:16]}... got {actual[:16]}...")
    return mismatches


def find_git_root(start: Path) -> Path:
    """Walk up to find the ``.git`` directory."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError(f"No git root found from {start}")


# ---------------------------------------------------------------------------
# Evidence saving
# ---------------------------------------------------------------------------


class EvidenceBundle:
    """Collects artefacts for a single run and writes them with a manifest."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._files: list[Path] = []

    def write_json(self, name: str, data: object) -> Path:
        """Write *data* as JSON and track the file for the manifest."""
        path = self.root / name
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        self._files.append(path)
        return path

    def write_text(self, name: str, text: str) -> Path:
        """Write raw text and track the file for the manifest."""
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        self._files.append(path)
        return path

    def copy_file(self, src: Path, name: str) -> Path:
        """Copy an external file into the evidence bundle."""
        dst = self.root / name
        shutil.copy2(src, dst)
        self._files.append(dst)
        return dst

    def manifest(self) -> dict[str, object]:
        """Return the manifest (byte sizes + SHA256, excluding itself)."""
        entries = {}
        for fp in sorted(self._files):
            data = fp.read_bytes()
            entries[str(fp.relative_to(self.root))] = {
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        return {"artifacts": entries}


# ---------------------------------------------------------------------------
# Subprocess execution with evidence capture
# ---------------------------------------------------------------------------


def run_subprocess(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    bundle: EvidenceBundle,
    step_name: str,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess, capture redacted evidence, return the result."""
    start = datetime.now(UTC).isoformat()
    try:
        result = subprocess.run(
            argv,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            argv=argv,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nTIMEOUT after {timeout}s",
        )
    except Exception as exc:  # noqa: BLE001
        result = subprocess.CompletedProcess(
            argv=argv, returncode=1, stdout="", stderr=f"SUBPROCESS_ERROR: {exc}"
        )

    end = datetime.now(UTC).isoformat()
    bundle.write_text(f"{step_name}.stdout.txt", result.stdout)
    bundle.write_text(f"{step_name}.stderr.txt", result.stderr)
    bundle.write_json(f"{step_name}.meta.json", {
        "argv": argv,
        "cwd": str(cwd),
        "env": redact_env(env),
        "start_utc": start,
        "end_utc": end,
        "returncode": result.returncode,
        "timeout_seconds": timeout,
    })
    return result


# ---------------------------------------------------------------------------
# Core: collect-only
# ---------------------------------------------------------------------------


def run_collect_only(
    candidate_root: Path,
    main_root: Path,
    evidence_root: Path,
    *,
    pytest_path: str = "pytest",
) -> dict[str, object]:
    """Execute structured collect-only and return a result dict."""
    bundle = EvidenceBundle(evidence_root)

    # --- Save runner + plugin source + SHA256 -------------------------------
    runner_src = Path(__file__).resolve()
    plugin_src = runner_src.parent / "wp04_02_r4_pytest_plugin.py"
    bundle.copy_file(runner_src, "runner.source.py")
    bundle.copy_file(plugin_src, "plugin.source.py")
    bundle.write_json("source-hashes.json", {
        "runner": sha256_file(runner_src),
        "plugin": sha256_file(plugin_src),
    })

    # --- Baseline pin verification ------------------------------------------
    candidate_mismatches = verify_candidate_pins(candidate_root)
    main_mismatches = verify_main_pins(main_root)
    bundle.write_json("baseline-pins.json", {
        "candidate_mismatches": candidate_mismatches,
        "main_mismatches": main_mismatches,
        "candidate_commit": CANDIDATE_COMMIT,
        "candidate_branch": CANDIDATE_BRANCH,
    })

    if candidate_mismatches:
        bundle.write_json("result.json", {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "candidate_pin_mismatch",
            "candidate_mismatches": candidate_mismatches,
        })
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "candidate_pin_mismatch",
            "mismatches": candidate_mismatches,
        }

    # --- Structured collection via plugin -----------------------------------
    collection_json = evidence_root / "collected-nodeids.json"
    env = os.environ.copy()
    env["TG_R4_COLLECTION_JSON"] = str(collection_json)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Stage the plugin to an isolated temp dir to avoid __pycache__ conflicts.
    plugin_dir = _stage_plugin_to_temp()
    bundle.write_json("plugin-staging.json", {
        "staging_dir": str(plugin_dir),
        "source_package": str(Path(__file__).resolve().parent.parent),
    })
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(plugin_dir) + (":" + existing_pythonpath if existing_pythonpath else "")
    )

    # If --pytest points to a python interpreter (e.g. /usr/bin/python3),
    # invoke via ``python3 -m pytest`` so the plugin can be loaded.
    pytest_path_obj = Path(pytest_path)
    is_python_interpreter = pytest_path_obj.name.startswith("python")
    base_argv = [str(pytest_path_obj), "-m", "pytest"] if is_python_interpreter else [str(pytest_path_obj)]

    collect_argv = base_argv + [
        "-p", "tg_verifier_tools.verification.wp04_02_r4_pytest_plugin",
        "-p", "no:cacheprovider",
        "--collect-only",
        "-q",
        "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue",
        "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit",
        "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only",
        "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay",
    ]

    result = run_subprocess(
        collect_argv,
        cwd=candidate_root,
        env=env,
        bundle=bundle,
        step_name="collect-only",
    )

    # --- Read structured output ---------------------------------------------
    if not collection_json.exists():
        bundle.write_json("result.json", {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "collection_json_missing",
            "stdout_excerpt": result.stdout[:500],
            "stderr_excerpt": result.stderr[:500],
        })
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "collection_json_missing",
        }

    raw = json.loads(collection_json.read_text(encoding="utf-8"))
    nodeids: list[str] = raw.get("nodeids", [])
    validation = validate_collection(nodeids)
    collection_json.rename(evidence_root / "collected-nodeids.json")

    bundle.write_json("result.json", {
        "valid": validation["valid"],
        "verdict": "PASS" if validation["valid"] else "FAIL",
        "count": validation["count"],
        "expected_count": validation["expected_count"],
        "distribution": validation["distribution"],
        "expected_distribution": validation["expected_distribution"],
        "missing": validation["missing"],
        "extra": validation["extra"],
        "duplicates": validation["duplicates"],
        "unclassified": validation["unclassified"],
        "pytest_returncode": result.returncode,
    })
    bundle.write_json("manifest.json", bundle.manifest())

    return {
        "valid": validation["valid"],
        "verdict": "PASS" if validation["valid"] else "FAIL",
        "count": validation["count"],
        "distribution": validation["distribution"],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="WP-04-02 R4 verifier harness runner.",
    )
    parser.add_argument(
        "--mode",
        choices=["collect-only", "self-test"],
        default="collect-only",
        help="Execution mode (default: collect-only)",
    )
    parser.add_argument(
        "--candidate-root",
        type=Path,
        required=True,
        help="Absolute path to the candidate worktree root",
    )
    parser.add_argument(
        "--main-root",
        type=Path,
        required=True,
        help="Absolute path to the main repo root",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=None,
        help="Evidence output directory (default: ./evidence under cwd)",
    )
    parser.add_argument(
        "--pytest",
        default="pytest",
        help="pytest executable (default: pytest on PATH)",
    )
    args = parser.parse_args(argv)

    evidence_dir: Path = args.evidence_dir or (Path.cwd() / "evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "self-test":
        return _run_self_tests(args)

    result = run_collect_only(
        candidate_root=args.candidate_root.resolve(),
        main_root=args.main_root.resolve(),
        evidence_root=evidence_dir.resolve(),
        pytest_path=args.pytest,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("valid") else 1


def _run_self_tests(args: argparse.Namespace) -> int:
    """Invoke pytest on the tool's own test file and capture evidence."""
    test_file = _HERE.parent.parent / "tg_verifier_tests" / "verification" / "test_wp04_02_r4_runner.py"
    if not test_file.exists():
        print(f"SELF-TEST SKIP: {test_file} not found (tests not yet written)")
        return 0

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [args.pytest, str(test_file), "-v", "--tb=short"],
        cwd=str(args.main_root.resolve()),
        env=env,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
