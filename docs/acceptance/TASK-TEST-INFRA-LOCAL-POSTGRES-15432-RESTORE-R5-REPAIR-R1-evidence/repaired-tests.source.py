#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import closure_helper as closure
import postgres_observer as observer
import stability_supervisor as supervisor


INVOCATION = "r5-test-7b1954d8"
CATALOG_HASH = "a" * 64
TASK_ID = "TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5"


def sample(sequence: int, **overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "invocation_id": INVOCATION,
        "sequence_number": sequence,
        "scheduled_offset_seconds": sequence * 5,
        "monotonic_elapsed_seconds": float(sequence * 5),
        "observed_at_utc": f"2026-09-23T00:00:{sequence * 5:02d}+00:00",
        "current_database": "postgres",
        "current_user": "thesisguard",
        "postgresql_major_version": 17,
        "observer_backend_pid": 12345,
        "catalog_row_count": 49,
        "catalog_canonical_sha256": CATALOG_HASH,
        "external_active_client_count": 0,
        "task_prefix_external_session_count": 0,
    }
    value.update(overrides)
    return value


def completion(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "invocation_id": INVOCATION,
        "sample_count": 7,
        "duration_seconds": 30.0,
        "catalog_row_counts": [49],
        "catalog_canonical_sha256_values": [CATALOG_HASH],
        "max_external_active_client_count": 0,
        "max_task_prefix_external_session_count": 0,
        "criteria_satisfied": True,
    }
    value.update(overrides)
    return value


def outcome(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "invocation_id": INVOCATION,
        "child_return_code": 0,
        "status": "OBSERVER_EXITED",
    }
    value.update(overrides)
    return value


class TimelineValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.timeline = self.root / "stability-timeline.jsonl"
        self.completion_path = self.root / "stability-completion.json"
        self.outcome_path = self.root / "stability-process-outcome.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_bundle(
        self,
        records: list[dict[str, object]] | None = None,
        completion_payload: dict[str, object] | None = None,
        outcome_payload: dict[str, object] | None = None,
    ) -> None:
        observer.write_records_durably(self.timeline, records or [sample(i) for i in range(7)])
        observer.atomic_publish_json(self.completion_path, completion_payload or completion())
        observer.atomic_publish_json(self.outcome_path, outcome_payload or outcome())

    def validate(self) -> dict[str, object]:
        return observer.validate_artifacts(
            timeline_path=self.timeline,
            completion_path=self.completion_path,
            outcome_path=self.outcome_path,
            invocation_id=INVOCATION,
            preflight_catalog_hash=CATALOG_HASH,
        )

    def assert_invalid(self) -> None:
        with self.assertRaises(observer.EvidenceValidationError):
            self.validate()

    def test_01_normal_seven_samples_pass(self) -> None:
        self.write_bundle()
        result = self.validate()
        self.assertTrue(result["criteria_satisfied"])
        self.assertEqual(result["sequence_numbers"], list(range(7)))

    def test_02_duration_below_thirty_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[-1]["monotonic_elapsed_seconds"] = 29.999
        self.write_bundle(records, completion(duration_seconds=29.999))
        self.assert_invalid()

    def test_03_fewer_than_seven_samples_fails(self) -> None:
        records = [sample(i) for i in range(6)]
        self.write_bundle(records, completion(sample_count=6, duration_seconds=25.0))
        self.assert_invalid()

    def test_04_invocation_id_mismatch_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[3]["invocation_id"] = "other"
        self.write_bundle(records)
        self.assert_invalid()

    def test_05_duplicate_sequence_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[4]["sequence_number"] = 3
        self.write_bundle(records)
        self.assert_invalid()

    def test_06_missing_sequence_fails(self) -> None:
        records = [sample(i) for i in (0, 1, 2, 3, 4, 5, 7)]
        self.write_bundle(records)
        self.assert_invalid()

    def test_07_out_of_order_sequence_fails(self) -> None:
        records = [sample(i) for i in (0, 1, 3, 2, 4, 5, 6)]
        self.write_bundle(records)
        self.assert_invalid()

    def test_08_truncated_jsonl_fails_with_prior_records_recoverable(self) -> None:
        observer.write_records_durably(self.timeline, [sample(i) for i in range(3)])
        with self.timeline.open("ab") as handle:
            handle.write(b'{"schema_version":1')
            handle.flush()
            os.fsync(handle.fileno())
        with self.assertRaises(observer.TimelineParseError) as captured:
            observer.parse_timeline(self.timeline)
        self.assertEqual(len(captured.exception.complete_records), 3)

    def test_09_malformed_json_line_fails(self) -> None:
        self.timeline.write_bytes(b'{"ok":1}\nnot-json\n')
        with self.assertRaises(observer.TimelineParseError):
            observer.parse_timeline(self.timeline)

    def test_10_catalog_row_count_change_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[5]["catalog_row_count"] = 50
        self.write_bundle(records, completion(catalog_row_counts=[49, 50]))
        self.assert_invalid()

    def test_11_catalog_hash_change_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[2]["catalog_canonical_sha256"] = "b" * 64
        self.write_bundle(records, completion(catalog_canonical_sha256_values=[CATALOG_HASH, "b" * 64]))
        self.assert_invalid()

    def test_12_external_active_client_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[1]["external_active_client_count"] = 1
        self.write_bundle(records, completion(max_external_active_client_count=1))
        self.assert_invalid()

    def test_13_task_prefix_external_session_fails(self) -> None:
        records = [sample(i) for i in range(7)]
        records[1]["task_prefix_external_session_count"] = 1
        self.write_bundle(records, completion(max_task_prefix_external_session_count=1))
        self.assert_invalid()

    def test_14_missing_completion_fails(self) -> None:
        observer.write_records_durably(self.timeline, [sample(i) for i in range(7)])
        observer.atomic_publish_json(self.outcome_path, outcome())
        self.assert_invalid()

    def test_15_completion_invocation_mismatch_fails(self) -> None:
        self.write_bundle(completion_payload=completion(invocation_id="other"))
        self.assert_invalid()

    def test_16_completion_sample_count_mismatch_fails(self) -> None:
        self.write_bundle(completion_payload=completion(sample_count=6))
        self.assert_invalid()

    def test_63_gate_index_hash_binding_passes_when_all_artifacts_match(self) -> None:
        gate_hash = "g" * 64
        records = [sample(i, prewindow_gate_index_sha256=gate_hash) for i in range(7)]
        self.write_bundle(
            records,
            completion(prewindow_gate_index_sha256=gate_hash),
            outcome(prewindow_gate_index_sha256=gate_hash),
        )
        result = observer.validate_artifacts(
            timeline_path=self.timeline,
            completion_path=self.completion_path,
            outcome_path=self.outcome_path,
            invocation_id=INVOCATION,
            preflight_catalog_hash=CATALOG_HASH,
            prewindow_gate_index_sha256=gate_hash,
        )
        self.assertTrue(result["criteria_satisfied"])

    def test_64_timeline_gate_index_hash_mismatch_fails(self) -> None:
        gate_hash = "g" * 64
        records = [sample(i, prewindow_gate_index_sha256=gate_hash) for i in range(7)]
        records[4]["prewindow_gate_index_sha256"] = "h" * 64
        self.write_bundle(
            records,
            completion(prewindow_gate_index_sha256=gate_hash),
            outcome(prewindow_gate_index_sha256=gate_hash),
        )
        with self.assertRaises(observer.EvidenceValidationError):
            observer.validate_artifacts(
                timeline_path=self.timeline,
                completion_path=self.completion_path,
                outcome_path=self.outcome_path,
                invocation_id=INVOCATION,
                preflight_catalog_hash=CATALOG_HASH,
                prewindow_gate_index_sha256=gate_hash,
            )

    def test_65_completion_or_outcome_gate_index_hash_mismatch_fails(self) -> None:
        gate_hash = "g" * 64
        records = [sample(i, prewindow_gate_index_sha256=gate_hash) for i in range(7)]
        self.write_bundle(
            records,
            completion(prewindow_gate_index_sha256="h" * 64),
            outcome(prewindow_gate_index_sha256=gate_hash),
        )
        with self.assertRaises(observer.EvidenceValidationError):
            observer.validate_artifacts(
                timeline_path=self.timeline,
                completion_path=self.completion_path,
                outcome_path=self.outcome_path,
                invocation_id=INVOCATION,
                preflight_catalog_hash=CATALOG_HASH,
                prewindow_gate_index_sha256=gate_hash,
            )

    def test_23_cross_invocation_old_artifacts_cannot_rescue_current(self) -> None:
        records = [sample(i, invocation_id="old") for i in range(7)]
        self.write_bundle(records, completion(invocation_id="old"), outcome(invocation_id=INVOCATION))
        self.assert_invalid()


class DurabilityAndSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_17_nonzero_child_exit_is_saved(self) -> None:
        outcome_path = self.root / "outcome.json"
        result = supervisor.run_child_and_record(
            [sys.executable, "-c", "raise SystemExit(7)"],
            outcome_path=outcome_path,
            invocation_id=INVOCATION,
            task_id=TASK_ID,
        )
        saved = json.loads(outcome_path.read_text(encoding="utf-8"))
        self.assertEqual(result, 7)
        self.assertEqual(saved["child_return_code"], 7)

    def test_18_interruption_preserves_first_n_complete_records(self) -> None:
        timeline = self.root / "timeline.jsonl"
        with self.assertRaises(observer.SyntheticInterruption):
            observer.write_records_durably(
                timeline,
                [sample(i) for i in range(7)],
                interrupt_after=4,
            )
        parsed = observer.parse_timeline(timeline)
        self.assertEqual([row["sequence_number"] for row in parsed], [0, 1, 2, 3])

    def test_19_existing_artifact_paths_are_rejected(self) -> None:
        path = self.root / "artifact.json"
        path.write_text("sentinel", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            observer.atomic_publish_json(path, {"new": True})
        self.assertEqual(path.read_text(encoding="utf-8"), "sentinel")

    def test_20_dry_run_uses_no_external_actions(self) -> None:
        with mock.patch("subprocess.run", side_effect=AssertionError("external command")), mock.patch(
            "socket.create_connection", side_effect=AssertionError("network")
        ):
            result = observer.dry_run(self.root / "dry-run")
        self.assertEqual(result["docker_calls"], 0)
        self.assertEqual(result["postgresql_connections"], 0)
        self.assertEqual(result["open_calls"], 0)
        self.assertEqual(result["docker_start_calls"], 0)

    def test_21_error_payload_redacts_credentials(self) -> None:
        secret = "".join(chr(value) for value in (115, 121, 110, 116, 104, 101, 116, 105, 99, 45, 99, 97, 110, 97, 114, 121))
        scheme = "postgresql" + ":" + "//"
        raw = f"{scheme}thesisguard:{secret}@127.0.0.1:15432/postgres dot-env {secret}"
        payload = observer.safe_failure_payload(INVOCATION, "OBSERVER_ERROR", RuntimeError(raw))
        encoded = json.dumps(payload, sort_keys=True)
        self.assertNotIn(secret, encoded)
        self.assertNotIn(scheme, encoded)
        self.assertNotIn("dot-env", encoded)

    def test_22_completion_publication_fsyncs_timeline_first(self) -> None:
        timeline = self.root / "timeline.jsonl"
        observer.write_records_durably(timeline, [sample(i) for i in range(7)])
        completion_path = self.root / "completion.json"
        events: list[str] = []
        with mock.patch.object(observer, "fsync_existing_file", side_effect=lambda _: events.append("timeline_fsync")), mock.patch.object(
            observer,
            "atomic_publish_json",
            side_effect=lambda path, payload: events.append("completion_publish"),
        ):
            observer.publish_completion_after_timeline_fsync(timeline, completion_path, completion())
        self.assertEqual(events, ["timeline_fsync", "completion_publish"])

    def test_24_synthetic_clock_is_forbidden_in_formal_mode(self) -> None:
        with self.assertRaises(observer.ObserverError):
            observer.require_clock_mode(mode="formal", clock_mode="synthetic")
        self.assertEqual(observer.require_clock_mode(mode="formal", clock_mode="real-monotonic"), "real-monotonic")
        self.assertEqual(observer.require_clock_mode(mode="dry-run", clock_mode="synthetic"), "synthetic")


class SourceSafetyTests(unittest.TestCase):
    def test_sources_do_not_embed_forbidden_mutations(self) -> None:
        combined = "\n".join(
            [
                Path(observer.__file__).read_text(encoding="utf-8"),
                Path(supervisor.__file__).read_text(encoding="utf-8"),
            ]
        ).lower()
        forbidden = (
            "create database",
            "drop database",
            "alter database",
            "pg_terminate_backend",
            "docker compose up",
            "docker restart",
            "docker stop",
        )
        for token in forbidden:
            self.assertNotIn(token, combined)

    def test_stdout_contains_only_fixed_status_tokens(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            observer.emit_status("DRY_RUN_OK")
        self.assertEqual(stream.getvalue(), "DRY_RUN_OK\n")


class NoClobberPublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_27_existing_target_before_call_is_unchanged(self) -> None:
        target = self.root / "target"
        target.write_bytes(b"winner")
        with self.assertRaises(FileExistsError):
            closure.publish_bytes_no_clobber(target, b"loser")
        self.assertEqual(target.read_bytes(), b"winner")

    def test_28_target_created_immediately_before_link_is_unchanged(self) -> None:
        target = self.root / "target"

        def competitor(_: Path, destination: Path) -> None:
            destination.write_bytes(b"competitor")

        with self.assertRaises(FileExistsError):
            closure.publish_bytes_no_clobber(target, b"publisher", before_link=competitor)
        self.assertEqual(target.read_bytes(), b"competitor")

    def test_29_symlink_target_is_not_followed_or_replaced(self) -> None:
        referent = self.root / "referent"
        referent.write_bytes(b"referent")
        target = self.root / "target"
        target.symlink_to(referent)
        with self.assertRaises(FileExistsError):
            closure.publish_bytes_no_clobber(target, b"publisher")
        self.assertTrue(target.is_symlink())
        self.assertEqual(referent.read_bytes(), b"referent")

    def test_30_two_publishers_yield_one_unchanged_winner(self) -> None:
        target = self.root / "target"
        barrier = threading.Barrier(2)
        results: list[str] = []

        def publish(label: str) -> None:
            try:
                closure.publish_bytes_no_clobber(
                    target,
                    label.encode("ascii"),
                    before_link=lambda _temp, _target: barrier.wait(timeout=5),
                )
                results.append(f"won:{label}")
            except FileExistsError:
                results.append(f"lost:{label}")

        threads = [threading.Thread(target=publish, args=(label,)) for label in ("A", "B")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(len([item for item in results if item.startswith("won:")]), 1)
        winner = next(item.split(":", 1)[1] for item in results if item.startswith("won:"))
        self.assertEqual(target.read_bytes(), winner.encode("ascii"))

    def test_31_failure_cleans_only_its_own_temporary_file(self) -> None:
        target = self.root / "target"
        target.write_bytes(b"winner")
        unrelated = self.root / ".target.tmp-unrelated"
        unrelated.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            closure.publish_bytes_no_clobber(target, b"loser")
        self.assertEqual(unrelated.read_bytes(), b"keep")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), [unrelated.name, target.name])

    def test_32_successful_publish_has_exact_bytes(self) -> None:
        target = self.root / "target"
        closure.publish_bytes_no_clobber(target, b"exact-payload")
        self.assertEqual(target.read_bytes(), b"exact-payload")

    def test_33_successful_publish_uses_requested_permissions(self) -> None:
        target = self.root / "target"
        closure.publish_bytes_no_clobber(target, b"x", mode=0o640)
        self.assertEqual(target.stat().st_mode & 0o777, 0o640)

    def test_34_successful_publish_fsyncs_parent_directory(self) -> None:
        target = self.root / "target"
        with mock.patch.object(closure, "fsync_directory") as directory_fsync:
            closure.publish_bytes_no_clobber(target, b"x")
        directory_fsync.assert_called_with(self.root)

    def test_35_failure_removes_owned_temp_and_fsyncs_parent(self) -> None:
        target = self.root / "target"
        with mock.patch.object(closure, "fsync_directory") as directory_fsync:
            with self.assertRaises(FileExistsError):
                closure.publish_bytes_no_clobber(
                    target,
                    b"x",
                    before_link=lambda _temp, destination: destination.write_bytes(b"winner"),
                )
        directory_fsync.assert_called_with(self.root)
        self.assertFalse(any(path.name.startswith(".target.tmp-") for path in self.root.iterdir()))

    def test_36_formal_publisher_source_contains_no_os_replace(self) -> None:
        source = Path(closure.__file__).read_text(encoding="utf-8")
        self.assertNotIn("os.replace", source)


class PrewindowGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.invocation_id = "repair-test-invocation"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_receipts(self) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        for gate_type in closure.REQUIRED_GATE_TYPES:
            path = self.root / f"{gate_type}.json"
            closure.write_receipt(
                path,
                receipt_type=gate_type,
                invocation_id=self.invocation_id,
                started_at_utc="2026-09-23T00:00:00+00:00",
                completed_at_utc="2026-09-23T00:00:01+00:00",
                monotonic_started=1.0,
                monotonic_finished=2.0,
                exit_code=0,
                criteria_satisfied=True,
                semantic_command=f"synthetic {gate_type}",
                relevant_result={"bytecode_file_count": 0, "pycache_directory_count": 0},
                source_config_sha256="a" * 64,
            )
            paths[gate_type] = path
        return paths

    def _valid_index(self) -> Path:
        receipts = self._write_receipts()
        index = closure.build_gate_index(
            self.root,
            receipts,
            invocation_id=self.invocation_id,
            bytecode_count=0,
            formal_paths=[self.root / name for name in closure.FORMAL_ARTIFACT_NAMES],
            generated_at_utc="2026-09-23T00:00:02+00:00",
        )
        path = self.root / "prewindow-gate-index.json"
        closure.publish_json_no_clobber(path, index)
        return path

    def _rewrite_index(self, path: Path, mutate: object) -> None:
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutate(payload)  # type: ignore[operator]
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_37_valid_gate_index_passes(self) -> None:
        path = self._valid_index()
        result = closure.validate_gate_index(
            path,
            self.root,
            invocation_id=self.invocation_id,
            formal_invocation_started_at_utc="2026-09-23T00:00:03+00:00",
        )
        self.assertTrue(result["criteria_satisfied"])

    def test_38_missing_receipt_file_fails(self) -> None:
        path = self._valid_index()
        (self.root / "docker-identity.json").unlink()
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_39_failed_receipt_fails(self) -> None:
        path = self._valid_index()
        receipt = self.root / "pg-isready.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["criteria_satisfied"] = False
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_40_receipt_hash_mismatch_fails(self) -> None:
        path = self._valid_index()
        receipt = self.root / "git-baseline.json"
        receipt.write_bytes(receipt.read_bytes() + b"\n")
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_41_receipt_timestamp_after_index_fails(self) -> None:
        path = self._valid_index()
        receipt = self.root / "fixed-input-hash.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["completed_at_utc"] = "2026-09-23T00:00:04+00:00"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        self._rewrite_index(
            path,
            lambda index: next(item for item in index["receipts"] if item["receipt_type"] == "fixed-input-hash").update(
                closure.file_record(receipt, self.root)
            ),
        )
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_42_gate_index_after_formal_invocation_fails(self) -> None:
        path = self._valid_index()
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(
                path,
                self.root,
                invocation_id=self.invocation_id,
                formal_invocation_started_at_utc="2026-09-23T00:00:01.500000+00:00",
            )

    def test_43_repair_invocation_id_mismatch_fails(self) -> None:
        path = self._valid_index()
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id="other")

    def test_44_stale_r5_receipt_fails(self) -> None:
        path = self._valid_index()
        receipt = self.root / "r5-helper-source-import-hash.json"
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["task_id"] = closure.ORIGINAL_TASK_ID
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        self._rewrite_index(
            path,
            lambda index: next(item for item in index["receipts"] if item["receipt_type"] == "r5-helper-source-import-hash").update(
                closure.file_record(receipt, self.root)
            ),
        )
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_45_index_missing_required_gate_fails(self) -> None:
        path = self._valid_index()
        self._rewrite_index(path, lambda index: index["receipts"].pop())
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_46_formal_path_already_exists_fails(self) -> None:
        path = self._valid_index()
        (self.root / closure.FORMAL_ARTIFACT_NAMES[0]).write_bytes(b"exists")
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_47_nonzero_bytecode_count_fails(self) -> None:
        path = self._valid_index()
        self._rewrite_index(path, lambda index: index.update(bytecode_count=1))
        with self.assertRaises(closure.GateValidationError):
            closure.validate_gate_index(path, self.root, invocation_id=self.invocation_id)

    def test_48_supervisor_does_not_start_child_for_invalid_index(self) -> None:
        path = self._valid_index()
        self._rewrite_index(path, lambda index: index["receipts"].pop())
        with mock.patch.object(supervisor, "run_child_and_record") as run_child:
            with self.assertRaises(closure.GateValidationError):
                supervisor.formal_supervise(
                    observer_source=self.root / "observer.py",
                    env_path=self.root / ".env",
                    evidence_dir=self.root,
                    invocation_id=self.invocation_id,
                    preflight_catalog_hash="a" * 64,
                    gate_index_path=path,
                )
        run_child.assert_not_called()


class BytecodeConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_49_pyc_causes_failure_and_is_not_deleted(self) -> None:
        pyc = self.root / "bad.pyc"
        pyc.write_bytes(b"bytecode")
        with self.assertRaises(closure.BytecodeConsistencyError):
            closure.assert_no_bytecode(self.root)
        self.assertTrue(pyc.exists())

    def test_50_pycache_directory_causes_failure(self) -> None:
        (self.root / "__pycache__").mkdir()
        with self.assertRaises(closure.BytecodeConsistencyError):
            closure.assert_no_bytecode(self.root)

    def test_51_compile_receipt_actual_and_planned_set_must_agree(self) -> None:
        receipt = {"criteria_satisfied": True, "relevant_result": {"bytecode_file_count": 0, "pycache_directory_count": 0}}
        result = closure.bytecode_consistency(receipt, self.root, ["source.py", "manifest.json"])
        self.assertTrue(result["criteria_satisfied"])
        with self.assertRaises(closure.BytecodeConsistencyError):
            closure.bytecode_consistency(receipt, self.root, ["__pycache__/source.pyc"])


class ClosureStateMachineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "payload.json").write_text('{"ok": true}\n', encoding="utf-8")
        self.report = self.root.parent / f"report-{Path(self.temp.name).name}.md"
        self.report.write_text("credential-safe report\n", encoding="utf-8")

    def tearDown(self) -> None:
        if self.report.exists():
            self.report.unlink()
        self.temp.cleanup()

    def test_52_credential_scan_requires_payloads_final(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=False)
        with self.assertRaises(closure.ClosureStateError):
            machine.finalize_credential_scan(self.report, secret=None)

    def test_53_json_audit_requires_credential_scan(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        with self.assertRaises(closure.ClosureStateError):
            machine.finalize_json_parse_audit()

    def test_54_credential_scan_cannot_be_finalized_twice(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        with self.assertRaises(closure.ClosureStateError):
            machine.finalize_credential_scan(self.report, secret=None)

    def test_55_json_audit_records_final_credential_scan_hash(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        credential = machine.finalize_credential_scan(self.report, secret=None)
        audit = machine.finalize_json_parse_audit()
        payload = json.loads(audit.read_text(encoding="utf-8"))
        self.assertEqual(payload["credential_scan_sha256"], closure.sha256_file(credential))

    def test_56_accept_json_audit_rejects_wrong_credential_hash(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        credential = machine.finalize_credential_scan(self.report, secret=None)
        bad = self.root / "bad-json-audit.json"
        bad.write_text(json.dumps({"credential_scan_sha256": "0" * 64}), encoding="utf-8")
        with self.assertRaises(closure.ClosureStateError):
            machine.accept_json_parse_audit(bad, credential)

    def test_57_manifest_requires_json_audit(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        with self.assertRaises(closure.ClosureStateError):
            machine.finalize_manifest()

    def test_58_manifest_includes_credential_and_json_audit(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        credential = machine.finalize_credential_scan(self.report, secret=None)
        audit = machine.finalize_json_parse_audit()
        manifest = machine.finalize_manifest()
        paths = {item["relative_path"] for item in json.loads(manifest.read_text(encoding="utf-8"))["files"]}
        self.assertIn(credential.name, paths)
        self.assertIn(audit.name, paths)

    def test_59_manifest_generated_after_json_audit(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        audit = machine.finalize_json_parse_audit()
        manifest = machine.finalize_manifest()
        audit_time = datetime.fromisoformat(json.loads(audit.read_text(encoding="utf-8"))["generated_at_utc"])
        manifest_time = datetime.fromisoformat(json.loads(manifest.read_text(encoding="utf-8"))["generated_at_utc"])
        self.assertLess(audit_time, manifest_time)

    def test_60_extra_file_after_manifest_is_detected(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        machine.finalize_json_parse_audit()
        manifest = machine.finalize_manifest()
        (self.root / "late.txt").write_text("late", encoding="utf-8")
        self.assertFalse(closure.rebuild_manifest(self.root, manifest)["criteria_satisfied"])

    def test_61_changed_file_after_manifest_is_detected(self) -> None:
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        machine.finalize_json_parse_audit()
        manifest = machine.finalize_manifest()
        (self.root / "payload.json").write_text('{"ok": false}\n', encoding="utf-8")
        result = closure.rebuild_manifest(self.root, manifest)
        self.assertFalse(result["criteria_satisfied"])
        self.assertEqual(result["hash_mismatch"], ["payload.json"])

    def test_62_nested_manifest_basename_is_included(self) -> None:
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "manifest.json").write_text('{"nested": true}\n', encoding="utf-8")
        machine = closure.ClosureStateMachine(self.root, payloads_final=True)
        machine.finalize_credential_scan(self.report, secret=None)
        machine.finalize_json_parse_audit()
        manifest = machine.finalize_manifest()
        paths = {item["relative_path"] for item in json.loads(manifest.read_text(encoding="utf-8"))["files"]}
        self.assertIn("nested/manifest.json", paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
