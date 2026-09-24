from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import collector


def completed(stdout: str, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["docker"], returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    def __init__(self, results: dict[tuple[str, ...], subprocess.CompletedProcess[str]]) -> None:
        self.results = results
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        key = tuple(argv)
        self.calls.append(key)
        if key not in self.results:
            raise AssertionError(f"unexpected argv: {argv!r}")
        return self.results[key]


def valid_results() -> dict[tuple[str, ...], subprocess.CompletedProcess[str]]:
    mounts = [
        {
            "Type": "volume",
            "Name": "thesisguard-postgres-data",
            "Source": "/var/lib/docker/volumes/thesisguard-postgres-data/_data",
            "Destination": "/var/lib/postgresql/data",
            "Driver": "local",
            "Mode": "rw",
            "RW": True,
            "Propagation": "",
        }
    ]
    ports = {"5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "15432"}]}
    return {
        tuple(collector.command_for("name")): completed("/thesisguard-postgres\n"),
        tuple(collector.command_for("status")): completed("running\n"),
        tuple(collector.command_for("health")): completed("healthy\n"),
        tuple(collector.command_for("image_reference")): completed("pgvector/pgvector:pg17\n"),
        tuple(collector.command_for("image_id")): completed(
            "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f\n"
        ),
        tuple(collector.command_for("restart_policy")): completed("unless-stopped\n"),
        tuple(collector.command_for("mounts")): completed(json.dumps(mounts) + "\n"),
        tuple(collector.command_for("port_bindings")): completed(json.dumps(ports) + "\n"),
        tuple(collector.command_for("volume_driver")): completed("local\n"),
    }


class CollectorTests(unittest.TestCase):
    def test_normal_scalar(self) -> None:
        self.assertEqual(collector.parse_scalar("healthy\n", "health"), "healthy")

    def test_normal_mounts_json(self) -> None:
        parsed = collector.parse_json_document('[{"Name":"v"}]\n', "mounts", list)
        self.assertEqual(parsed, [{"Name": "v"}])

    def test_normal_port_bindings_json(self) -> None:
        parsed = collector.parse_json_document('{"5432/tcp":[]}', "ports", dict)
        self.assertEqual(parsed, {"5432/tcp": []})

    def test_empty_stdout_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_scalar("", "name")

    def test_whitespace_only_stdout_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_scalar("  \n\t", "name")

    def test_malformed_json_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_json_document("{", "mounts", list)

    def test_valid_json_with_trailing_garbage_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_json_document("[] garbage", "mounts", list)

    def test_multiple_json_documents_fail_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_json_document("[] {}", "mounts", list)

    def test_multiline_scalar_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_scalar("running\nhealthy\n", "status")

    def test_subprocess_nonzero_exit_fails_closed_without_stderr_retention(self) -> None:
        runner = FakeRunner({tuple(collector.command_for("name")): completed("", 1, "secret-value")})
        with self.assertRaisesRegex(collector.CollectorError, "return code 1") as caught:
            collector.run_field("name", runner)
        self.assertNotIn("secret-value", str(caught.exception))

    def test_required_field_missing_fails_closed(self) -> None:
        results = valid_results()
        results[tuple(collector.command_for("image_reference"))] = completed("")
        with self.assertRaises(collector.CollectorError):
            collector.collect_identity(FakeRunner(results))

    def test_wrong_field_type_fails_closed(self) -> None:
        with self.assertRaises(collector.CollectorError):
            collector.parse_json_document("{}", "mounts", list)

    def test_safe_json_encoding_handles_quotes_backslashes_and_unicode(self) -> None:
        encoded = collector.encode_json({"value": 'quote " slash \\ 中文'})
        self.assertEqual(json.loads(encoded), {"value": 'quote " slash \\ 中文'})

    def test_health_field_missing_fails_closed(self) -> None:
        results = valid_results()
        results[tuple(collector.command_for("health"))] = completed("<no value>\n")
        with self.assertRaises(collector.CollectorError):
            collector.collect_identity(FakeRunner(results))

    def test_empty_mounts_fail_closed(self) -> None:
        results = valid_results()
        results[tuple(collector.command_for("mounts"))] = completed("[]\n")
        with self.assertRaises(collector.CollectorError):
            collector.collect_identity(FakeRunner(results))

    def test_empty_port_bindings_fail_closed(self) -> None:
        results = valid_results()
        results[tuple(collector.command_for("port_bindings"))] = completed("{}\n")
        with self.assertRaises(collector.CollectorError):
            collector.collect_identity(FakeRunner(results))

    def test_valid_inputs_produce_exact_expected_structure(self) -> None:
        identity = collector.collect_identity(FakeRunner(valid_results()))
        self.assertEqual(identity["container_name"], "thesisguard-postgres")
        self.assertEqual(identity["state_status"], "running")
        self.assertEqual(identity["health_status"], "healthy")
        self.assertEqual(identity["volume_driver"], "local")
        self.assertEqual(identity["host_port"], "15432")
        self.assertEqual(identity["container_port"], "5432/tcp")

    def test_dry_run_reads_fixture_directory_without_docker(self) -> None:
        with TemporaryDirectory() as directory:
            fixture = Path(directory)
            for field, result in valid_results().items():
                name = collector.fixture_name_for_command(list(field))
                (fixture / name).write_text(result.stdout, encoding="utf-8")
            identity = collector.collect_from_fixture(fixture)
            self.assertEqual(identity["identity_match"], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
