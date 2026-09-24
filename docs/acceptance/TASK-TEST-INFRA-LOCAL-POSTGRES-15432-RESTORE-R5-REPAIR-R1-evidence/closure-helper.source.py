#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


REPAIR_TASK_ID = "TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5-REPAIR-R1"
ORIGINAL_TASK_ID = "TASK-TEST-INFRA-LOCAL-POSTGRES-15432-RESTORE-R5"
REPAIR_ID = REPAIR_TASK_ID
RECEIPT_SCHEMA_VERSION = 1
FORMAL_ARTIFACT_NAMES = (
    "stability-invocation.json",
    "stability-timeline.jsonl",
    "stability-completion.json",
    "stability-process-outcome.json",
    "stability-failure.json",
)
REQUIRED_GATE_TYPES = (
    "output-path",
    "git-baseline",
    "fixed-input-hash",
    "protected-untracked-before",
    "r5-helper-source-import-hash",
    "repair-helper-compile",
    "repair-helper-self-test",
    "repair-helper-dry-run",
    "no-bytecode",
    "docker-context",
    "docker-identity",
    "pg-isready",
    "postgres-read-only-preflight",
    "formal-artifact-path-absence",
)


class NoClobberPrimitiveError(OSError):
    pass


class GateValidationError(RuntimeError):
    pass


class BytecodeConsistencyError(RuntimeError):
    pass


class ClosureStateError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("UTC timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def publish_bytes_no_clobber(
    path: Path,
    data: bytes,
    *,
    mode: int = 0o600,
    before_link: Callable[[Path, Path], None] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}-{uuid.uuid4().hex}")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    linked = False
    try:
        os.fchmod(descriptor, mode)
        _write_all(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        if before_link is not None:
            before_link(temporary, path)
        try:
            os.link(temporary, path, follow_symlinks=False)
            linked = True
        except FileExistsError:
            raise
        except OSError as exc:
            raise NoClobberPrimitiveError("same-filesystem hard-link publication unavailable") from exc
    finally:
        try:
            temporary.unlink()
        finally:
            fsync_directory(path.parent)
    if not linked:
        raise NoClobberPrimitiveError("publication did not create final path")


def publish_json_no_clobber(path: Path, payload: Mapping[str, Any]) -> None:
    publish_bytes_no_clobber(path, pretty_json_bytes(dict(payload)))


def file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "relative_path": path.relative_to(root).as_posix(),
        "byte_count": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_receipt(
    path: Path,
    *,
    receipt_type: str,
    invocation_id: str,
    started_at_utc: str,
    completed_at_utc: str,
    monotonic_started: float,
    monotonic_finished: float,
    exit_code: int,
    criteria_satisfied: bool,
    semantic_command: str,
    relevant_result: Mapping[str, Any],
    source_config_sha256: str,
    failure_classification: str = "NONE",
    task_id: str = REPAIR_TASK_ID,
) -> dict[str, Any]:
    payload = {
        "task_id": task_id,
        "original_task_id": ORIGINAL_TASK_ID,
        "repair_id": REPAIR_ID,
        "repair_invocation_id": invocation_id,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_type": receipt_type,
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "monotonic_started": monotonic_started,
        "monotonic_finished": monotonic_finished,
        "exit_code": exit_code,
        "criteria_satisfied": criteria_satisfied,
        "semantic_command": semantic_command,
        "relevant_result": dict(relevant_result),
        "source_config_sha256": source_config_sha256,
        "credential_safe_failure_classification": failure_classification,
    }
    publish_json_no_clobber(path, payload)
    return payload


def scan_bytecode(root: Path) -> dict[str, Any]:
    pyc = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.pyc"))
    caches = sorted(path.relative_to(root).as_posix() for path in root.rglob("__pycache__") if path.is_dir())
    return {
        "bytecode_file_count": len(pyc),
        "pycache_directory_count": len(caches),
        "bytecode_files": pyc,
        "pycache_directories": caches,
    }


def assert_no_bytecode(root: Path) -> dict[str, Any]:
    result = scan_bytecode(root)
    if result["bytecode_file_count"] or result["pycache_directory_count"]:
        raise BytecodeConsistencyError("bytecode exists; audit does not delete it")
    return result


def bytecode_consistency(
    compile_receipt: Mapping[str, Any], root: Path, planned_relative_paths: Iterable[str]
) -> dict[str, Any]:
    actual = assert_no_bytecode(root)
    reported = compile_receipt.get("relevant_result", {})
    planned = list(planned_relative_paths)
    planned_bad = sorted(
        path for path in planned if path.endswith(".pyc") or "__pycache__" in Path(path).parts
    )
    checks = {
        "compile_receipt_satisfied": compile_receipt.get("criteria_satisfied") is True,
        "compile_receipt_bytecode_zero": reported.get("bytecode_file_count") == 0,
        "compile_receipt_pycache_zero": reported.get("pycache_directory_count") == 0,
        "actual_bytecode_zero": actual["bytecode_file_count"] == 0,
        "actual_pycache_zero": actual["pycache_directory_count"] == 0,
        "planned_manifest_has_no_bytecode": not planned_bad,
    }
    if not all(checks.values()):
        raise BytecodeConsistencyError("compile receipt, actual directory, or planned set disagrees")
    return {"criteria_satisfied": True, "checks": checks, "planned_bytecode_paths": planned_bad, **actual}


def build_gate_index(
    evidence_dir: Path,
    receipt_paths: Mapping[str, Path],
    *,
    invocation_id: str,
    bytecode_count: int,
    formal_paths: Iterable[Path],
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    if set(receipt_paths) != set(REQUIRED_GATE_TYPES):
        raise GateValidationError("required receipt set mismatch")
    generated = generated_at_utc or utc_now()
    generated_time = parse_utc(generated)
    records: list[dict[str, Any]] = []
    for receipt_type in REQUIRED_GATE_TYPES:
        path = receipt_paths[receipt_type]
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("receipt_type") != receipt_type:
            raise GateValidationError("receipt type mismatch")
        if payload.get("criteria_satisfied") is not True:
            raise GateValidationError("failed receipt")
        if payload.get("repair_invocation_id") != invocation_id:
            raise GateValidationError("receipt invocation mismatch")
        if payload.get("task_id") != REPAIR_TASK_ID or payload.get("repair_id") != REPAIR_ID:
            raise GateValidationError("stale or foreign receipt")
        if parse_utc(str(payload["completed_at_utc"])) >= generated_time:
            raise GateValidationError("receipt not completed before index")
        record = file_record(path, evidence_dir)
        record.update(
            {
                "receipt_type": receipt_type,
                "completed_at_utc": payload["completed_at_utc"],
                "criteria_satisfied": True,
            }
        )
        records.append(record)
    existing_formal = sorted(path.name for path in formal_paths if path.exists() or path.is_symlink())
    if existing_formal:
        raise GateValidationError("formal path already exists")
    if bytecode_count != 0:
        raise GateValidationError("bytecode count nonzero")
    return {
        "schema_version": 1,
        "task_id": REPAIR_TASK_ID,
        "original_task_id": ORIGINAL_TASK_ID,
        "repair_id": REPAIR_ID,
        "repair_invocation_id": invocation_id,
        "generated_at_utc": generated,
        "formal_window_started": False,
        "all_receipts_criteria_satisfied": True,
        "bytecode_count": bytecode_count,
        "formal_artifact_paths_absent": True,
        "required_receipt_types": list(REQUIRED_GATE_TYPES),
        "receipts": records,
    }


def validate_gate_index(
    index_path: Path,
    evidence_dir: Path,
    *,
    invocation_id: str,
    formal_invocation_started_at_utc: str | None = None,
) -> dict[str, Any]:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateValidationError("gate index unreadable") from exc
    if index.get("task_id") != REPAIR_TASK_ID or index.get("repair_id") != REPAIR_ID:
        raise GateValidationError("gate index task mismatch")
    if index.get("repair_invocation_id") != invocation_id:
        raise GateValidationError("gate index invocation mismatch")
    if index.get("formal_window_started") is not False:
        raise GateValidationError("index does not assert pre-window state")
    if index.get("bytecode_count") != 0 or index.get("formal_artifact_paths_absent") is not True:
        raise GateValidationError("index prerequisite summary invalid")
    entries = index.get("receipts")
    if not isinstance(entries, list):
        raise GateValidationError("receipt index is not a list")
    types = [entry.get("receipt_type") for entry in entries if isinstance(entry, dict)]
    if sorted(types) != sorted(REQUIRED_GATE_TYPES) or len(types) != len(REQUIRED_GATE_TYPES):
        raise GateValidationError("index missing or duplicating a required receipt")
    index_time = parse_utc(str(index["generated_at_utc"]))
    for entry in entries:
        path = evidence_dir / str(entry["relative_path"])
        if not path.is_file() or path.is_symlink():
            raise GateValidationError("receipt file missing or not regular")
        actual = file_record(path, evidence_dir)
        if actual["byte_count"] != entry.get("byte_count") or actual["sha256"] != entry.get("sha256"):
            raise GateValidationError("receipt hash or size mismatch")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt.get("criteria_satisfied") is not True or entry.get("criteria_satisfied") is not True:
            raise GateValidationError("failed receipt")
        if receipt.get("receipt_type") != entry.get("receipt_type"):
            raise GateValidationError("receipt type mismatch")
        if receipt.get("repair_invocation_id") != invocation_id:
            raise GateValidationError("receipt invocation mismatch")
        if receipt.get("task_id") != REPAIR_TASK_ID or receipt.get("repair_id") != REPAIR_ID:
            raise GateValidationError("stale or foreign receipt")
        completed = parse_utc(str(receipt["completed_at_utc"]))
        if completed >= index_time or str(receipt["completed_at_utc"]) != entry.get("completed_at_utc"):
            raise GateValidationError("receipt timestamp does not precede index")
    if formal_invocation_started_at_utc is not None:
        if index_time >= parse_utc(formal_invocation_started_at_utc):
            raise GateValidationError("gate index does not precede formal invocation")
    existing = [name for name in FORMAL_ARTIFACT_NAMES if (evidence_dir / name).exists() or (evidence_dir / name).is_symlink()]
    if existing:
        raise GateValidationError("formal artifact path exists")
    digest = sha256_file(index_path)
    return {
        "criteria_satisfied": True,
        "repair_invocation_id": invocation_id,
        "prewindow_gate_index_sha256": digest,
        "receipt_count": len(entries),
        "all_receipts_before_index": True,
        "index_before_formal_invocation": formal_invocation_started_at_utc is not None,
        "formal_artifact_paths_absent": True,
    }


def _path_type_and_bytes(path: Path) -> tuple[str, bytes]:
    if path.is_symlink():
        data = os.readlink(path).encode("utf-8", errors="surrogateescape")
        return "symlink", data
    if path.is_file():
        return "regular", path.read_bytes()
    return "other", b""


def snapshot_untracked(repo: Path, excluded_prefixes: Iterable[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--others", "--exclude-standard"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    excluded = tuple(prefix.rstrip("/") for prefix in excluded_prefixes)
    paths = sorted(item.decode("utf-8", errors="surrogateescape") for item in completed.stdout.split(b"\0") if item)
    entries: list[dict[str, Any]] = []
    for relative in paths:
        if any(relative == prefix or relative.startswith(prefix + "/") for prefix in excluded):
            continue
        path = repo / relative
        file_type, data = _path_type_and_bytes(path)
        entries.append(
            {
                "relative_path": relative,
                "file_type": file_type,
                "byte_count": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    canonical = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"entry_count": len(entries), "entries": entries, "canonical_sha256": sha256_bytes(canonical)}


def compare_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    same = before.get("entries") == after.get("entries")
    return {
        "criteria_satisfied": same,
        "before_entry_count": before.get("entry_count"),
        "after_entry_count": after.get("entry_count"),
        "before_canonical_sha256": before.get("canonical_sha256"),
        "after_canonical_sha256": after.get("canonical_sha256"),
        "path_type_byte_sha256_exact": same,
    }


def evidence_file_records(root: Path, *, exclude: Iterable[str] = ()) -> list[dict[str, Any]]:
    excluded = set(exclude)
    records: list[dict[str, Any]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file() or item.is_symlink()), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        if path.is_symlink():
            data = os.readlink(path).encode("utf-8", errors="surrogateescape")
            records.append({"relative_path": relative, "file_type": "symlink", "byte_count": len(data), "sha256": sha256_bytes(data)})
        else:
            records.append({"relative_path": relative, "file_type": "regular", "byte_count": path.stat().st_size, "sha256": sha256_file(path)})
    return records


class ClosureStateMachine:
    def __init__(self, evidence_dir: Path, *, payloads_final: bool) -> None:
        self.evidence_dir = evidence_dir
        self.state = "PAYLOADS_FINAL" if payloads_final else "OPEN"
        self.credential_path = evidence_dir / "credential-scan.json"
        self.audit_path = evidence_dir / "json-parse-audit.json"
        self.manifest_path = evidence_dir / "manifest.json"

    def _require(self, expected: str) -> None:
        if self.state != expected:
            raise ClosureStateError(f"closure state {self.state}, expected {expected}")

    def finalize_credential_scan(self, report_path: Path, *, secret: str | None) -> Path:
        self._require("PAYLOADS_FINAL")
        excluded = {self.credential_path.name, self.audit_path.name, self.manifest_path.name}
        paths = [report_path] + [
            self.evidence_dir / record["relative_path"]
            for record in evidence_file_records(self.evidence_dir, exclude=excluded)
            if record["file_type"] == "regular"
        ]
        url_pattern = re.compile(rb"postgres(?:ql)?://[^\s/:]+:[^\s@]+@", re.IGNORECASE)
        files: list[dict[str, Any]] = []
        finding_count = 0
        for path in paths:
            data = path.read_bytes()
            categories: list[str] = []
            if url_pattern.search(data):
                categories.append("DATABASE_URL_WITH_USERINFO")
            if secret is not None and secret.encode("utf-8") in data:
                categories.append("PROCESS_CREDENTIAL_VALUE")
            finding_count += len(categories)
            files.append(
                {
                    "path": path.name if path == report_path else path.relative_to(self.evidence_dir).as_posix(),
                    "scope": "execution-report" if path == report_path else "evidence",
                    "byte_count": len(data),
                    "sha256": sha256_bytes(data),
                    "finding_categories": categories,
                }
            )
        payload = {
            "schema_version": 1,
            "task_id": REPAIR_TASK_ID,
            "generated_at_utc": utc_now(),
            "criteria_satisfied": finding_count == 0,
            "finding_count": finding_count,
            "files_scanned": files,
            "excluded_not_yet_generated": sorted(excluded),
            "raw_matches_retained": False,
        }
        publish_json_no_clobber(self.credential_path, payload)
        if finding_count:
            raise ClosureStateError("credential scan found unsafe payload")
        self.state = "CREDENTIAL_SCAN_FINAL"
        return self.credential_path

    def accept_json_parse_audit(self, path: Path, credential_path: Path) -> None:
        self._require("CREDENTIAL_SCAN_FINAL")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("credential_scan_sha256") != sha256_file(credential_path):
            raise ClosureStateError("JSON audit does not bind final credential scan")
        self.audit_path = path
        self.state = "JSON_PARSE_AUDIT_FINAL"

    def finalize_json_parse_audit(self) -> Path:
        self._require("CREDENTIAL_SCAN_FINAL")
        excluded = {self.audit_path.name, self.manifest_path.name}
        records: list[dict[str, Any]] = []
        for path in sorted(self.evidence_dir.rglob("*"), key=lambda item: item.relative_to(self.evidence_dir).as_posix()):
            if not path.is_file() or path.name in excluded and path.parent == self.evidence_dir:
                continue
            relative = path.relative_to(self.evidence_dir).as_posix()
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                records.append({**file_record(path, self.evidence_dir), "type": "json", "parsed": True})
            elif path.suffix == ".jsonl":
                lines = path.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    json.loads(line)
                records.append({**file_record(path, self.evidence_dir), "type": "jsonl", "parsed": True, "line_count": len(lines)})
        credential_hash = sha256_file(self.credential_path)
        if not any(record["relative_path"] == self.credential_path.name and record["sha256"] == credential_hash for record in records):
            raise ClosureStateError("final credential scan not parsed")
        payload = {
            "schema_version": 1,
            "task_id": REPAIR_TASK_ID,
            "generated_at_utc": utc_now(),
            "criteria_satisfied": True,
            "parsed_files": records,
            "credential_scan_byte_count": self.credential_path.stat().st_size,
            "credential_scan_sha256": credential_hash,
            "excluded_not_yet_generated": sorted(excluded),
            "raw_content_retained": False,
        }
        publish_json_no_clobber(self.audit_path, payload)
        self.state = "JSON_PARSE_AUDIT_FINAL"
        return self.audit_path

    def finalize_manifest(self) -> Path:
        self._require("JSON_PARSE_AUDIT_FINAL")
        records = evidence_file_records(self.evidence_dir, exclude={self.manifest_path.name})
        paths = {record["relative_path"] for record in records}
        if self.credential_path.name not in paths or self.audit_path.name not in paths:
            raise ClosureStateError("manifest input set lacks final closure artifacts")
        generated = utc_now()
        audit_generated = parse_utc(json.loads(self.audit_path.read_text(encoding="utf-8"))["generated_at_utc"])
        while parse_utc(generated) <= audit_generated:
            generated = utc_now()
        payload = {
            "schema_version": 1,
            "task_id": REPAIR_TASK_ID,
            "generated_at_utc": generated,
            "root": str(self.evidence_dir),
            "self_excluded": True,
            "declared_file_count": len(records),
            "files": records,
        }
        publish_json_no_clobber(self.manifest_path, payload)
        self.state = "MANIFEST_FINAL"
        return self.manifest_path


def rebuild_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared = {record["relative_path"]: record for record in manifest["files"]}
    actual_records = evidence_file_records(root, exclude={manifest_path.relative_to(root).as_posix()})
    actual = {record["relative_path"]: record for record in actual_records}
    missing = sorted(set(declared) - set(actual))
    extra = sorted(set(actual) - set(declared))
    byte_mismatch = sorted(path for path in set(declared) & set(actual) if declared[path]["byte_count"] != actual[path]["byte_count"])
    hash_mismatch = sorted(path for path in set(declared) & set(actual) if declared[path]["sha256"] != actual[path]["sha256"])
    type_mismatch = sorted(path for path in set(declared) & set(actual) if declared[path].get("file_type") != actual[path].get("file_type"))
    return {
        "criteria_satisfied": not (missing or extra or byte_mismatch or hash_mismatch or type_mismatch),
        "declared_file_count": len(declared),
        "actual_file_count": len(actual),
        "missing": missing,
        "extra": extra,
        "byte_count_mismatch": byte_mismatch,
        "hash_mismatch": hash_mismatch,
        "file_type_mismatch": type_mismatch,
    }
