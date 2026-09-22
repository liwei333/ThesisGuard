"""WP-02 R4 structured pytest collection plugin.

Uses the public ``pytest_collection_finish(session)`` hook to capture the final
collected ``nodeid`` list from ``session.items``.  Writes a JSON artefact that
the R4 runner consumes.  No terminal-output parsing, no ``<Coroutine ...>``
string matching, no dependency on the display format.

The plugin is loaded via ``-p tools.verification.wp04_02_r4_pytest_plugin``.
The output path is taken from the ``TG_R4_COLLECTION_JSON`` environment variable;
if unset the plugin writes nothing (harmless no-op).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Expected focused node IDs (41 total, 20/16/3/2 distribution).
# Kept here as a single source of truth shared by the plugin and the runner.
# ---------------------------------------------------------------------------

EXPECTED_NODEIDS: tuple[str, ...] = (
    # 20 × forbidden_status_commit_fresh_no_residue  (4 routes × 5 denied statuses)
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[PENDING_REVIEW-same]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[PENDING_REVIEW-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[PENDING_REVIEW-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[PENDING_REVIEW-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[DISPUTED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[DISPUTED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[DISPUTED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[DISPUTED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[REJECTED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[INVALIDATED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[INVALIDATED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[INVALIDATED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[INVALIDATED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[RETRACTED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[RETRACTED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[RETRACTED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_forbidden_status_commit_fresh_no_residue[RETRACTED-underlying]",
    # 16 × allowed_routing_history_audit  (4 routes × 2 statuses × 2 explicit_none)
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-VERIFIED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-VERIFIED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-VERIFIED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-VERIFIED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-UNREVIEWED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-UNREVIEWED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-UNREVIEWED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[omitted-UNREVIEWED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-VERIFIED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-VERIFIED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-VERIFIED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-VERIFIED-underlying]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-UNREVIEWED-same]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-UNREVIEWED-automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-UNREVIEWED-direct]",
    "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[none-UNREVIEWED-underlying]",
    # 3 × committed_exact_replay_read_only
    "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only[automatic]",
    "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only[direct]",
    "tests/test_evidence_services.py::test_r1c05c01_committed_exact_replay_read_only[underlying]",
    # 2 × legacy_forbidden_prior_committed_replay
    "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay[direct]",
    "tests/test_evidence_services.py::test_r1c05c01_legacy_forbidden_prior_committed_replay[underlying]",
)

EXPECTED_COUNT = 41

DISTRIBUTION = {
    "forbidden_status_commit_fresh_no_residue": 20,
    "allowed_routing_history_audit": 16,
    "committed_exact_replay_read_only": 3,
    "legacy_forbidden_prior_committed_replay": 2,
}


def _classify_nodeid(nodeid: str) -> str | None:
    """Return the test-function prefix (without parameterisation) or ``None``."""
    if "test_r1c05c01_forbidden_status_commit_fresh_no_residue" in nodeid:
        return "forbidden_status_commit_fresh_no_residue"
    if "test_r1c05c01_allowed_routing_history_audit" in nodeid:
        return "allowed_routing_history_audit"
    if "test_r1c05c01_committed_exact_replay_read_only" in nodeid:
        return "committed_exact_replay_read_only"
    if "test_r1c05c01_legacy_forbidden_prior_committed_replay" in nodeid:
        return "legacy_forbidden_prior_committed_replay"
    return None


def compute_distribution(nodeids: list[str]) -> dict[str, int]:
    """Return a ``{test_prefix: count}`` mapping for the given node IDs."""
    dist: dict[str, int] = {k: 0 for k in DISTRIBUTION}
    for nid in nodeids:
        key = _classify_nodeid(nid)
        if key is not None:
            dist[key] = dist.get(key, 0) + 1
    return dist


def validate_collection(nodeids: list[str]) -> dict[str, Any]:
    """Validate a collected node-ID list against the expected 41/20/16/3/2 contract.

    Returns a structured dict with ``valid``, ``count``, ``distribution``,
    ``missing``, ``extra``, ``duplicates`` and ``unclassified`` fields.
    """
    expected_set = set(EXPECTED_NODEIDS)
    actual_set = set(nodeids)
    seen: set[str] = set()
    duplicates: list[str] = []
    for nid in nodeids:
        if nid in seen:
            duplicates.append(nid)
        seen.add(nid)

    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    unclassified = sorted(nid for nid in actual_set if _classify_nodeid(nid) is None)
    dist = compute_distribution(nodeids)

    valid = (
        len(nodeids) == EXPECTED_COUNT
        and not missing
        and not extra
        and not duplicates
        and not unclassified
        and dist == DISTRIBUTION
    )

    return {
        "valid": valid,
        "count": len(nodeids),
        "expected_count": EXPECTED_COUNT,
        "distribution": dist,
        "expected_distribution": DISTRIBUTION,
        "missing": missing,
        "extra": extra,
        "duplicates": duplicates,
        "unclassified": unclassified,
    }


# ---------------------------------------------------------------------------
# Pytest hook implementation
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Register the plugin only when an output path is requested."""
    output_path = os.environ.get("TG_R4_COLLECTION_JSON")
    if output_path:
        config._r4_collection_output = Path(output_path)  # type: ignore[attr-defined]


def pytest_collection_finish(session: pytest.Session) -> None:
    """Write the final collected node-ID list to JSON.

    Uses ``session.items`` — the authoritative post-resolution list — not
    terminal output.  The hook fires after parametrisation expansion, so every
    ``[param]`` variant appears as its own entry.
    """
    output_path: Path | None = getattr(session.config, "_r4_collection_output", None)
    if output_path is None:
        return

    nodeids = [item.nodeid for item in session.items]
    validation = validate_collection(nodeids)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "plugin": "wp04_02_r4_pytest_plugin",
                "count": len(nodeids),
                "nodeids": nodeids,
                "validation": validation,
            },
            indent=2,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
