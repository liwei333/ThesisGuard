"""Deterministic security tests for the WP-04-02 PostgreSQL proof protocol.

These tests never connect to PostgreSQL.  All child results and failure modes
are synthetic, and credential-shaped canaries are assembled only in memory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import NoReturn

import pytest
from tg_verifier_tools.verification.wp04_02_secure_pg_proof import (
    CHILD_EXIT_STAGES,
    MAX_STDOUT_BYTES,
    ConnectionFailure,
    EvidencePublisher,
    InterruptedChild,
    ResultSchemaFailure,
    SelectFailure,
    TimedOutChild,
    audit_json_documents,
    audit_manifest,
    build_child_argv,
    build_manifest,
    child_main,
    credential_scan_bytes,
    fixed_child_environment,
    make_failure_bundle,
    run_parent,
    validate_success_stdout,
)

INVOCATION_ID = "a" * 64


def _success_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 1,
        "invocation_id": INVOCATION_ID,
        "outcome": "SUCCESS",
        "child_return_code": 0,
        "stage": "SUCCESS",
        "connection_count": 1,
        "query_count": 1,
        "schema_valid_result_count": 1,
        "current_database": "postgres",
        "current_user": "postgres",
        "postgres_server_major": 17,
    }
    payload.update(overrides)
    return payload


def _stdout(**overrides: object) -> bytes:
    return json.dumps(_success_payload(**overrides), separators=(",", ":")).encode()


def _synthetic_url() -> str:
    return "postgresql" + "://" + "canary-user" + ":" + "canary-pass" + "@db.invalid/x"


def _launcher(returncode: int, stdout: bytes = b"", *, calls: list[int] | None = None):
    def launch(**_: object) -> tuple[int, bytes]:
        if calls is not None:
            calls.append(1)
        return returncode, stdout

    return launch


def test_parent_accepts_single_schema_valid_success_document() -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(0, _stdout()))
    assert result == {
        **_success_payload(),
        "parent_return_code": 0,
    }


@pytest.mark.parametrize(
    ("returncode", "stage"),
    sorted((code, stage) for code, stage in CHILD_EXIT_STAGES.items() if code not in {0, 124, 130}),
)
def test_parent_preserves_known_nonzero_child_codes(returncode: int, stage: str) -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(returncode))
    assert result["child_return_code"] == returncode
    assert result["stage"] == stage
    assert result["outcome"] == "FAILURE"
    assert result["parent_return_code"] == 1


def test_parent_classifies_timeout_without_retry() -> None:
    calls: list[int] = []

    def launch(**_: object) -> NoReturn:
        calls.append(1)
        raise TimedOutChild

    result = run_parent(INVOCATION_ID, launcher=launch)
    assert calls == [1]
    assert result["child_return_code"] == 124
    assert result["stage"] == "TIMEOUT"


def test_parent_classifies_interruption_without_retry() -> None:
    calls: list[int] = []

    def launch(**_: object) -> NoReturn:
        calls.append(1)
        raise InterruptedChild

    result = run_parent(INVOCATION_ID, launcher=launch)
    assert calls == [1]
    assert result["child_return_code"] == 130
    assert result["stage"] == "INTERRUPTED"


def test_parent_preserves_unknown_child_return_code() -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(91))
    assert result["child_return_code"] == 91
    assert result["stage"] == "UNKNOWN_CHILD_RETURN_CODE"


@pytest.mark.parametrize(
    "stdout",
    [
        b"{not-json",
        _stdout() + b"\n" + _stdout(),
        _stdout() + b" trailing",
        b"",
        b" \n\t",
        b"x" * (MAX_STDOUT_BYTES + 1),
    ],
    ids=["malformed", "multiple", "trailing", "empty", "whitespace", "oversized"],
)
def test_parent_rejects_invalid_success_transport(stdout: bytes) -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(0, stdout))
    assert result["child_return_code"] == 0
    assert result["stage"] == "CHILD_PROTOCOL_OR_SERIALIZATION_FAILURE"
    assert "stdout" not in result


@pytest.mark.parametrize(
    "overrides",
    [
        {"invocation_id": "b" * 64},
        {"stage": "SQL_CONNECTION_FAILURE"},
        {"child_return_code": 43},
        {"connection_count": 0},
        {"query_count": 0},
        {"schema_valid_result_count": 0},
    ],
)
def test_parent_rejects_contradictory_or_cross_invocation_success(
    overrides: dict[str, object],
) -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(0, _stdout(**overrides)))
    assert result["stage"] == "CHILD_PROTOCOL_OR_SERIALIZATION_FAILURE"


def test_validator_rejects_missing_required_field() -> None:
    payload = _success_payload()
    del payload["current_database"]
    with pytest.raises(ValueError, match="protocol violation"):
        validate_success_stdout(json.dumps(payload).encode(), INVOCATION_ID)


def test_validator_rejects_wrong_field_type() -> None:
    with pytest.raises(ValueError, match="protocol violation"):
        validate_success_stdout(_stdout(postgres_server_major="17"), INVOCATION_ID)


def test_validator_rejects_unexpected_credential_like_field() -> None:
    payload = _success_payload()
    payload["database_url"] = _synthetic_url()
    with pytest.raises(ValueError, match="protocol violation"):
        validate_success_stdout(json.dumps(payload).encode(), INVOCATION_ID)


def test_parent_does_not_retain_synthetic_stderr() -> None:
    canary = _synthetic_url()

    def launch(**_: object) -> tuple[int, bytes]:
        # The launcher API deliberately has no stderr return channel.
        assert canary
        return 43, b""

    serialized = json.dumps(run_parent(INVOCATION_ID, launcher=launch))
    assert canary not in serialized
    assert "stderr" not in serialized


def test_parent_rejects_sensitive_stdout_without_retaining_it() -> None:
    canary = _synthetic_url()
    result = run_parent(INVOCATION_ID, launcher=_launcher(0, canary.encode()))
    serialized = json.dumps(result)
    assert result["stage"] == "CHILD_PROTOCOL_OR_SERIALIZATION_FAILURE"
    assert canary not in serialized


def test_traceback_and_exception_repr_do_not_enter_failure_record() -> None:
    canary = "Traceback" + " synthetic exception repr"
    result = make_failure_bundle(
        invocation_id=INVOCATION_ID,
        child_return_code=47,
        stage="UNEXPECTED_CHILD_INTERNAL_FAILURE",
    )
    serialized = json.dumps(result)
    assert canary not in serialized
    assert "traceback" not in serialized.lower()
    assert "exception" not in serialized.lower()


class ExplodingEnvironment:
    def _explode(self, *_: object, **__: object) -> NoReturn:
        raise AssertionError("environment was accessed")

    __iter__ = _explode
    __getitem__ = _explode
    __len__ = _explode
    get = _explode
    keys = _explode
    items = _explode
    values = _explode
    copy = _explode


def test_parent_neither_enumerates_nor_copies_environment() -> None:
    env = fixed_child_environment(ExplodingEnvironment())
    assert env == {
        "LC_ALL": "C",
        "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
    }


def test_parent_does_not_read_unrelated_environment_variables() -> None:
    result = run_parent(
        INVOCATION_ID,
        launcher=_launcher(43),
        source_environment=ExplodingEnvironment(),
    )
    assert result["child_return_code"] == 43


def test_child_argv_contains_no_connection_material() -> None:
    argv = build_child_argv(INVOCATION_ID)
    joined = " ".join(argv).lower()
    assert argv[1:3] == ["-m", "tg_verifier_tools.verification.wp04_02_secure_pg_proof"]
    assert INVOCATION_ID in argv
    assert "postgresql" not in joined
    assert "database_url" not in joined
    assert "dsn" not in joined


def test_child_environment_contains_no_connection_material() -> None:
    env = fixed_child_environment(ExplodingEnvironment())
    serialized = json.dumps(env).lower()
    assert "postgresql" not in serialized
    assert "database_url" not in serialized
    assert "dsn" not in serialized


def test_parent_protocol_creates_no_temporary_connection_file(tmp_path: Path) -> None:
    before = list(tmp_path.iterdir())
    run_parent(INVOCATION_ID, launcher=_launcher(43), cwd=tmp_path)
    assert list(tmp_path.iterdir()) == before


def test_failure_bundle_contains_no_raw_stream_fields() -> None:
    bundle = make_failure_bundle(INVOCATION_ID, 43, "SQL_CONNECTION_FAILURE")
    assert "stdout" not in bundle
    assert "stderr" not in bundle
    assert "error" not in bundle


def test_child_success_emits_one_strict_document() -> None:
    writes: list[bytes] = []
    rc = child_main(
        INVOCATION_ID,
        loader=_synthetic_url,
        db_probe=lambda _: {
            "current_database": "postgres",
            "current_user": "postgres",
            "postgres_server_major": 17,
        },
        writer=writes.append,
    )
    assert rc == 0
    assert len(writes) == 1
    assert validate_success_stdout(writes[0], INVOCATION_ID)["query_count"] == 1


@pytest.mark.parametrize(
    ("loader", "probe", "expected"),
    [
        (lambda: (_ for _ in ()).throw(ImportError()), lambda _: {}, 41),
        (lambda: "", lambda _: {}, 42),
        (_synthetic_url, lambda _: (_ for _ in ()).throw(ConnectionFailure()), 43),
        (_synthetic_url, lambda _: (_ for _ in ()).throw(SelectFailure()), 44),
        (_synthetic_url, lambda _: (_ for _ in ()).throw(ResultSchemaFailure()), 45),
        (_synthetic_url, lambda _: (_ for _ in ()).throw(RuntimeError()), 47),
    ],
)
def test_child_uses_fixed_failure_exit_codes(loader: object, probe: object, expected: int) -> None:
    writes: list[bytes] = []
    assert (
        child_main(INVOCATION_ID, loader=loader, db_probe=probe, writer=writes.append) == expected
    )
    assert writes == []


def test_child_serialization_failure_uses_fixed_exit_code() -> None:
    def broken_writer(_: bytes) -> NoReturn:
        raise OSError

    rc = child_main(
        INVOCATION_ID,
        loader=_synthetic_url,
        db_probe=lambda _: {
            "current_database": "postgres",
            "current_user": "postgres",
            "postgres_server_major": 17,
        },
        writer=broken_writer,
    )
    assert rc == 46


def test_publisher_refuses_preexisting_formal_paths(tmp_path: Path) -> None:
    staged_evidence, staged_report = _staged_bundle(tmp_path)
    final_evidence = tmp_path / "formal-evidence"
    final_report = tmp_path / "formal-report.md"
    final_report.write_text("preexisting", encoding="utf-8")
    publisher = EvidencePublisher(final_report, final_evidence)
    with pytest.raises(FileExistsError):
        publisher.publish(staged_report, staged_evidence)
    assert final_report.read_text(encoding="utf-8") == "preexisting"
    assert not final_evidence.exists()


def test_publisher_rejects_race_and_preserves_competitor(tmp_path: Path) -> None:
    staged_evidence, staged_report = _staged_bundle(tmp_path)
    final_evidence = tmp_path / "formal-evidence"
    final_report = tmp_path / "formal-report.md"

    def race() -> None:
        final_evidence.mkdir()
        (final_evidence / "sentinel.txt").write_text("competitor", encoding="utf-8")

    publisher = EvidencePublisher(final_report, final_evidence)
    with pytest.raises(FileExistsError):
        publisher.publish(staged_report, staged_evidence, before_publish=race)
    assert (final_evidence / "sentinel.txt").read_text(encoding="utf-8") == "competitor"
    assert not final_report.exists()


def _staged_bundle(tmp_path: Path) -> tuple[Path, Path]:
    evidence = tmp_path / "staged-evidence"
    evidence.mkdir()
    (evidence / "result.json").write_text('{"safe":true}\n', encoding="utf-8")
    manifest = build_manifest(evidence)
    (evidence / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = tmp_path / "staged-report.md"
    report.write_text("safe report\n", encoding="utf-8")
    return evidence, report


def test_root_manifest_excludes_only_exact_root_manifest(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "manifest.json").write_text("root", encoding="utf-8")
    (tmp_path / "nested" / "manifest.json").write_text("nested", encoding="utf-8")
    manifest = build_manifest(tmp_path)
    paths = {item["path"] for item in manifest["files"]}
    assert "manifest.json" not in paths
    assert "nested/manifest.json" in paths


def test_manifest_rebuild_matches_paths_bytes_and_hashes(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text('{"a":1}\n', encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.txt").write_bytes(b"b\n")
    manifest = build_manifest(tmp_path)
    result = audit_manifest(tmp_path, manifest)
    assert result == {"missing": 0, "extra": 0, "byte_mismatch": 0, "hash_mismatch": 0}


def test_json_and_jsonl_audit_parses_every_document(tmp_path: Path) -> None:
    (tmp_path / "one.json").write_text('{"ok":true}\n', encoding="utf-8")
    (tmp_path / "many.jsonl").write_text('{"n":1}\n{"n":2}\n', encoding="utf-8")
    result = audit_json_documents(tmp_path)
    assert result["invalid"] == 0
    assert result["documents"] == 3


def test_credential_scanner_detects_memory_only_canary() -> None:
    canary = _synthetic_url().encode()
    findings = credential_scan_bytes(canary, "memory-only")
    assert findings == [{"finding_type": "URL_USERINFO", "path": "memory-only", "count": 1}]


def test_credential_scanner_detects_memory_only_sensitive_assignment() -> None:
    canary = ("password" + ' = "' + "memory-only-canary-value" + '"').encode()
    findings = credential_scan_bytes(canary, "memory-only")
    assert findings == [{"finding_type": "SENSITIVE_ASSIGNMENT", "path": "memory-only", "count": 1}]


def test_credential_scanner_does_not_self_match_formal_sources() -> None:
    paths = [
        Path(__file__),
        Path(__file__).parents[2]
        / "tg_verifier_tools"
        / "verification"
        / "wp04_02_secure_pg_proof.py",
    ]
    assert [
        finding for path in paths for finding in credential_scan_bytes(path.read_bytes(), str(path))
    ] == []


def test_synthetic_canary_is_not_a_literal_in_test_source() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    assert _synthetic_url() not in source


def test_proof_failure_closes_bundle_without_second_invocation(tmp_path: Path) -> None:
    calls: list[int] = []
    result = run_parent(INVOCATION_ID, launcher=_launcher(43, calls=calls))
    bundle_path = tmp_path / "proof-failure.json"
    bundle_path.write_text(json.dumps(result), encoding="utf-8")
    assert calls == [1]
    assert json.loads(bundle_path.read_text(encoding="utf-8"))["child_return_code"] == 43


def test_failure_bundle_child_return_code_is_never_null() -> None:
    bundle = make_failure_bundle(INVOCATION_ID, 43, "SQL_CONNECTION_FAILURE")
    assert isinstance(bundle["child_return_code"], int)


def test_failure_bundle_does_not_claim_connection_or_query_success() -> None:
    bundle = make_failure_bundle(INVOCATION_ID, 43, "SQL_CONNECTION_FAILURE")
    assert bundle["connection_count"] == 0
    assert bundle["query_count"] == 0
    assert bundle["schema_valid_result_count"] == 0


def test_success_requires_exact_single_connection_query_and_schema_result() -> None:
    result = run_parent(INVOCATION_ID, launcher=_launcher(0, _stdout()))
    assert (
        result["connection_count"],
        result["query_count"],
        result["schema_valid_result_count"],
    ) == (1, 1, 1)
