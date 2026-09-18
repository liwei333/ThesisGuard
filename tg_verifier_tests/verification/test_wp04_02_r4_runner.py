"""Self-tests for the WP-04-02 R4 verifier harness tool.

Covers:
- validate_collection: correct 41, missing, extra, duplicates, wrong distribution
- _classify_nodeid: known prefixes and unknown input
- compute_distribution: correct totals
- EvidenceBundle: write, manifest, SHA256 consistency
- redact_env: sensitive key redaction
- sha256_file / sha256_text: deterministic hashing
- run_collect_only: end-to-end collect-only against the candidate worktree
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure the tg_verifier_tools package is importable regardless of cwd.
_HERE = Path(__file__).resolve().parent
_TOOLS = _HERE.parent.parent / "tg_verifier_tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from tg_verifier_tools.verification.wp04_02_r4_pytest_plugin import (  # noqa: E402
    DISTRIBUTION,
    EXPECTED_COUNT,
    EXPECTED_NODEIDS,
    _classify_nodeid,
    compute_distribution,
    validate_collection,
)
from tg_verifier_tools.verification.wp04_02_r4_runner import (  # noqa: E402
    EvidenceBundle,
    redact_env,
    sha256_file,
    sha256_text,
)

# ---------------------------------------------------------------------------
# validate_collection
# ---------------------------------------------------------------------------


def test_validate_collection_correct_41() -> None:
    """The exact expected 41 node IDs must validate."""
    result = validate_collection(list(EXPECTED_NODEIDS))
    assert result["valid"] is True
    assert result["count"] == EXPECTED_COUNT == 41
    assert result["distribution"] == DISTRIBUTION
    assert result["missing"] == []
    assert result["extra"] == []
    assert result["duplicates"] == []
    assert result["unclassified"] == []


def test_validate_collection_missing_one() -> None:
    """Removing one node must invalidate and report it missing."""
    incomplete = list(EXPECTED_NODEIDS[1:])  # drop first
    result = validate_collection(incomplete)
    assert result["valid"] is False
    assert result["count"] == 40
    assert EXPECTED_NODEIDS[0] in result["missing"]


def test_validate_collection_extra_one() -> None:
    """Adding an unknown node must invalidate and report it extra."""
    extra = list(EXPECTED_NODEIDS) + ["tests/test_evidence_services.py::test_unknown_param[extra]"]
    result = validate_collection(extra)
    assert result["valid"] is False
    assert result["count"] == 42
    assert any("test_unknown_param" in e for e in result["extra"])


def test_validate_collection_duplicate() -> None:
    """Duplicate node IDs must be detected."""
    dup = list(EXPECTED_NODEIDS) + [EXPECTED_NODEIDS[0]]
    result = validate_collection(dup)
    assert result["valid"] is False
    assert EXPECTED_NODEIDS[0] in result["duplicates"]


def test_validate_collection_wrong_distribution() -> None:
    """Swapping one node for another prefix breaks the distribution."""
    # Replace one forbidden node with an extra allowed node.
    modified = list(EXPECTED_NODEIDS)
    # Find first forbidden node and replace with a fabricated allowed node.
    for i, nid in enumerate(modified):
        if "forbidden_status_commit_fresh_no_residue" in nid:
            modified[i] = (
                "tests/test_evidence_services.py::"
                "test_r1c05c01_allowed_routing_history_audit"
                "[omitted-VERIFIED-same-DUPE]"
            )
            break
    result = validate_collection(modified)
    # Distribution no longer matches even though count is still 41.
    assert result["count"] == 41
    assert result["distribution"] != DISTRIBUTION
    assert result["valid"] is False


def test_validate_collection_empty() -> None:
    """Empty collection must be invalid with all 41 missing."""
    result = validate_collection([])
    assert result["valid"] is False
    assert result["count"] == 0
    assert len(result["missing"]) == EXPECTED_COUNT


# ---------------------------------------------------------------------------
# _classify_nodeid
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("nodeid", "expected"),
    [
        (
            "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[PENDING_REVIEW-same]",
            "forbidden_status_commit_fresh_no_residue",
        ),
        (
            "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-VERIFIED-same]",
            "allowed_routing_history_audit",
        ),
        (
            "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only[direct]",
            "committed_exact_replay_read_only",
        ),
        (
            "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay[underlying]",
            "legacy_forbidden_prior_committed_replay",
        ),
        ("tests/test_evidence_services.py::test_unknown_thing[x]", None),
        ("", None),
    ],
)
def test_classify_nodeid(nodeid: str, expected: str | None) -> None:
    assert _classify_nodeid(nodeid) == expected


# ---------------------------------------------------------------------------
# compute_distribution
# ---------------------------------------------------------------------------


def test_compute_distribution_correct() -> None:
    dist = compute_distribution(list(EXPECTED_NODEIDS))
    assert dist == DISTRIBUTION
    assert sum(dist.values()) == EXPECTED_COUNT


def test_compute_distribution_empty() -> None:
    dist = compute_distribution([])
    assert dist == dict.fromkeys(DISTRIBUTION, 0)


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def test_sha256_text_deterministic() -> None:
    assert sha256_text("hello") == sha256_text("hello")
    assert sha256_text("hello") != sha256_text("world")


def test_sha256_file_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "sample.txt"
    p.write_text("content", encoding="utf-8")
    assert sha256_file(p) == sha256_file(p)
    assert sha256_file(p) == sha256_text("content")


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------


def test_redact_env_masks_sensitive() -> None:
    env = {
        "TG_TEST_ADMIN_DATABASE_URL": "postgresql://secret",
        "HOME": "/Users/test",
        "AWS_SECRET_ACCESS_KEY": "shhh",
    }
    redacted = redact_env(env)
    assert redacted["TG_TEST_ADMIN_DATABASE_URL"] == "<REDACTED>"
    assert redacted["AWS_SECRET_ACCESS_KEY"] == "<REDACTED>"
    assert redacted["HOME"] == "/Users/test"


def test_redact_env_no_sensitive() -> None:
    env = {"HOME": "/Users/test", "PATH": "/usr/bin"}
    assert redact_env(env) == env


# ---------------------------------------------------------------------------
# EvidenceBundle
# ---------------------------------------------------------------------------


def test_evidence_bundle_write_and_manifest(tmp_path: Path) -> None:
    bundle = EvidenceBundle(tmp_path / "evidence")
    bundle.write_json("data.json", {"key": "value"})
    bundle.write_text("log.txt", "hello")

    manifest = bundle.manifest()
    assert "data.json" in manifest["artifacts"]
    assert "log.txt" in manifest["artifacts"]
    assert manifest["artifacts"]["data.json"]["bytes"] > 0
    assert manifest["artifacts"]["data.json"]["sha256"] == sha256_file(bundle.root / "data.json")


def test_evidence_bundle_manifest_excludes_itself(tmp_path: Path) -> None:
    """Writing the manifest must not create a recursive hash."""
    bundle = EvidenceBundle(tmp_path / "evidence")
    bundle.write_text("a.txt", "A")
    manifest = bundle.manifest()
    # Manifest is computed from tracked files; it is not yet written.
    assert "manifest.json" not in manifest["artifacts"]


# ---------------------------------------------------------------------------
# End-to-end: collect-only against the candidate worktree
# ---------------------------------------------------------------------------


def _find_candidate_root() -> Path | None:
    """Return the candidate worktree path, or None if not found."""
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("worktree ") and "codex-wp04-02-evidence-domain-service" in line:
                return Path(line[len("worktree ") :]).resolve()
    except Exception:  # noqa: BLE001
        return None
    return None


def _find_main_root() -> Path:
    """Return the main ThesisGuard repo root.

    Tries the well-known path first, then falls back to git discovery.
    """
    well_known = Path("/Users/qianduoduo/Desktop/AI_app/ThesisGuard")
    if (well_known / "docs" / "WP04_EVIDENCE_DOMAIN_CONTRACT.md").exists():
        return well_known
    # Fallback: walk up from this file to find a dir containing AGENTS.md.
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "AGENTS.md").exists() and (current / "docs").is_dir():
            return current
        current = current.parent
    return well_known


@pytest.mark.skipif(
    _find_candidate_root() is None,
    reason="Candidate worktree not available on this machine",
)
def test_collect_only_end_to_end(tmp_path: Path) -> None:
    """Run the runner in collect-only mode and verify the 41/20/16/3/2 result."""
    from tg_verifier_tools.verification.wp04_02_r4_runner import run_collect_only

    candidate_root = _find_candidate_root()
    assert candidate_root is not None
    main_root = _find_main_root()
    evidence_dir = tmp_path / "evidence"

    # Use a pytest whose Python has boto3 (required by candidate conftest.py).
    pytest_exec = "/opt/homebrew/bin/pytest"
    conda_pytest = shutil.which("pytest") or "pytest"
    if conda_pytest != pytest_exec:
        # Check if the conda pytest's Python has boto3.
        try:
            r = subprocess.run(
                [conda_pytest, "-c", "import boto3"],
                capture_output=True,
                timeout=15,
            )
            if r.returncode == 0:
                pytest_exec = conda_pytest
        except Exception:
            pass

    result = run_collect_only(
        candidate_root=candidate_root,
        main_root=main_root,
        evidence_root=evidence_dir,
        pytest_path=pytest_exec,
    )

    assert result["valid"] is True, f"collect-only failed: {result}"
    assert result["count"] == 41
    assert result["distribution"] == DISTRIBUTION

    # Verify evidence artefacts exist.
    assert (evidence_dir / "result.json").exists()
    assert (evidence_dir / "collected-nodeids.json").exists()
    assert (evidence_dir / "manifest.json").exists()
    assert (evidence_dir / "source-hashes.json").exists()

    # Verify manifest integrity.
    manifest = json.loads((evidence_dir / "manifest.json").read_text())
    for name, info in manifest["artifacts"].items():
        fp = evidence_dir / name
        if fp.exists():
            actual = sha256_file(fp)
            assert actual == info["sha256"], f"manifest hash mismatch for {name}"
