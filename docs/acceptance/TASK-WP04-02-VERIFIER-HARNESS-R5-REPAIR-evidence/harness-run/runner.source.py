"""WP-04-02 R4/R5 verifier harness runner.

Orchestrates structured pytest collection against the Evidence candidate branch
using the public ``pytest_collection_finish`` hook.  Saves version-controlled
evidence with SHA256 manifest.  Supports three mutually-exclusive modes:

    collect-only   (default)  — no DB, no test execution, validates node IDs
                against the 41/20/16/3/2 contract.
    self-test               — run the built-in tool self-tests.
    real-db                 — NOT authorised in this task; placeholder only.

R5 repairs (fail-closed, evidence-integrity, credential-safety):

- F-01: main pin mismatches now fail closed (previously recorded but ignored).
- F-02: candidate/main Git identity is resolved and enforced via ``git``;
        constants printed into JSON are not verification.
- F-03: pytest return code 0 is required before PASS; invocation nonce binds
        collection output to the current run; stale JSON cannot rescue a failed
        invocation.
- F-04: pre-existing evidence leaf is rejected without modification.
- F-06: minimal child environment; case-insensitive/prefix/suffix sensitive-key
        classification; value-level redaction applied to stdout, stderr, JSON
        metadata and exception messages; URL userinfo and credential query
        components redacted.
- F-07: malformed collection JSON produces structured closed failure evidence
        instead of an unguarded ``JSONDecodeError``.

The runner never modifies the candidate branch, never connects to PostgreSQL
in collect-only mode, and never merges main.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path

# Allow running directly from the tg_verifier_tools/verification directory.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from wp04_02_r4_pytest_plugin import (  # noqa: E402
    validate_collection,
)

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
    "docs/acceptance/TASK-TEST-INFRA-PG-FIXTURE-LIFECYCLE-R1-INDEPENDENT-REVERIFY-acceptance.md": "daf2779bda9602a7397ffc01398b940b704091a3529015475542d5e7ad66de89",
    "docs/acceptance/TASK-WP04-02-R1C-05C-01-INDEPENDENT-REVERIFY-R1-evidence/phase-a-20260916-exact-cleanup-plan.json": "635ba4aad0468c15b4360733c784d52f4430f03477a14ef8a271a1e32bada360",
}

MAIN_HEAD = "675217c3a15c0f416aa4462ca6edc491bf99f9f6"
CANDIDATE_BRANCH = "codex/wp04-02-evidence-domain-service"
CANDIDATE_COMMIT = "e942cbcc9e0b5d95a6c7ee46d4d74ee90ff03ad4"
CANDIDATE_PARENT = "af4f2cbbb0a50bd6c215bcaa78dd9fcd98414cc8"

# Sensitive env-key tokens for case-insensitive classification.
# Any env key that contains one of these tokens (case-insensitive), including
# prefix/suffix variants, is treated as sensitive.
_SENSITIVE_ENV_KEY_TOKENS = (
    "password",
    "passwd",
    "token",
    "secret",
    "credential",
    "apikey",
    "accesskey",
    "api_key",
    "access_key",
    "auth",
    "cookie",
    "session",
    "database_url",
    "db_url",
    "dsn",
)

# Query parameter names whose values are treated as sensitive in URLs.
_SENSITIVE_QUERY_PARAMS = (
    "password",
    "passwd",
    "token",
    "secret",
    "apikey",
    "api_key",
    "accesskey",
    "access_key",
    "key",
    "auth",
    "credential",
    "credentials",
    "session",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _is_sensitive_env_key(key: str) -> bool:
    """Return True if *key* matches a sensitive pattern (case-insensitive).

    Matches when the lower-cased key either equals or contains any of the
    configured sensitive tokens.  This covers prefix/suffix variants such as
    ``MY_ACCESS_TOKEN``, ``database_url_backup``, ``SERVICE_PASSWORD``, etc.
    """
    lowered = key.lower().replace("-", "_").replace(".", "_")
    return any(token in lowered for token in _SENSITIVE_ENV_KEY_TOKENS)


def _redact_url_value(value: str) -> str:
    """Redact userinfo and credential-bearing query params in a URL string.

    If the value does not parse as a URL with a network location, it is
    returned unchanged.
    """
    try:
        parsed = urllib.parse.urlparse(value)
    except (ValueError, TypeError):
        return value
    if not parsed.netloc:
        return value

    # Redact userinfo: user:pass@host -> <REDACTED>@host
    redacted_netloc = parsed.netloc
    if "@" in parsed.netloc:
        _, host_part = parsed.netloc.rsplit("@", 1)
        redacted_netloc = f"<REDACTED>@{host_part}"

    # Redact sensitive query parameter values.
    if parsed.query:
        params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        new_pairs: list[str] = []
        for k, v in params:
            if k.lower() in _SENSITIVE_QUERY_PARAMS:
                new_pairs.append(f"{k}=<REDACTED>")
            else:
                new_pairs.append(f"{k}={v}")
        parsed = parsed._replace(query="&".join(new_pairs))

    parsed = parsed._replace(netloc=redacted_netloc)
    return parsed.geturl()


def _redact_value(value: str, sensitive_values: frozenset[str]) -> str:
    """Apply value-level redaction to a string.

    Replaces any known sensitive literal, then applies URL redaction.
    """
    result = value
    for sv in sensitive_values:
        if sv and sv in result:
            result = result.replace(sv, "<REDACTED>")
    result = _redact_url_value(result)
    return result


def redact_env(env: dict[str, str]) -> dict[str, str]:
    """Return a copy with sensitive values replaced by ``<REDACTED>``.

    Uses case-insensitive key classification covering password, token, secret,
    credential, api/access key, auth, cookie, session, database URL and DSN,
    including prefix/suffix variants.
    """
    return {k: ("<REDACTED>" if _is_sensitive_env_key(k) else v) for k, v in sorted(env.items())}


def _collect_sensitive_values(env: dict[str, str]) -> frozenset[str]:
    """Return the set of sensitive literal values present in *env*."""
    return frozenset(v for k, v in env.items() if _is_sensitive_env_key(k) and v)


def find_candidate_root() -> Path:
    """Locate the candidate worktree using ``git worktree list --porcelain``.

    Parses the ``branch`` line (not the ``worktree`` line) to find the
    worktree path associated with :data:`CANDIDATE_BRANCH`.
    """
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    current_path: Path | None = None
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = Path(line[len("worktree ") :]).resolve()
        elif line.startswith("branch "):
            branch_ref = line[len("branch ") :]
            # branch refs look like "refs/heads/<branch-name>"
            branch_name = branch_ref.replace("refs/heads/", "")
            if branch_name == CANDIDATE_BRANCH and current_path is not None:
                return current_path
            current_path = None
    raise RuntimeError(
        f"Candidate worktree for branch '{CANDIDATE_BRANCH}' not found. "
        "Run `git worktree list` to verify."
    )


def _git_root(start: Path) -> Path:
    """Walk up to find the ``.git`` directory or file."""
    current = start.resolve()
    while current != current.parent:
        git_entry = current / ".git"
        if git_entry.exists():
            return current
        current = current.parent
    raise RuntimeError(f"No git root found from {start}")


def _is_git_repo(path: Path) -> bool:
    """Return True if *path* is inside a Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def _git_rev_parse(path: Path, ref: str) -> str:
    """Return the SHA for *ref* in the repo at *path``."""
    result = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=str(path),
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


def _git_symbolic_ref(path: Path) -> str:
    """Return the short symbolic branch name for HEAD in *path*."""
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=str(path),
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip()


def _git_parent_commit(path: Path) -> str:
    """Return the parent SHA of HEAD in *path*."""
    return _git_rev_parse(path, "HEAD~1")


def _git_is_clean(path: Path) -> bool:
    """Return True if the working tree at *path* has no changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(path),
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip() == ""


def verify_main_git_identity(main_root: Path) -> list[str]:
    """Verify main repo identity.  Return list of mismatch descriptions."""
    mismatches: list[str] = []
    if not _is_git_repo(main_root):
        mismatches.append("main is not a git repository")
        return mismatches
    actual_head = _git_rev_parse(main_root, "HEAD")
    if actual_head != MAIN_HEAD:
        mismatches.append(f"main HEAD: expected {MAIN_HEAD[:16]}... got {actual_head[:16]}...")
    return mismatches


def verify_candidate_git_identity(candidate_root: Path) -> list[str]:
    """Verify candidate Git identity: branch, HEAD, parent, cleanliness.

    Returns a list of mismatch descriptions (empty when all checks pass).
    """
    mismatches: list[str] = []
    if not _is_git_repo(candidate_root):
        mismatches.append("candidate is not a git repository")
        return mismatches

    actual_branch = _git_symbolic_ref(candidate_root)
    if actual_branch != CANDIDATE_BRANCH:
        mismatches.append(f"candidate branch: expected {CANDIDATE_BRANCH} got {actual_branch}")

    actual_head = _git_rev_parse(candidate_root, "HEAD")
    if actual_head != CANDIDATE_COMMIT:
        mismatches.append(
            f"candidate HEAD: expected {CANDIDATE_COMMIT[:16]}... got {actual_head[:16]}..."
        )

    actual_parent = _git_parent_commit(candidate_root)
    if actual_parent != CANDIDATE_PARENT:
        mismatches.append(
            f"candidate parent: expected {CANDIDATE_PARENT[:16]}... got {actual_parent[:16]}..."
        )

    if not _git_is_clean(candidate_root):
        mismatches.append("candidate worktree is not clean")

    return mismatches


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


# ---------------------------------------------------------------------------
# Evidence saving
# ---------------------------------------------------------------------------


class EvidenceBundle:
    """Collects artefacts for a single run and writes them with a manifest.

    The manifest is generated by recursively scanning the evidence root after
    all other artefacts exist, so it covers every retained non-manifest file
    (including ``collected-nodeids.json``) with correct byte sizes and SHA-256
    values.  Only the manifest itself is excluded.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, data: object) -> Path:
        """Write *data* as JSON atomically and return the path."""
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        os.replace(str(tmp), str(path))
        return path

    def write_text(self, name: str, text: str) -> Path:
        """Write raw text atomically and return the path."""
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(str(tmp), str(path))
        return path

    def copy_file(self, src: Path, name: str) -> Path:
        """Copy an external file into the evidence bundle."""
        dst = self.root / name
        shutil.copy2(src, dst)
        return dst

    def manifest(self) -> dict[str, object]:
        """Return the manifest (byte sizes + SHA256, excluding itself).

        Generated by recursively scanning the evidence root so that every
        retained non-manifest file is covered.
        """
        entries: dict[str, dict[str, object]] = {}
        manifest_path = (self.root / "manifest.json").resolve()
        for fp in sorted(self.root.rglob("*")):
            if not fp.is_file():
                continue
            if fp.resolve() == manifest_path:
                continue
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
    """Run a subprocess, capture redacted evidence, return the result.

    Builds a minimal child environment (only keys required for the subprocess),
    applies value-level redaction to stdout/stderr/exception text, and records
    redacted env metadata.
    """
    sensitive_values = _collect_sensitive_values(env)
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
            args=argv,
            returncode=124,
            stdout=_redact_value(exc.stdout or "", sensitive_values),
            stderr=_redact_value(
                (exc.stderr or "") + f"\nTIMEOUT after {timeout}s",
                sensitive_values,
            ),
        )
    except Exception as exc:  # noqa: BLE001
        result = subprocess.CompletedProcess(
            args=argv,
            returncode=1,
            stdout="",
            stderr=_redact_value(f"SUBPROCESS_ERROR: {exc}", sensitive_values),
        )

    end = datetime.now(UTC).isoformat()
    bundle.write_text(
        f"{step_name}.stdout.txt",
        _redact_value(result.stdout, sensitive_values),
    )
    bundle.write_text(
        f"{step_name}.stderr.txt",
        _redact_value(result.stderr, sensitive_values),
    )
    bundle.write_json(
        f"{step_name}.meta.json",
        {
            "argv": argv,
            "cwd": str(cwd),
            "env": redact_env(env),
            "start_utc": start,
            "end_utc": end,
            "returncode": result.returncode,
            "timeout_seconds": timeout,
        },
    )
    return result


# ---------------------------------------------------------------------------
# Core: collect-only
# ---------------------------------------------------------------------------


def _build_minimal_env(
    collection_json: Path,
    plugin_dir: Path,
    existing_pythonpath: str,
) -> dict[str, str]:
    """Build an explicit minimal child environment for the pytest subprocess."""
    env: dict[str, str] = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "TG_R4_COLLECTION_JSON": str(collection_json),
        "TG_R4_INVOCATION_NONCE": secrets.token_hex(16),
    }
    # Preserve HOME/USER only if present (needed by some conftest setups).
    for key in ("HOME", "USER", "LANG", "LC_ALL"):
        val = os.environ.get(key)
        if val is not None:
            env[key] = val
    pythonpath = str(plugin_dir)
    if existing_pythonpath:
        pythonpath += ":" + existing_pythonpath
    env["PYTHONPATH"] = pythonpath
    return env


def run_collect_only(
    candidate_root: Path,
    main_root: Path,
    evidence_root: Path,
    *,
    pytest_path: str = "pytest",
) -> dict[str, object]:
    """Execute structured collect-only and return a result dict.

    Fail-closed checks (in order):

    0. Reject pre-existing evidence leaf without modification.
    1. Verify main Git identity (HEAD).
    2. Verify candidate Git identity (branch, HEAD, parent, cleanliness).
    3. Verify main file pins.
    4. Verify candidate file pins.
    5. Require pytest return code 0.
    6. Require current invocation nonce in collection JSON.
    """
    evidence_root = evidence_root.resolve()

    # --- F-04: reject pre-existing evidence leaf ---------------------------
    if evidence_root.exists():
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "evidence_path_exists",
        }

    bundle = EvidenceBundle(evidence_root)

    # --- Save runner + plugin source + SHA256 -------------------------------
    runner_src = Path(__file__).resolve()
    plugin_src = runner_src.parent / "wp04_02_r4_pytest_plugin.py"
    bundle.copy_file(runner_src, "runner.source.py")
    bundle.copy_file(plugin_src, "plugin.source.py")
    bundle.write_json(
        "source-hashes.json",
        {
            "runner": sha256_file(runner_src),
            "plugin": sha256_file(plugin_src),
        },
    )

    # --- F-02: Git identity verification ------------------------------------
    main_git_mismatches = verify_main_git_identity(main_root)
    candidate_git_mismatches = verify_candidate_git_identity(candidate_root)

    # --- F-01 + pin verification --------------------------------------------
    candidate_pin_mismatches = verify_candidate_pins(candidate_root)
    main_pin_mismatches = verify_main_pins(main_root)

    all_mismatches: dict[str, list[str]] = {
        "main_git_mismatches": main_git_mismatches,
        "candidate_git_mismatches": candidate_git_mismatches,
        "candidate_pin_mismatches": candidate_pin_mismatches,
        "main_pin_mismatches": main_pin_mismatches,
    }
    bundle.write_json(
        "baseline-pins.json",
        {
            **all_mismatches,
            "main_head": MAIN_HEAD,
            "candidate_commit": CANDIDATE_COMMIT,
            "candidate_branch": CANDIDATE_BRANCH,
            "candidate_parent": CANDIDATE_PARENT,
        },
    )

    # Fail closed on ANY mismatch (F-01: main mismatches now block too).
    total_mismatches = (
        len(main_git_mismatches)
        + len(candidate_git_mismatches)
        + len(candidate_pin_mismatches)
        + len(main_pin_mismatches)
    )
    if total_mismatches > 0:
        bundle.write_json(
            "result.json",
            {
                "valid": False,
                "verdict": "BLOCKED",
                "reason": "baseline_mismatch",
                **all_mismatches,
            },
        )
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "baseline_mismatch",
            **all_mismatches,
        }

    # --- Structured collection via plugin -----------------------------------
    collection_json = evidence_root / "_collected-nodeids.json"
    # Stage the plugin to an isolated temp dir to avoid __pycache__ conflicts.
    plugin_dir = _stage_plugin_to_temp()
    bundle.write_json(
        "plugin-staging.json",
        {
            "staging_dir": str(plugin_dir),
            "source_package": str(Path(__file__).resolve().parent.parent),
        },
    )

    # Build minimal child environment (F-06: no full inherited env dump).
    env = _build_minimal_env(collection_json, plugin_dir, os.environ.get("PYTHONPATH", ""))
    invocation_nonce = env["TG_R4_INVOCATION_NONCE"]

    # If --pytest points to a python interpreter (e.g. /usr/bin/python3),
    # invoke via ``python3 -m pytest`` so the plugin can be loaded.
    pytest_path_obj = Path(pytest_path)
    is_python_interpreter = pytest_path_obj.name.startswith("python")
    base_argv = (
        [str(pytest_path_obj), "-m", "pytest"] if is_python_interpreter else [str(pytest_path_obj)]
    )

    collect_argv = base_argv + [
        "-p",
        "tg_verifier_tools.verification.wp04_02_r4_pytest_plugin",
        "-p",
        "no:cacheprovider",
        "--collect-only",
        "-q",
        "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue",
        "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit",
        "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only",
        "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay",
    ]

    try:
        result = run_subprocess(
            collect_argv,
            cwd=candidate_root,
            env=env,
            bundle=bundle,
            step_name="collect-only",
        )
    finally:
        # Clean up temporary plugin staging (TOP-AC-05).
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir, ignore_errors=True)

    # --- F-03: require pytest return code 0 --------------------------------
    if result.returncode != 0:
        bundle.write_json(
            "result.json",
            {
                "valid": False,
                "verdict": "BLOCKED",
                "reason": "pytest_nonzero",
                "pytest_returncode": result.returncode,
            },
        )
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "pytest_nonzero",
            "pytest_returncode": result.returncode,
        }

    # --- Read structured output ---------------------------------------------
    if not collection_json.exists():
        bundle.write_json(
            "result.json",
            {
                "valid": False,
                "verdict": "BLOCKED",
                "reason": "collection_json_missing",
            },
        )
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "collection_json_missing",
        }

    # --- F-07: guard malformed JSON -----------------------------------------
    try:
        raw = json.loads(collection_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        bundle.write_json(
            "result.json",
            {
                "valid": False,
                "verdict": "BLOCKED",
                "reason": "collection_json_malformed",
                "error": f"{type(exc).__name__}: {exc}",
            },
        )
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "collection_json_malformed",
        }

    # --- F-03: verify invocation nonce --------------------------------------
    collection_nonce = raw.get("nonce")
    if collection_nonce != invocation_nonce:
        bundle.write_json(
            "result.json",
            {
                "valid": False,
                "verdict": "BLOCKED",
                "reason": "invocation_nonce_mismatch",
            },
        )
        bundle.write_json("manifest.json", bundle.manifest())
        return {
            "valid": False,
            "verdict": "BLOCKED",
            "reason": "invocation_nonce_mismatch",
        }

    nodeids: list[str] = raw.get("nodeids", [])
    validation = validate_collection(nodeids)

    # Move the collection JSON to its final name (F-05: now covered by manifest).
    final_collection = evidence_root / "collected-nodeids.json"
    os.replace(str(collection_json), str(final_collection))

    bundle.write_json(
        "result.json",
        {
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
            "invocation_nonce": invocation_nonce,
        },
    )
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
        description="WP-04-02 R4/R5 verifier harness runner.",
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
    test_file = (
        _HERE.parent.parent / "tg_verifier_tests" / "verification" / "test_wp04_02_r4_runner.py"
    )
    if not test_file.exists():
        # F-09: missing self-test file must return non-zero, not skip.
        print(f"SELF-TEST FAIL: {test_file} not found", file=sys.stderr)
        return 1

    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
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
