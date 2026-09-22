"""Self-tests for the WP-04-02 R4/R5 verifier harness tool.

Covers:

* validate_collection: correct 41, missing, extra, duplicates, wrong distribution
* _classify_nodeid: known prefixes and unknown input
* compute_distribution: correct totals
* EvidenceBundle: write, manifest, SHA256 consistency, recursive coverage
* redact_env: sensitive key redaction (case/prefix/suffix variants, URLs)
* sha256_file / sha256_text: deterministic hashing
* run_collect_only: end-to-end collect-only against the candidate worktree
* R5 fail-closed regression: F-01 main pin mismatch, F-02 Git identity,
  F-03 pytest non-zero / stale nonce, F-04 pre-existing evidence,
  F-06 value redaction, F-07 malformed JSON, F-09 self-test non-zero
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

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
    _is_sensitive_env_key,
    _redact_url_value,
    _redact_value,
    redact_env,
    sha256_file,
    sha256_text,
)

# ===================================================================
# Shared helpers for R5 negative-path tests
# ===================================================================


def _fake_collection_payload(nodeids: list[str] | None = None) -> dict[str, object]:
    ids = list(EXPECTED_NODEIDS if nodeids is None else nodeids)
    return {
        "plugin": "test-counterexample",
        "count": len(ids),
        "nodeids": ids,
        "validation": validate_collection(ids),
        "test_body_calls": 0,
    }


def _make_fake_run(
    *,
    write: str = "valid",
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> object:
    """Build a fake ``run_subprocess`` that writes collection JSON.

    ``write`` modes:
        "valid"        - correct payload with env nonce
        "malformed"    - broken JSON
        "wrong-nonce"  - valid JSON but stale nonce
        "none"         - do not write any file
        "missing-one"  - valid JSON missing one node
    """

    def fake(
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        bundle: object,
        step_name: str,
        timeout: int = 120,
    ) -> subprocess.CompletedProcess[str]:
        del argv, cwd, step_name, timeout
        output = bundle.root / "_collected-nodeids.json"
        if write == "valid":
            data = _fake_collection_payload()
            data["nonce"] = env.get("TG_R4_INVOCATION_NONCE", "")
            output.write_text(json.dumps(data), encoding="utf-8")
        elif write == "malformed":
            output.write_text("{not-json", encoding="utf-8")
        elif write == "wrong-nonce":
            data = _fake_collection_payload()
            data["nonce"] = "stale-nonce-value"
            output.write_text(json.dumps(data), encoding="utf-8")
        elif write == "missing-one":
            data = _fake_collection_payload(list(EXPECTED_NODEIDS[1:]))
            data["nonce"] = env.get("TG_R4_INVOCATION_NONCE", "")
            output.write_text(json.dumps(data), encoding="utf-8")
        elif write == "body-called":
            data = _fake_collection_payload()
            data["nonce"] = env.get("TG_R4_INVOCATION_NONCE", "")
            data["test_body_calls"] = 1
            output.write_text(json.dumps(data), encoding="utf-8")
        # "none" -> write nothing
        return subprocess.CompletedProcess(["fake"], returncode, stdout, stderr)

    return fake


def _run_collect_only_with_mocks(
    tmp_path: Path,
    *,
    name: str,
    main_git_mismatches: list[str] | None = None,
    candidate_git_mismatches: list[str] | None = None,
    candidate_pin_mismatches: list[str] | None = None,
    main_pin_mismatches: list[str] | None = None,
    write: str = "valid",
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
    preexisting: bool = False,
    preexisting_empty: bool = False,
) -> tuple[dict[str, object], Path]:
    """Run ``run_collect_only`` with patched Git/pin verification and subprocess.

    Returns ``(result, evidence_dir)``.
    """
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    evidence = tmp_path / name
    candidate = tmp_path / f"{name}-candidate"
    main = tmp_path / f"{name}-main"
    candidate.mkdir()
    main.mkdir()
    if preexisting:
        evidence.mkdir()
        (evidence / "result.json").write_text('{"verdict":"OLD_PASS"}', encoding="utf-8")
        (evidence / "sentinel.txt").write_text("pre-existing", encoding="utf-8")
    elif preexisting_empty:
        evidence.mkdir()

    with (
        patch.object(
            runner,
            "verify_main_git_identity",
            return_value=main_git_mismatches or [],
        ),
        patch.object(
            runner,
            "verify_candidate_git_identity",
            return_value=candidate_git_mismatches or [],
        ),
        patch.object(
            runner,
            "verify_candidate_pins",
            return_value=candidate_pin_mismatches or [],
        ),
        patch.object(
            runner,
            "verify_main_pins",
            return_value=main_pin_mismatches or [],
        ),
        patch.object(
            runner,
            "run_subprocess",
            side_effect=_make_fake_run(
                write=write, returncode=returncode, stdout=stdout, stderr=stderr
            ),
        ),
    ):
        result = runner.run_collect_only(candidate, main, evidence)
    return result, evidence


# ===================================================================
# validate_collection (existing R4 tests, preserved)
# ===================================================================


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
    modified = list(EXPECTED_NODEIDS)
    for i, nid in enumerate(modified):
        if "forbidden_status_commit_fresh_no_residue" in nid:
            modified[i] = (
                "tests/test_evidence_services.py::"
                "test_r1c05c01_allowed_routing_history_audit"
                "[omitted-VERIFIED-same-DUPE]"
            )
            break
    result = validate_collection(modified)
    assert result["count"] == 41
    assert result["distribution"] != DISTRIBUTION
    assert result["valid"] is False


def test_validate_collection_empty() -> None:
    """Empty collection must be invalid with all 41 missing."""
    result = validate_collection([])
    assert result["valid"] is False
    assert result["count"] == 0
    assert len(result["missing"]) == EXPECTED_COUNT


# ===================================================================
# _classify_nodeid (existing R4 tests, preserved)
# ===================================================================


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


# ===================================================================
# compute_distribution (existing R4 tests, preserved)
# ===================================================================


def test_compute_distribution_correct() -> None:
    dist = compute_distribution(list(EXPECTED_NODEIDS))
    assert dist == DISTRIBUTION
    assert sum(dist.values()) == EXPECTED_COUNT


def test_compute_distribution_empty() -> None:
    dist = compute_distribution([])
    assert dist == dict.fromkeys(DISTRIBUTION, 0)


# ===================================================================
# Hash helpers (existing R4 tests, preserved)
# ===================================================================


def test_sha256_text_deterministic() -> None:
    assert sha256_text("hello") == sha256_text("hello")
    assert sha256_text("hello") != sha256_text("world")


def test_sha256_file_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "sample.txt"
    p.write_text("content", encoding="utf-8")
    assert sha256_file(p) == sha256_file(p)
    assert sha256_file(p) == sha256_text("content")


# ===================================================================
# redact_env (existing R4 tests preserved + new R5 coverage)
# ===================================================================


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


# --- R5 F-06: case-insensitive and prefix/suffix variant redaction ---


@pytest.mark.parametrize(
    "key",
    [
        "database_url",
        "DATABASE_URL",
        "Database_Url",
        "MY_DATABASE_URL",
        "database_url_backup",
        "SERVICE_PASSWORD",
        "service_password",
        "MY_ACCESS_TOKEN",
        "auth_token",
        "X_Secret",
        "api_key",
        "API_KEY",
        "my_credentials",
        "session_id",
        "data_dsn",
        "CODEX_SESSION_ID",
        "ANTHROPIC_AUTH_TOKEN",
    ],
)
def test_redact_env_case_and_variant_keys(key: str) -> None:
    """Sensitive keys must be redacted regardless of case or prefix/suffix."""
    env = {key: "sensitive-value-123"}
    redacted = redact_env(env)
    assert redacted[key] == "<REDACTED>", f"key {key!r} not redacted"


def test_redact_env_url_userinfo() -> None:
    """URL userinfo must be redacted."""
    result = _redact_url_value("postgresql://user:pass@host:5432/db")
    assert "user" not in result
    assert "pass" not in result
    assert "<REDACTED>@host:5432/db" in result


def test_redact_env_url_query_params() -> None:
    """Credential-bearing URL query parameters must be redacted."""
    result = _redact_url_value("https://example.com/path?api_key=secret123&page=1")
    assert "secret123" not in result
    assert "api_key=<REDACTED>" in result
    assert "page=1" in result


def test_redact_value_literals() -> None:
    """Known sensitive literals must be redacted from arbitrary text."""
    secret = "super-secret-token"
    text = f"error occurred: {secret} was exposed"
    result = _redact_value(text, frozenset({secret}))
    assert secret not in result
    assert "<REDACTED>" in result


def test_embedded_credential_urls_are_redacted_everywhere() -> None:
    """B-04: URLs embedded in surrounding text must not leak credentials."""
    secret_url = (
        "postgresql://synthetic-user:synthetic-pass@127.0.0.1:1/db"
        "?api_key=synthetic-query-secret&application_name=takeover"
    )
    result = _redact_value(f"prefix {secret_url} suffix", frozenset())
    for secret in ("synthetic-user", "synthetic-pass", "synthetic-query-secret"):
        assert secret not in result
    assert result.startswith("prefix ")
    assert result.endswith(" suffix")


def test_recursive_metadata_redaction_covers_argv_cwd_and_errors() -> None:
    """B-04: nested strings must be sanitized before JSON serialization."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret_url = "postgresql://recursive-user:recursive-pass@127.0.0.1:1/db"
    raw = {
        "argv": ["tool", f"--dsn={secret_url}"],
        "cwd": f"/tmp/context/{secret_url}",
        "nested": {"error": f"failed while opening {secret_url}"},
    }
    sanitized = runner._redact_metadata(raw, frozenset())
    serialized = json.dumps(sanitized)
    assert "recursive-user" not in serialized
    assert "recursive-pass" not in serialized


def test_minimal_env_uses_verifier_owned_guards_without_inherited_credentials(
    tmp_path: Path,
) -> None:
    """R2: child guards are verifier-owned, not inherited credential values."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    staged = runner._stage_plugin_to_temp()
    ledger = tmp_path / "fresh-ledger.jsonl"
    guard_path = tmp_path / "guards"
    guard_path.mkdir()
    inherited_url = "postgresql+asyncpg://inherited:secret@127.0.0.1:9999/private"
    try:
        with patch.dict(
            runner.os.environ,
            {
                "TG_TEST_ADMIN_DATABASE_URL": inherited_url,
                "TG_EVIDENCE_PG_LEDGER": "/tmp/inherited-ledger.jsonl",
                "UNRELATED_PASSWORD_BACKUP": "must-never-be-read-or-propagated",
            },
            clear=False,
        ):
            env = runner._build_minimal_env(
                tmp_path / "collection.json",
                staged,
                ledger,
                guard_path,
            )
        assert env["TG_TEST_ADMIN_DATABASE_URL"] == runner.SYNTHETIC_DB_GUARD_URL
        assert env["TG_TEST_ADMIN_DATABASE_URL"] != inherited_url
        assert env["TG_EVIDENCE_PG_LEDGER"] == str(ledger)
        assert "UNRELATED_PASSWORD_BACKUP" not in env
        assert "/tmp/inherited-ledger.jsonl" not in env.values()
        assert env["PYTHONPATH"].split(":") == [str(staged.root), str(guard_path)]
        assert redact_env(env)["TG_TEST_ADMIN_DATABASE_URL"] == "<REDACTED>"
    finally:
        shutil.rmtree(staged.root, ignore_errors=True)


def test_early_baseline_failure_never_inspects_unrelated_inherited_secret(
    tmp_path: Path,
) -> None:
    """R2: early closure must not enumerate or inspect the inherited environment."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret_key = "R2_UNRELATED_PASSWORD_BACKUP"
    secret_value = "r2-unrelated-sensitive-value-must-remain-unread"

    class GuardedEnvironment:
        def __init__(self) -> None:
            self.accessed: list[str] = []
            self.safe = {
                "PATH": "/usr/bin:/bin",
                "HOME": str(tmp_path),
                "USER": "verifier",
                "LANG": "C.UTF-8",
                secret_key: secret_value,
            }

        def get(self, key: str, default: str | None = None) -> str | None:
            self.accessed.append(key)
            if key == secret_key:
                raise AssertionError("unrelated inherited secret was read")
            return self.safe.get(key, default)

        def __getitem__(self, key: str) -> str:
            self.accessed.append(key)
            if key == secret_key:
                raise AssertionError("unrelated inherited secret was read")
            return self.safe[key]

        def __iter__(self) -> object:
            raise AssertionError("complete inherited environment was enumerated")

        def __len__(self) -> int:
            raise AssertionError("complete inherited environment was sized")

        def items(self) -> object:
            raise AssertionError("complete inherited environment items were read")

        def keys(self) -> object:
            raise AssertionError("complete inherited environment keys were read")

        def copy(self) -> object:
            raise AssertionError("complete inherited environment was copied")

    guarded_env = GuardedEnvironment()
    evidence = tmp_path / "early-baseline-evidence"
    with (
        patch.object(runner.os, "environ", guarded_env),
        patch.object(
            runner,
            "verify_main_git_identity",
            return_value=["forced early identity mismatch"],
        ),
    ):
        result = runner.run_collect_only(tmp_path / "candidate", tmp_path / "main", evidence)

    assert result["valid"] is False
    assert result["reason"] == "main_git_identity_mismatch"
    assert guarded_env.accessed == []
    retained = b"".join(path.read_bytes() for path in evidence.rglob("*") if path.is_file())
    assert secret_key.encode() not in retained
    assert secret_value.encode() not in retained


def test_is_sensitive_env_key_classification() -> None:
    assert _is_sensitive_env_key("DATABASE_URL") is True
    assert _is_sensitive_env_key("database_url") is True
    assert _is_sensitive_env_key("MY_ACCESS_TOKEN") is True
    assert _is_sensitive_env_key("SERVICE_PASSWORD") is True
    assert _is_sensitive_env_key("HOME") is False
    assert _is_sensitive_env_key("PATH") is False
    assert _is_sensitive_env_key("LANG") is False


# ===================================================================
# EvidenceBundle (existing R4 tests preserved + new R5 coverage)
# ===================================================================


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
    assert "manifest.json" not in manifest["artifacts"]


def test_evidence_bundle_manifest_covers_all_files(tmp_path: Path) -> None:
    """Manifest must cover every non-manifest file in the bundle root."""
    bundle = EvidenceBundle(tmp_path / "evidence")
    bundle.write_json("result.json", {"verdict": "PASS"})
    bundle.write_text("log.txt", "data")
    bundle.write_text("sub/deep.txt", "nested")
    manifest = bundle.manifest()
    artifact_names = set(manifest["artifacts"].keys())
    assert "result.json" in artifact_names
    assert "log.txt" in artifact_names
    # Recursive scan includes subdirectories
    assert any("deep.txt" in n for n in artifact_names)
    assert "manifest.json" not in artifact_names


def test_evidence_bundle_manifest_size_and_hash_correct(tmp_path: Path) -> None:
    """Manifest byte size and SHA256 must match actual file content."""
    bundle = EvidenceBundle(tmp_path / "evidence")
    bundle.write_text("check.txt", "exact-content")
    manifest = bundle.manifest()
    entry = manifest["artifacts"]["check.txt"]
    fp = bundle.root / "check.txt"
    assert entry["bytes"] == fp.stat().st_size
    assert entry["sha256"] == sha256_file(fp)


def test_outer_manifest_audit_includes_nested_manifests(tmp_path: Path) -> None:
    """R2: only the exact outer manifest is excluded from recursive coverage."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    bundle = EvidenceBundle(tmp_path / "outer")
    bundle.write_json("harness-run/manifest.json", {"inner": True})
    bundle.write_json("negative/staged-mismatch/manifest.json", {"inner": True})
    bundle.write_text("negative/staged-mismatch/result.json", "{}")
    bundle.write_json("manifest.json", bundle.manifest())

    manifest = json.loads((bundle.root / "manifest.json").read_text(encoding="utf-8"))
    audit = runner._audit_recursive_manifest(bundle.root, manifest)

    assert audit["inventory_equal"] is True
    assert audit["size_hash_equal"] is True
    assert audit["actual_retained_files"] == 3
    assert audit["manifest_entries"] == 3
    assert audit["missing"] == []
    assert audit["extra"] == []
    assert audit["size_hash_mismatches"] == []
    assert audit["nested_manifests"] == [
        "harness-run/manifest.json",
        "negative/staged-mismatch/manifest.json",
    ]


# ===================================================================
# R5 F-01: main pin mismatch must fail closed
# ===================================================================


def test_main_pin_mismatch_fails_closed(tmp_path: Path) -> None:
    """F-01: main pin mismatch must produce non-success before pytest."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f01-main-pin",
        main_pin_mismatches=["docs/changed.md: hash mismatch"],
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"


def test_main_git_identity_mismatch_fails_closed(tmp_path: Path) -> None:
    """F-02: wrong main HEAD must produce non-success."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f02-main-git",
        main_git_mismatches=["main HEAD: expected abc... got def..."],
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"


# ===================================================================
# R5 F-02: candidate Git identity verification
# ===================================================================


@pytest.mark.parametrize(
    ("git_mismatches", "label"),
    [
        (["candidate branch: expected X got Y"], "wrong-branch"),
        (["candidate HEAD: expected abc... got def..."], "wrong-head"),
        (["candidate parent: expected abc... got def..."], "wrong-parent"),
        (["candidate worktree is not clean"], "dirty"),
        (["candidate is not a git repository"], "not-git"),
    ],
)
def test_candidate_git_identity_failures(
    tmp_path: Path, git_mismatches: list[str], label: str
) -> None:
    """F-02: wrong candidate branch/HEAD/parent/dirty/not-git must fail."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name=f"f02-candidate-{label}",
        candidate_git_mismatches=git_mismatches,
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"


def test_wrong_candidate_git_identity_even_when_pins_match(tmp_path: Path) -> None:
    """F-02: file pins matching alone must not permit execution."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f02-git-vs-pins",
        candidate_git_mismatches=["candidate is not a git repository"],
    )
    assert result["valid"] is False


# ===================================================================
# R5 F-03: pytest non-zero / stale nonce
# ===================================================================


def test_nonzero_pytest_exit_cannot_pass(tmp_path: Path) -> None:
    """F-03: pytest non-zero must produce non-success even with valid JSON."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f03-nonzero",
        returncode=2,
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"
    assert result.get("reason") == "pytest_nonzero"


def test_stale_nonce_cannot_rescue_failed_invocation(tmp_path: Path) -> None:
    """F-03: collection JSON with wrong nonce must not produce PASS."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f03-stale-nonce",
        write="wrong-nonce",
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"
    assert result.get("reason") == "invocation_nonce_mismatch"


def test_missing_collection_json_fails_closed(tmp_path: Path) -> None:
    """F-03: missing collection JSON must fail closed with evidence."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="f03-missing-json",
        write="none",
    )
    assert result["valid"] is False
    assert (evidence / "result.json").exists()


# ===================================================================
# R5 F-04: pre-existing evidence rejection
# ===================================================================


def test_preexisting_nonempty_evidence_rejected(tmp_path: Path) -> None:
    """F-04: non-empty pre-existing evidence must be rejected, not overwritten."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="f04-preexisting",
        preexisting=True,
    )
    assert result["valid"] is False
    assert result["reason"] == "evidence_path_exists"
    # Original bytes must be preserved exactly.
    assert json.loads((evidence / "result.json").read_text(encoding="utf-8")) == {
        "verdict": "OLD_PASS"
    }
    assert (evidence / "sentinel.txt").read_text(encoding="utf-8") == "pre-existing"


def test_preexisting_empty_evidence_rejected(tmp_path: Path) -> None:
    """F-04: even an empty pre-existing evidence directory must be rejected."""
    result, _ = _run_collect_only_with_mocks(
        tmp_path,
        name="f04-empty",
        preexisting_empty=True,
    )
    assert result["valid"] is False
    assert result["reason"] == "evidence_path_exists"


# ===================================================================
# R5 F-06: stdout/stderr/exception value redaction
# ===================================================================


def test_sensitive_stdout_stderr_redacted(tmp_path: Path) -> None:
    """F-06: sensitive values must be redacted in stdout/stderr evidence."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret = "representative-secret-value"
    evidence = tmp_path / "f06-stdout"
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


def test_sensitive_exception_message_redacted(tmp_path: Path) -> None:
    """F-06: sensitive values in exception text must be redacted."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret = "another-secret-value"
    evidence = tmp_path / "f06-exception"
    bundle = runner.EvidenceBundle(evidence)

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="x", timeout=1, output=secret)

    with patch.object(runner.subprocess, "run", side_effect=raise_timeout):
        runner.run_subprocess(
            ["fake"],
            cwd=tmp_path,
            env={"MY_ACCESS_TOKEN": secret},
            bundle=bundle,
            step_name="collect-only",
        )
    stderr_text = (evidence / "collect-only.stderr.txt").read_text(encoding="utf-8")
    assert secret not in stderr_text


def test_embedded_url_redacted_in_subprocess_outputs_and_metadata(tmp_path: Path) -> None:
    """R-04: persisted stdout/stderr/argv/cwd must recursively redact URLs."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret_url = "postgresql://output-user:output-pass@127.0.0.1:1/db?token=query-secret"
    evidence = tmp_path / "embedded-output"
    bundle = runner.EvidenceBundle(evidence)
    completed = subprocess.CompletedProcess(
        ["fake"], 0, f"stdout {secret_url}", f"stderr {secret_url}"
    )
    with patch.object(runner.subprocess, "run", return_value=completed):
        runner.run_subprocess(
            ["fake", f"--url={secret_url}"],
            cwd=Path(f"/tmp/context/{secret_url}"),
            env={"PATH": "/usr/bin"},
            bundle=bundle,
            step_name="collect-only",
        )
    retained = "\n".join(path.read_text() for path in evidence.iterdir())
    for secret in ("output-user", "output-pass", "query-secret"):
        assert secret not in retained


def test_embedded_url_redacted_in_startup_exception(tmp_path: Path) -> None:
    """R-04: startup exception text with an embedded URL must be sanitized."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret_url = "postgresql://error-user:error-pass@127.0.0.1:1/db"
    evidence = tmp_path / "embedded-error"
    bundle = runner.EvidenceBundle(evidence)
    with patch.object(runner.subprocess, "run", side_effect=OSError(f"cannot open {secret_url}")):
        result = runner.run_subprocess(
            ["fake"],
            cwd=tmp_path,
            env={"PATH": "/usr/bin"},
            bundle=bundle,
            step_name="collect-only",
        )
    assert result.returncode != 0
    retained = "\n".join(path.read_text() for path in evidence.iterdir())
    assert "error-user" not in retained
    assert "error-pass" not in retained


# ===================================================================
# R5 F-07: malformed JSON produces structured closed failure
# ===================================================================


def test_malformed_collection_json_fails_closed(tmp_path: Path) -> None:
    """F-07: malformed JSON must produce structured failure evidence."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="f07-malformed",
        write="malformed",
    )
    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"
    assert (evidence / "result.json").exists()
    assert (evidence / "manifest.json").exists()


# ===================================================================
# R5 F-09: self-test mode non-zero on missing file / subprocess failure
# ===================================================================


def test_selftest_missing_file_returns_nonzero(tmp_path: Path) -> None:
    """F-09: --mode self-test must return non-zero when test file is absent."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    # Create a fake args namespace pointing to a non-existent test file.
    class FakeArgs:
        mode = "self-test"
        candidate_root = tmp_path / "c"
        main_root = tmp_path / "m"
        pytest = "pytest"

    tmp_path.joinpath("c").mkdir()
    tmp_path.joinpath("m").mkdir()
    with patch.object(runner, "_HERE", tmp_path / "nonexistent"):
        rc = runner._run_self_tests(FakeArgs())
    assert rc != 0


def test_selftest_missing_executable_returns_nonzero(tmp_path: Path) -> None:
    """R-05: self-test subprocess startup failure must return non-zero."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    class FakeArgs:
        main_root = tmp_path
        pytest = "/definitely/missing/pytest"

    with patch.object(runner.subprocess, "run", side_effect=FileNotFoundError("missing")):
        rc = runner._run_self_tests(FakeArgs())
    assert rc != 0


def test_selftest_nonzero_subprocess_is_preserved(tmp_path: Path) -> None:
    """R-05: self-test must preserve a pytest non-zero return code."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    class FakeArgs:
        main_root = tmp_path
        pytest = "pytest"

    completed = subprocess.CompletedProcess(["pytest"], 7, "", "synthetic failure")
    with patch.object(runner.subprocess, "run", return_value=completed):
        assert runner._run_self_tests(FakeArgs()) == 7


# ===================================================================
# Manifest completeness (R5 TOP-AC-04)
# ===================================================================


def test_manifest_covers_every_retained_nonmanifest_artifact(
    tmp_path: Path,
) -> None:
    """Manifest must cover every retained file except itself."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="manifest-coverage",
    )
    assert result["valid"] is True
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    retained = {path.name for path in evidence.iterdir() if path.name != "manifest.json"}
    assert set(manifest["artifacts"]) == retained


def test_manifest_includes_collected_nodeids(tmp_path: Path) -> None:
    """collected-nodeids.json must appear in the manifest."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="manifest-nodeids",
    )
    assert result["valid"] is True
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    assert "collected-nodeids.json" in manifest["artifacts"]


# ===================================================================
# Plugin collision resistance and staging cleanup
# ===================================================================


def test_plugin_staging_cleanup_on_success(tmp_path: Path) -> None:
    """Temporary plugin staging dir must be cleaned up after success."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    staged = runner._stage_plugin_to_temp()
    stage_path = staged.root

    with (
        patch.object(runner, "verify_main_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_pins", return_value=[]),
        patch.object(runner, "verify_main_pins", return_value=[]),
        patch.object(runner, "_stage_plugin_to_temp", return_value=staged),
        patch.object(
            runner,
            "run_subprocess",
            side_effect=_make_fake_run(write="valid"),
        ),
    ):
        candidate = tmp_path / "candidate"
        main = tmp_path / "main"
        candidate.mkdir()
        main.mkdir()
        evidence = tmp_path / "evidence"
        runner.run_collect_only(candidate, main, evidence)
    # The staging dir must be removed (or at least not cause failure).
    assert not stage_path.exists()


def test_plugin_staging_is_unique_isolated_and_byte_authenticated() -> None:
    """B-03: stage only the exact plugin under a private unique namespace."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    staged = runner._stage_plugin_to_temp()
    try:
        assert not staged.module_name.startswith("tg_verifier_tools")
        assert (
            staged.plugin_path.read_bytes()
            == Path(runner.__file__).with_name("wp04_02_r4_pytest_plugin.py").read_bytes()
        )
        assert runner._verify_staged_plugin(staged) is True
        staged.plugin_path.write_text("# tampered\n", encoding="utf-8")
        assert runner._verify_staged_plugin(staged) is False
    finally:
        shutil.rmtree(staged.root, ignore_errors=True)


def test_staged_plugin_namespace_resists_ambient_package_collision(tmp_path: Path) -> None:
    """B-03: an ambient public-package plugin cannot win module resolution."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    ambient = tmp_path / "ambient" / "tg_verifier_tools" / "verification"
    ambient.mkdir(parents=True)
    (ambient / "wp04_02_r4_pytest_plugin.py").write_text(
        "raise RuntimeError('ambient collision selected')\n", encoding="utf-8"
    )
    staged = runner._stage_plugin_to_temp()
    try:
        assert "tg_verifier_tools" not in staged.module_name
        assert str(staged.root) != str(ambient.parents[1])
        assert runner._verify_staged_plugin(staged) is True
        probe = subprocess.run(
            [
                sys.executable,
                "-c",
                f"import {staged.module_name} as p; print(p.__file__)",
            ],
            env={
                "PATH": "/usr/bin:/bin",
                "PYTHONPATH": f"{staged.root}:{tmp_path / 'ambient'}",
            },
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert probe.returncode == 0, probe.stderr
        assert Path(probe.stdout.strip()).resolve() == staged.plugin_path.resolve()
    finally:
        shutil.rmtree(staged.root, ignore_errors=True)


def test_staged_plugin_mismatch_blocks_before_pytest(tmp_path: Path) -> None:
    """R-03: tampered staged bytes must fail closed before subprocess start."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    staged = runner._stage_plugin_to_temp()
    staged.plugin_path.write_text("# synthetic tamper\n", encoding="utf-8")
    candidate = tmp_path / "candidate"
    main = tmp_path / "main"
    evidence = tmp_path / "staged-mismatch"
    candidate.mkdir()
    main.mkdir()
    with (
        patch.object(runner, "verify_main_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_pins", return_value=[]),
        patch.object(runner, "verify_main_pins", return_value=[]),
        patch.object(runner, "_stage_plugin_to_temp", return_value=staged),
        patch.object(runner, "run_subprocess") as subprocess_mock,
    ):
        result = runner.run_collect_only(candidate, main, evidence)
    assert result["valid"] is False
    assert result["reason"] == "staged_plugin_mismatch"
    subprocess_mock.assert_not_called()
    assert (evidence / "manifest.json").exists()
    assert not staged.root.exists()


def test_plugin_staging_cleanup_on_ordinary_failure(tmp_path: Path) -> None:
    """R-03: staging must be removed when pytest returns non-zero."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    staged = runner._stage_plugin_to_temp()
    candidate = tmp_path / "candidate"
    main = tmp_path / "main"
    evidence = tmp_path / "ordinary-failure"
    candidate.mkdir()
    main.mkdir()
    with (
        patch.object(runner, "verify_main_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_pins", return_value=[]),
        patch.object(runner, "verify_main_pins", return_value=[]),
        patch.object(runner, "_stage_plugin_to_temp", return_value=staged),
        patch.object(runner, "run_subprocess", side_effect=_make_fake_run(returncode=2)),
    ):
        result = runner.run_collect_only(candidate, main, evidence)
    assert result["valid"] is False
    assert result["reason"] == "pytest_nonzero"
    assert not staged.root.exists()


# ===================================================================
# Timeout/interruption closed evidence
# ===================================================================


def test_timeout_produces_closed_evidence(tmp_path: Path) -> None:
    """Subprocess timeout must produce redacted, structured failure evidence."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    secret = "timeout-secret"
    evidence = tmp_path / "timeout-evidence"
    bundle = runner.EvidenceBundle(evidence)

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    with patch.object(runner.subprocess, "run", side_effect=raise_timeout):
        result = runner.run_subprocess(
            ["fake"],
            cwd=tmp_path,
            env={"MY_ACCESS_TOKEN": secret},
            bundle=bundle,
            step_name="collect-only",
        )
    assert result.returncode == 124
    stderr_text = (evidence / "collect-only.stderr.txt").read_text(encoding="utf-8")
    assert "TIMEOUT" in stderr_text
    assert secret not in stderr_text


def test_keyboard_interrupt_closes_owned_bundle_and_cleans_staging(tmp_path: Path) -> None:
    """B-02: a controlled interruption must yield a closed non-success bundle."""
    import tg_verifier_tools.verification.wp04_02_r4_runner as runner

    candidate = tmp_path / "candidate"
    main = tmp_path / "main"
    evidence = tmp_path / "interrupted-evidence"
    staged = runner._stage_plugin_to_temp()
    stage_path = staged.root
    candidate.mkdir()
    main.mkdir()

    with (
        patch.object(runner, "verify_main_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_git_identity", return_value=[]),
        patch.object(runner, "verify_candidate_pins", return_value=[]),
        patch.object(runner, "verify_main_pins", return_value=[]),
        patch.object(runner, "_stage_plugin_to_temp", return_value=staged),
        patch.object(runner, "run_subprocess", side_effect=KeyboardInterrupt),
    ):
        result = runner.run_collect_only(candidate, main, evidence)

    assert result["valid"] is False
    assert result["verdict"] == "BLOCKED"
    assert result["reason"] == "interrupted"
    assert json.loads((evidence / "result.json").read_text())["verdict"] == "BLOCKED"
    assert (evidence / "manifest.json").exists()
    assert not stage_path.exists()


# ===================================================================
# Exact 41/20/16/3/2 happy path with mocks
# ===================================================================


def test_happy_path_41_distribution(tmp_path: Path) -> None:
    """Mocked happy path must yield valid=True with exact 41/20/16/3/2."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="happy-path",
    )
    assert result["valid"] is True
    assert result["count"] == 41
    assert result["distribution"] == DISTRIBUTION
    assert (evidence / "result.json").exists()
    assert (evidence / "collected-nodeids.json").exists()
    assert (evidence / "manifest.json").exists()


def test_any_test_body_execution_fails_closed(tmp_path: Path) -> None:
    """R-05: collect-only must reject evidence indicating a body call."""
    result, evidence = _run_collect_only_with_mocks(
        tmp_path,
        name="body-called",
        write="body-called",
    )
    assert result["valid"] is False
    assert result["reason"] == "test_body_execution_detected"
    assert (evidence / "manifest.json").exists()


# ===================================================================
# Missing/extra/duplicate/unclassified at count 41
# ===================================================================


def test_missing_extra_duplicate_wrong_distribution_fail() -> None:
    """R5 TOP-AC-03: collection anomalies at count 41 must fail validation."""
    missing = list(EXPECTED_NODEIDS[1:])
    extra = list(EXPECTED_NODEIDS) + ["tests/x.py::test_unclassified[x]"]
    duplicate = list(EXPECTED_NODEIDS) + [EXPECTED_NODEIDS[0]]
    wrong_dist = list(EXPECTED_NODEIDS)
    wrong_dist[0] = (
        "tests/test_evidence_services.py::test_r1c05c01_allowed_routing_history_audit[fabricated]"
    )
    for nodeids in (missing, extra, duplicate, wrong_dist):
        assert validate_collection(nodeids)["valid"] is False


# ===================================================================
# End-to-end: collect-only against the real candidate worktree
# ===================================================================


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

    # Verify manifest covers collected-nodeids.json (F-05 fix).
    assert "collected-nodeids.json" in manifest["artifacts"]

    # Verify result.json has invocation_nonce (F-03 fix).
    result_data = json.loads((evidence_dir / "result.json").read_text())
    assert "invocation_nonce" in result_data

    # Final source attribution must bind live, staged and retained bytes.
    source_hashes = json.loads((evidence_dir / "source-hashes.json").read_text())
    assert source_hashes["runner"]["equal"] is True
    assert source_hashes["plugin"]["equal_live_staged_retained"] is True
