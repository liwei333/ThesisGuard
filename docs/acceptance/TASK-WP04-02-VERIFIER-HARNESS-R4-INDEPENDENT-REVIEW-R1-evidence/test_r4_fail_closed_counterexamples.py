"""Independent, non-repairing counterexamples for the committed R4 harness."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


REVIEW_ROOT = Path("/private/tmp/tg-wp04-02-r4-review-r1.o31SWt/review")
VERIFY_DIR = REVIEW_ROOT / "tg_verifier_tools" / "verification"
sys.path.insert(0, str(VERIFY_DIR))

import wp04_02_r4_pytest_plugin as plugin  # noqa: E402
import wp04_02_r4_runner as runner  # noqa: E402


def _collection_payload(nodeids: list[str] | None = None) -> dict[str, object]:
    ids = list(plugin.EXPECTED_NODEIDS if nodeids is None else nodeids)
    return {
        "plugin": "independent-counterexample",
        "count": len(ids),
        "nodeids": ids,
        "validation": plugin.validate_collection(ids),
    }


def _fake_run(
    *,
    write: str = "valid",
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
):
    def fake(
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        bundle: runner.EvidenceBundle,
        step_name: str,
        timeout: int = 120,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, env, step_name, timeout
        output = bundle.root / "collected-nodeids.json"
        if write == "valid":
            output.write_text(json.dumps(_collection_payload()), encoding="utf-8")
        elif write == "malformed":
            output.write_text("{not-json", encoding="utf-8")
        elif write == "missing-one":
            output.write_text(
                json.dumps(_collection_payload(list(plugin.EXPECTED_NODEIDS[1:]))),
                encoding="utf-8",
            )
        return subprocess.CompletedProcess(argv, returncode, stdout, stderr)

    return fake


def _run(
    tmp_path: Path,
    *,
    name: str,
    candidate_mismatches: list[str] | None = None,
    main_mismatches: list[str] | None = None,
    write: str = "valid",
    returncode: int = 0,
    stdout: str = "",
    preexisting: bool = False,
) -> tuple[dict[str, object], Path]:
    evidence = tmp_path / name
    candidate = tmp_path / f"{name}-candidate-not-a-git-worktree"
    main = tmp_path / f"{name}-main"
    candidate.mkdir()
    main.mkdir()
    if preexisting:
        evidence.mkdir()
        (evidence / "result.json").write_text('{"verdict":"OLD_PASS"}', encoding="utf-8")
        (evidence / "sentinel.txt").write_text("pre-existing", encoding="utf-8")
    with (
        patch.object(
            runner,
            "verify_candidate_pins",
            return_value=[] if candidate_mismatches is None else candidate_mismatches,
        ),
        patch.object(
            runner,
            "verify_main_pins",
            return_value=[] if main_mismatches is None else main_mismatches,
        ),
        patch.object(runner, "_stage_plugin_to_temp", return_value=tmp_path / "stage"),
        patch.object(
            runner,
            "run_subprocess",
            side_effect=_fake_run(write=write, returncode=returncode, stdout=stdout),
        ),
    ):
        result = runner.run_collect_only(candidate, main, evidence)
    return result, evidence


def test_candidate_pin_mismatch_fails_closed(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, name="candidate-pin", candidate_mismatches=["changed"])
    assert result["valid"] is False


def test_main_pin_mismatch_fails_closed(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, name="main-pin", main_mismatches=["changed"])
    assert result["valid"] is False


def test_wrong_candidate_git_identity_fails_closed_even_when_pins_match(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, name="wrong-git-identity")
    assert result["valid"] is False


def test_nonzero_pytest_exit_cannot_pass_with_valid_json(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, name="nonzero-pytest", returncode=2)
    assert result["valid"] is False


def test_missing_collection_json_fails_closed(tmp_path: Path) -> None:
    result, _ = _run(tmp_path, name="missing-json", write="none")
    assert result["valid"] is False


def test_malformed_collection_json_returns_recorded_failure(tmp_path: Path) -> None:
    result, evidence = _run(tmp_path, name="malformed-json", write="malformed")
    assert result["valid"] is False
    assert (evidence / "result.json").exists()
    assert (evidence / "manifest.json").exists()


def test_stale_collection_json_cannot_rescue_current_failed_invocation(tmp_path: Path) -> None:
    evidence = tmp_path / "stale-json"
    evidence.mkdir()
    (evidence / "collected-nodeids.json").write_text(
        json.dumps(_collection_payload()), encoding="utf-8"
    )
    candidate = tmp_path / "stale-candidate"
    main = tmp_path / "stale-main"
    candidate.mkdir()
    main.mkdir()
    with (
        patch.object(runner, "verify_candidate_pins", return_value=[]),
        patch.object(runner, "verify_main_pins", return_value=[]),
        patch.object(runner, "_stage_plugin_to_temp", return_value=tmp_path / "stage"),
        patch.object(
            runner,
            "run_subprocess",
            side_effect=_fake_run(write="none", returncode=2),
        ),
    ):
        result = runner.run_collect_only(candidate, main, evidence)
    assert result["valid"] is False


def test_missing_extra_duplicate_and_wrong_distribution_fail_validation() -> None:
    missing = list(plugin.EXPECTED_NODEIDS[1:])
    extra = list(plugin.EXPECTED_NODEIDS) + ["tests/x.py::test_unclassified[x]"]
    duplicate = list(plugin.EXPECTED_NODEIDS) + [plugin.EXPECTED_NODEIDS[0]]
    wrong_dist = list(plugin.EXPECTED_NODEIDS)
    wrong_dist[0] = (
        "tests/test_evidence_services.py::"
        "test_r1c05c01_allowed_routing_history_audit[fabricated]"
    )
    for nodeids in (missing, extra, duplicate, wrong_dist):
        assert plugin.validate_collection(nodeids)["valid"] is False


def test_preexisting_evidence_directory_is_rejected_without_overwrite(tmp_path: Path) -> None:
    result, evidence = _run(tmp_path, name="preexisting", preexisting=True)
    assert result["valid"] is False
    assert json.loads((evidence / "result.json").read_text(encoding="utf-8")) == {
        "verdict": "OLD_PASS"
    }


def test_manifest_covers_every_retained_nonmanifest_artifact(tmp_path: Path) -> None:
    result, evidence = _run(tmp_path, name="manifest-coverage")
    assert result["valid"] is True
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    retained = {path.name for path in evidence.iterdir() if path.name != "manifest.json"}
    assert set(manifest["artifacts"]) == retained


def test_sensitive_stdout_is_redacted_before_retention(tmp_path: Path) -> None:
    secret = "representative-secret-value"
    evidence = tmp_path / "stdout-secret"
    bundle = runner.EvidenceBundle(evidence)
    completed = subprocess.CompletedProcess(["fake"], 0, secret, secret)
    with patch.object(runner.subprocess, "run", return_value=completed):
        runner.run_subprocess(
            ["fake"],
            cwd=tmp_path,
            env={"TG_TEST_ADMIN_DATABASE_URL": secret},
            bundle=bundle,
            step_name="collect-only",
        )
    assert secret not in (evidence / "collect-only.stdout.txt").read_text(encoding="utf-8")
    assert secret not in (evidence / "collect-only.stderr.txt").read_text(encoding="utf-8")


def test_representative_sensitive_env_key_variants_are_redacted() -> None:
    secret = "representative-secret-value"
    redacted = runner.redact_env(
        {
            "database_url": secret,
            "SERVICE_PASSWORD": secret,
            "MY_ACCESS_TOKEN": secret,
            "TG_TEST_ADMIN_DATABASE_URL_BACKUP": secret,
        }
    )
    assert secret not in redacted.values()
