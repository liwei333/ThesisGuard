from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Callable


CONTAINER = "thesisguard-postgres"
IMAGE_REFERENCE = "pgvector/pgvector:pg17"
IMAGE_ID = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME = "thesisguard-postgres-data"
MOUNT_DESTINATION = "/var/lib/postgresql/data"
RESTART_POLICY = "unless-stopped"
CONTAINER_PORT = "5432/tcp"
HOST_PORT = "15432"
VOLUME_DRIVER = "local"


class CollectorError(RuntimeError):
    pass


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


COMMANDS: dict[str, list[str]] = {
    "name": ["docker", "inspect", "--format", "{{.Name}}", CONTAINER],
    "status": ["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER],
    "health": ["docker", "inspect", "--format", "{{.State.Health.Status}}", CONTAINER],
    "image_reference": ["docker", "inspect", "--format", "{{.Config.Image}}", CONTAINER],
    "image_id": ["docker", "inspect", "--format", "{{.Image}}", CONTAINER],
    "restart_policy": [
        "docker",
        "inspect",
        "--format",
        "{{.HostConfig.RestartPolicy.Name}}",
        CONTAINER,
    ],
    "mounts": ["docker", "inspect", "--format", "{{json .Mounts}}", CONTAINER],
    "port_bindings": [
        "docker",
        "inspect",
        "--format",
        "{{json .HostConfig.PortBindings}}",
        CONTAINER,
    ],
    "volume_driver": [
        "docker",
        "volume",
        "inspect",
        "--format",
        "{{.Driver}}",
        VOLUME,
    ],
}


FIXTURE_NAMES = {
    "name": "name.txt",
    "status": "state-status.txt",
    "health": "health-status.txt",
    "image_reference": "image-reference.txt",
    "image_id": "image-id.txt",
    "restart_policy": "restart-policy.txt",
    "mounts": "mounts.json",
    "port_bindings": "port-bindings.json",
    "volume_driver": "volume-driver.txt",
}


def command_for(field: str) -> list[str]:
    if field not in COMMANDS:
        raise CollectorError(f"unknown required field: {field}")
    return list(COMMANDS[field])


def fixture_name_for_command(argv: list[str]) -> str:
    for field, command in COMMANDS.items():
        if argv == command:
            return FIXTURE_NAMES[field]
    raise CollectorError("unknown dry-run command")


def parse_scalar(stdout: str, field: str) -> str:
    value = stdout.strip()
    if not value:
        raise CollectorError(f"{field}: empty stdout")
    if value == "<no value>":
        raise CollectorError(f"{field}: required field missing")
    if "\n" in value or "\r" in value:
        raise CollectorError(f"{field}: scalar contains multiple lines")
    return value


def parse_json_document(stdout: str, field: str, expected_type: type[Any]) -> Any:
    source = stdout.strip()
    if not source:
        raise CollectorError(f"{field}: empty stdout")
    decoder = json.JSONDecoder()
    try:
        value, end = decoder.raw_decode(source)
    except json.JSONDecodeError as exc:
        raise CollectorError(f"{field}: malformed JSON") from exc
    if source[end:].strip():
        raise CollectorError(f"{field}: trailing content or multiple JSON documents")
    if not isinstance(value, expected_type):
        raise CollectorError(f"{field}: wrong JSON type")
    return value


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _subprocess_runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def run_field(field: str, runner: Runner = _subprocess_runner) -> str:
    result = runner(command_for(field))
    if result.returncode != 0:
        raise CollectorError(f"{field}: subprocess return code {result.returncode}")
    if field in {"mounts", "port_bindings"}:
        expected_type = list if field == "mounts" else dict
        parse_json_document(result.stdout, field, expected_type)
    else:
        parse_scalar(result.stdout, field)
    return result.stdout


def _sanitize_mounts(mounts: list[Any]) -> list[dict[str, Any]]:
    if not mounts:
        raise CollectorError("mounts: empty Mounts")
    sanitized: list[dict[str, Any]] = []
    for item in mounts:
        if not isinstance(item, dict):
            raise CollectorError("mounts: wrong field type")
        required = {"Type", "Name", "Destination"}
        if not required.issubset(item):
            raise CollectorError("mounts: required field missing")
        sanitized.append(
            {
                "type": item["Type"],
                "name": item["Name"],
                "destination": item["Destination"],
                "driver": item.get("Driver"),
                "read_write": item.get("RW"),
            }
        )
    return sanitized


def _sanitize_port_bindings(bindings: dict[str, Any]) -> list[dict[str, str]]:
    if not bindings:
        raise CollectorError("port_bindings: empty PortBindings")
    if CONTAINER_PORT not in bindings:
        raise CollectorError("port_bindings: required field missing")
    values = bindings[CONTAINER_PORT]
    if not isinstance(values, list) or not values:
        raise CollectorError("port_bindings: wrong field type")
    sanitized: list[dict[str, str]] = []
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("HostPort"), str):
            raise CollectorError("port_bindings: wrong field type")
        host_ip = item.get("HostIp", "")
        if not isinstance(host_ip, str):
            raise CollectorError("port_bindings: wrong field type")
        sanitized.append({"host_ip": host_ip, "host_port": item["HostPort"]})
    return sanitized


def collect_identity(runner: Runner = _subprocess_runner) -> dict[str, Any]:
    scalar_fields = {
        field: parse_scalar(run_field(field, runner), field)
        for field in (
            "name",
            "status",
            "health",
            "image_reference",
            "image_id",
            "restart_policy",
            "volume_driver",
        )
    }
    if scalar_fields["status"] not in {
        "created",
        "running",
        "paused",
        "restarting",
        "removing",
        "exited",
        "dead",
    }:
        raise CollectorError("status: non-canonical value")
    if scalar_fields["health"] not in {"starting", "healthy", "unhealthy"}:
        raise CollectorError("health: non-canonical value")
    mounts = _sanitize_mounts(
        parse_json_document(run_field("mounts", runner), "mounts", list)
    )
    port_bindings_raw = parse_json_document(
        run_field("port_bindings", runner), "port_bindings", dict
    )
    port_bindings = _sanitize_port_bindings(port_bindings_raw)
    normalized_name = scalar_fields["name"].removeprefix("/")
    expected_mount = {
        "type": "volume",
        "name": VOLUME,
        "destination": MOUNT_DESTINATION,
    }
    mount_match = len(mounts) == 1 and all(
        mounts[0].get(key) == value for key, value in expected_mount.items()
    )
    port_match = set(port_bindings_raw) == {CONTAINER_PORT} and all(
        item["host_port"] == HOST_PORT for item in port_bindings
    )
    static_match = all(
        (
            normalized_name == CONTAINER,
            scalar_fields["image_reference"] == IMAGE_REFERENCE,
            scalar_fields["image_id"] == IMAGE_ID,
            scalar_fields["restart_policy"] == RESTART_POLICY,
            scalar_fields["volume_driver"] == VOLUME_DRIVER,
            mount_match,
            port_match,
        )
    )
    return {
        "container_name": normalized_name,
        "state_status": scalar_fields["status"],
        "health_status": scalar_fields["health"],
        "image_reference": scalar_fields["image_reference"],
        "image_id": scalar_fields["image_id"],
        "restart_policy": scalar_fields["restart_policy"],
        "volume_name": VOLUME,
        "volume_driver": scalar_fields["volume_driver"],
        "mounts": mounts,
        "container_port": CONTAINER_PORT,
        "host_port": HOST_PORT,
        "port_bindings": port_bindings,
        "static_identity_match": static_match,
        "runtime_ready": scalar_fields["status"] == "running"
        and scalar_fields["health"] == "healthy",
        "identity_match": static_match,
    }


def collect_from_fixture(directory: Path) -> dict[str, Any]:
    def fixture_runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
        fixture_path = directory / fixture_name_for_command(argv)
        if not fixture_path.is_file():
            return subprocess.CompletedProcess(argv, 2, stdout="", stderr="fixture missing")
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout=fixture_path.read_text(encoding="utf-8"),
            stderr="",
        )

    return collect_identity(fixture_runner)


def run_self_test() -> dict[str, Any]:
    suite = unittest.defaultTestLoader.discover(
        str(Path(__file__).resolve().parent), pattern="test_collector.py"
    )
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {
        "mode": "synthetic-self-test",
        "docker_called": False,
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.wasSuccessful(),
        "required_cases_minimum": 16,
        "case_count_satisfied": result.testsRun >= 16,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--dry-run", type=Path)
    modes.add_argument("--collect", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            payload = run_self_test()
            print(encode_json(payload), end="")
            return 0 if payload["successful"] and payload["case_count_satisfied"] else 1
        if args.dry_run is not None:
            payload = {
                "mode": "fixture-dry-run",
                "docker_called": False,
                "identity": collect_from_fixture(args.dry_run),
            }
            print(encode_json(payload), end="")
            return 0
        print(encode_json(collect_identity()), end="")
        return 0
    except CollectorError as exc:
        print(
            encode_json(
                {
                    "status": "ERROR",
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            ),
            end="",
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
