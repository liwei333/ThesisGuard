"""Credential-safe, one-shot PostgreSQL identity proof for WP-04-02.

The parent process never reads database connection material.  It launches this
module as a child with a fixed argv and fixed environment, discards child
stderr, retains only a bounded stdout buffer, and accepts exactly one strict
success JSON document.  Failed children are classified solely by their numeric
return code; raw output and exception details are never retained.

The child imports the already-existing test fixture module by exact name and
obtains its connection value inside the child process.  The value is never
placed in argv, environment, a temporary file, stdout, stderr, a report, or an
evidence bundle.  The live probe opens at most one connection and executes
exactly one fixed read-only SELECT.
"""

from __future__ import annotations

import asyncio
import contextlib
import ctypes
import errno
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
import threading
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, BinaryIO

SCHEMA_VERSION = 1
FIXED_PYTHON = "/opt/homebrew/bin/python3.12"
DEFAULT_TIMEOUT_SECONDS = 30
MAX_STDOUT_BYTES = 4096
OPAQUE_LOADER_MODULE = "tests.evidence_pg_fixture"
OPAQUE_VALUE_ATTRIBUTE = "DEFAULT_ADMIN_DATABASE_URL"
FIXED_READ_ONLY_SELECT = (
    "SELECT current_database() AS current_database, "
    "current_user AS current_user, "
    "current_setting('server_version_num')::integer AS server_version_num"
)

CHILD_EXIT_STAGES: dict[int, str] = {
    0: "SUCCESS",
    41: "OPAQUE_LOADER_IMPORT_FAILURE",
    42: "OPAQUE_VALUE_UNAVAILABLE_OR_INVALID",
    43: "SQL_CONNECTION_FAILURE",
    44: "FIXED_SELECT_FAILURE",
    45: "RESULT_SCHEMA_FAILURE",
    46: "CHILD_PROTOCOL_OR_SERIALIZATION_FAILURE",
    47: "UNEXPECTED_CHILD_INTERNAL_FAILURE",
    124: "TIMEOUT",
    130: "INTERRUPTED",
}

_SUCCESS_FIELDS = frozenset(
    {
        "schema_version",
        "invocation_id",
        "outcome",
        "child_return_code",
        "stage",
        "connection_count",
        "query_count",
        "schema_valid_result_count",
        "current_database",
        "current_user",
        "postgres_server_major",
    }
)
_SAFE_ID = re.compile(r"\A[0-9a-f]{64}\Z")
_SAFE_DB_IDENTIFIER = re.compile(r"\A[A-Za-z0-9_.-]{1,128}\Z")
_URL_USERINFO = re.compile(rb"[A-Za-z][A-Za-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@")
_SENSITIVE_ASSIGNMENT = re.compile(
    rb"(?i)(?:password|passwd|token|secret|database_url|dsn)\s*[:=]\s*"
    rb"[\"'][A-Za-z0-9_./+=-]{12,}[\"']"
)


class TimedOutChild(Exception):
    """The child exceeded the fixed parent timeout."""


class InterruptedChild(Exception):
    """The parent was interrupted while waiting for its only child."""


class ConnectionFailure(Exception):
    """The child could not establish its single PostgreSQL connection."""


class SelectFailure(Exception):
    """The child's single fixed SELECT failed."""


class ResultSchemaFailure(Exception):
    """The fixed SELECT result did not have the required safe schema."""


class OpaqueLoaderImportFailure(Exception):
    """The exact opaque loader module could not be imported."""


def fixed_child_environment(source_environment: object | None = None) -> dict[str, str]:
    """Return the child allowlist without reading *source_environment* at all."""
    del source_environment
    return {
        "LC_ALL": "C",
        "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
    }


def build_child_argv(invocation_id: str) -> list[str]:
    """Return fixed child argv containing only code location and invocation ID."""
    _validate_invocation_id(invocation_id)
    return [
        FIXED_PYTHON,
        "-m",
        "tg_verifier_tools.verification.wp04_02_secure_pg_proof",
        "--child",
        invocation_id,
    ]


def _validate_invocation_id(invocation_id: str) -> None:
    if not isinstance(invocation_id, str) or _SAFE_ID.fullmatch(invocation_id) is None:
        raise ValueError("protocol violation")


def _bounded_reader(stream: BinaryIO, limit: int, output: list[bytes]) -> None:
    retained = bytearray()
    while True:
        chunk = stream.read(1024)
        if not chunk:
            break
        if len(retained) <= limit:
            remaining = limit + 1 - len(retained)
            retained.extend(chunk[:remaining])
    output.append(bytes(retained))


def launch_child(
    *,
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    max_stdout: int,
) -> tuple[int, bytes]:
    """Launch one child and retain at most ``max_stdout + 1`` stdout bytes."""
    process = subprocess.Popen(  # noqa: S603 - fixed absolute runtime and local source
        argv,
        cwd=str(cwd),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    if process.stdout is None:
        process.kill()
        process.wait()
        return 47, b""

    retained: list[bytes] = []
    reader = threading.Thread(
        target=_bounded_reader,
        args=(process.stdout, max_stdout, retained),
        daemon=True,
    )
    reader.start()
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        reader.join(timeout=5)
        raise TimedOutChild from None
    except KeyboardInterrupt:
        process.kill()
        process.wait()
        reader.join(timeout=5)
        raise InterruptedChild from None
    reader.join(timeout=5)
    if reader.is_alive():
        process.kill()
        process.wait()
        raise TimedOutChild
    return returncode, retained[0] if retained else b""


def make_failure_bundle(
    invocation_id: str,
    child_return_code: int,
    stage: str,
) -> dict[str, object]:
    """Build a fixed-schema failure record without any raw diagnostic channel."""
    _validate_invocation_id(invocation_id)
    if type(child_return_code) is not int or not isinstance(stage, str):
        raise ValueError("protocol violation")
    return {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": invocation_id,
        "outcome": "FAILURE",
        "parent_return_code": 1,
        "child_return_code": child_return_code,
        "stage": stage,
        "connection_count": 0,
        "query_count": 0,
        "schema_valid_result_count": 0,
    }


def validate_success_stdout(stdout: bytes, invocation_id: str) -> dict[str, object]:
    """Validate one exact, bounded child success JSON document."""
    _validate_invocation_id(invocation_id)
    if not stdout or len(stdout) > MAX_STDOUT_BYTES:
        raise ValueError("protocol violation")
    try:
        text = stdout.decode("utf-8", errors="strict")
        decoder = json.JSONDecoder()
        payload, end = decoder.raw_decode(text)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("protocol violation") from None
    if end != len(text) or not isinstance(payload, dict) or set(payload) != _SUCCESS_FIELDS:
        raise ValueError("protocol violation")

    exact_values = {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": invocation_id,
        "outcome": "SUCCESS",
        "child_return_code": 0,
        "stage": "SUCCESS",
        "connection_count": 1,
        "query_count": 1,
        "schema_valid_result_count": 1,
    }
    for key, expected in exact_values.items():
        value = payload.get(key)
        if type(value) is not type(expected) or value != expected:
            raise ValueError("protocol violation")
    for key in ("current_database", "current_user"):
        value = payload.get(key)
        if not isinstance(value, str) or _SAFE_DB_IDENTIFIER.fullmatch(value) is None:
            raise ValueError("protocol violation")
    major = payload.get("postgres_server_major")
    if type(major) is not int or not 9 <= major <= 99:
        raise ValueError("protocol violation")
    return dict(payload)


Launcher = Callable[..., tuple[int, bytes]]


def run_parent(
    invocation_id: str,
    *,
    launcher: Launcher = launch_child,
    cwd: Path | None = None,
    source_environment: object | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, object]:
    """Run exactly one child and return only a credential-safe proof record."""
    _validate_invocation_id(invocation_id)
    argv = build_child_argv(invocation_id)
    env = fixed_child_environment(source_environment)
    try:
        returncode, stdout = launcher(
            argv=argv,
            cwd=(cwd or Path.cwd()).resolve(),
            env=env,
            timeout=timeout,
            max_stdout=MAX_STDOUT_BYTES,
        )
    except TimedOutChild:
        return make_failure_bundle(invocation_id, 124, CHILD_EXIT_STAGES[124])
    except (InterruptedChild, KeyboardInterrupt):
        return make_failure_bundle(invocation_id, 130, CHILD_EXIT_STAGES[130])
    except BaseException:
        return make_failure_bundle(invocation_id, 47, CHILD_EXIT_STAGES[47])

    if type(returncode) is not int:
        return make_failure_bundle(invocation_id, 47, CHILD_EXIT_STAGES[47])
    if returncode != 0:
        stage = CHILD_EXIT_STAGES.get(returncode, "UNKNOWN_CHILD_RETURN_CODE")
        return make_failure_bundle(invocation_id, returncode, stage)
    try:
        payload = validate_success_stdout(stdout, invocation_id)
    except ValueError:
        return make_failure_bundle(invocation_id, 0, CHILD_EXIT_STAGES[46])
    payload["parent_return_code"] = 0
    return payload


def _load_opaque_value() -> object:
    try:
        module = importlib.import_module(OPAQUE_LOADER_MODULE)
    except BaseException:
        raise OpaqueLoaderImportFailure from None
    return getattr(module, OPAQUE_VALUE_ATTRIBUTE, None)


def _validated_result(result: Mapping[str, object]) -> dict[str, object]:
    if set(result) != {"current_database", "current_user", "postgres_server_major"}:
        raise ResultSchemaFailure
    for key in ("current_database", "current_user"):
        value = result.get(key)
        if not isinstance(value, str) or _SAFE_DB_IDENTIFIER.fullmatch(value) is None:
            raise ResultSchemaFailure
    major = result.get("postgres_server_major")
    if type(major) is not int or not 9 <= major <= 99:
        raise ResultSchemaFailure
    return dict(result)


async def _async_database_probe(connection_value: str) -> dict[str, object]:
    try:
        import asyncpg
    except BaseException:
        raise ConnectionFailure from None

    dsn = connection_value
    prefix = "postgresql+asyncpg://"
    if dsn.startswith(prefix):
        dsn = "postgresql://" + dsn[len(prefix) :]

    connection: Any | None = None
    try:
        connection = await asyncpg.connect(dsn=dsn, timeout=10)
    except BaseException:
        raise ConnectionFailure from None
    try:
        try:
            row = await connection.fetchrow(FIXED_READ_ONLY_SELECT, timeout=10)
        except BaseException:
            raise SelectFailure from None
        if row is None:
            raise ResultSchemaFailure
        try:
            version_num = int(row["server_version_num"])
            result = {
                "current_database": row["current_database"],
                "current_user": row["current_user"],
                "postgres_server_major": version_num // 10000,
            }
        except BaseException:
            raise ResultSchemaFailure from None
        return _validated_result(result)
    finally:
        with contextlib.suppress(BaseException):
            await connection.close(timeout=5)


def _database_probe(connection_value: str) -> dict[str, object]:
    return asyncio.run(_async_database_probe(connection_value))


def _stdout_writer(payload: bytes) -> None:
    written = os.write(sys.stdout.fileno(), payload)
    if written != len(payload):
        raise OSError


def child_main(
    invocation_id: str,
    *,
    loader: Callable[[], object] = _load_opaque_value,
    db_probe: Callable[[str], Mapping[str, object]] = _database_probe,
    writer: Callable[[bytes], object] = _stdout_writer,
) -> int:
    """Run the child protocol without ever emitting failure diagnostics."""
    try:
        _validate_invocation_id(invocation_id)
    except ValueError:
        return 46
    try:
        connection_value = loader()
    except (ImportError, OpaqueLoaderImportFailure):
        return 41
    except BaseException:
        return 41
    if (
        not isinstance(connection_value, str)
        or not connection_value
        or len(connection_value) > 4096
        or not connection_value.startswith(("postgresql://", "postgresql+asyncpg://"))
    ):
        return 42
    try:
        result = _validated_result(db_probe(connection_value))
    except ConnectionFailure:
        return 43
    except SelectFailure:
        return 44
    except ResultSchemaFailure:
        return 45
    except BaseException:
        return 47
    try:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "invocation_id": invocation_id,
            "outcome": "SUCCESS",
            "child_return_code": 0,
            "stage": "SUCCESS",
            "connection_count": 1,
            "query_count": 1,
            "schema_valid_result_count": 1,
            **result,
        }
        encoded = json.dumps(
            payload,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(encoded) > MAX_STDOUT_BYTES:
            return 46
        writer(encoded)
    except BaseException:
        return 46
    return 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path) -> dict[str, object]:
    """Build the recursive manifest, excluding only the exact root manifest."""
    root = root.resolve()
    files: list[dict[str, object]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "manifest.json":
            continue
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "root_manifest_exclusion": "manifest.json",
        "file_count": len(files),
        "files": files,
    }


def audit_manifest(root: Path, manifest: Mapping[str, object]) -> dict[str, int]:
    expected_items = manifest.get("files")
    if not isinstance(expected_items, list):
        raise ValueError("invalid manifest")
    expected = {
        str(item["path"]): item
        for item in expected_items
        if isinstance(item, dict) and "path" in item
    }
    actual_manifest = build_manifest(root)
    actual_items = actual_manifest["files"]
    assert isinstance(actual_items, list)
    actual = {
        str(item["path"]): item
        for item in actual_items
        if isinstance(item, dict) and "path" in item
    }
    shared = expected.keys() & actual.keys()
    return {
        "missing": len(expected.keys() - actual.keys()),
        "extra": len(actual.keys() - expected.keys()),
        "byte_mismatch": sum(expected[p].get("bytes") != actual[p].get("bytes") for p in shared),
        "hash_mismatch": sum(expected[p].get("sha256") != actual[p].get("sha256") for p in shared),
    }


def audit_json_documents(root: Path) -> dict[str, int]:
    files = documents = invalid = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix not in {".json", ".jsonl"}:
            continue
        files += 1
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                documents += 1
            else:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        json.loads(line)
                        documents += 1
        except (OSError, UnicodeError, json.JSONDecodeError):
            invalid += 1
    return {"files": files, "documents": documents, "invalid": invalid}


def credential_scan_bytes(data: bytes, path: str) -> list[dict[str, object]]:
    """Return only finding type, path, and count; never return matched values."""
    findings: list[dict[str, object]] = []
    for finding_type, pattern in (
        ("URL_USERINFO", _URL_USERINFO),
        ("SENSITIVE_ASSIGNMENT", _SENSITIVE_ASSIGNMENT),
    ):
        count = len(pattern.findall(data))
        if count:
            findings.append({"finding_type": finding_type, "path": path, "count": count})
    return findings


def credential_scan_tree(root: Path) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    scanned = 0
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        scanned += 1
        findings.extend(credential_scan_bytes(path.read_bytes(), path.relative_to(root).as_posix()))
    return {"scanned_files": scanned, "finding_count": len(findings), "findings": findings}


def _exclusive_rename_directory(source: Path, destination: Path) -> None:
    """Atomically rename a directory while refusing to replace any destination."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        renamex = libc.renamex_np
        renamex.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex.restype = ctypes.c_int
        result = renamex(os.fsencode(source), os.fsencode(destination), 0x00000004)
        if result == 0:
            return
        error = ctypes.get_errno()
        if error in {errno.EEXIST, errno.ENOTEMPTY}:
            raise FileExistsError(destination)
        raise OSError(error, os.strerror(error), destination)
    if destination.exists():
        raise FileExistsError(destination)
    os.rename(source, destination)


class EvidencePublisher:
    """No-clobber publisher for one staged report and one staged evidence tree."""

    def __init__(self, final_report: Path, final_evidence: Path) -> None:
        self.final_report = final_report
        self.final_evidence = final_evidence

    def publish(
        self,
        staged_report: Path,
        staged_evidence: Path,
        *,
        before_publish: Callable[[], object] | None = None,
    ) -> None:
        if self.final_report.exists() or self.final_evidence.exists():
            raise FileExistsError("formal output already exists")
        if before_publish is not None:
            before_publish()
        if self.final_report.exists() or self.final_evidence.exists():
            raise FileExistsError("formal output appeared during publish")

        self.final_report.parent.mkdir(parents=True, exist_ok=True)
        os.link(staged_report, self.final_report)
        try:
            _exclusive_rename_directory(staged_evidence, self.final_evidence)
        except BaseException:
            try:
                if self.final_report.samefile(staged_report):
                    self.final_report.unlink()
            except OSError:
                pass
            raise


def write_json_exclusive(path: Path, value: Mapping[str, object]) -> None:
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    with path.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def _run_parent_cli(argv: list[str]) -> int:
    if len(argv) != 3 or argv[0] != "--parent" or argv[1] != "--output":
        return 2
    output = Path(argv[2])
    invocation_id = output.stem.removeprefix("proof-")
    try:
        result = run_parent(invocation_id)
        write_json_exclusive(output, result)
    except BaseException:
        return 2
    return int(result["parent_return_code"])


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 2 and args[0] == "--child":
        return child_main(args[1])
    return _run_parent_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
