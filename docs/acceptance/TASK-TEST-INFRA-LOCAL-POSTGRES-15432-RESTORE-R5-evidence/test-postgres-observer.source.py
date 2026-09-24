#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
