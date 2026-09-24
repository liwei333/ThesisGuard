from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

import asyncpg
from sqlalchemy.engine import make_url

from tests.test_evidence_services import DEFAULT_ADMIN_DATABASE_URL


CATALOG_SQL = """SELECT d.datname, d.oid::bigint AS oid, r.rolname AS owner,
    d.datdba::bigint AS owner_oid
FROM pg_database d JOIN pg_roles r ON r.oid = d.datdba ORDER BY d.datname"""


def canonical_hash(rows: list[dict[str, object]]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


async def main() -> int:
    nonce = os.environ["TG_R5_OBSERVER_NONCE"]
    timeline_path = Path(os.environ["TG_R5_OBSERVER_TIMELINE"])
    ready_path = Path(os.environ["TG_R5_OBSERVER_READY"])
    stop_path = Path(os.environ["TG_R5_OBSERVER_STOP"])
    baseline_path = Path(os.environ["TG_R5_BASELINE_CATALOG"])
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_hash = baseline["canonical_sha256"]
    baseline_count = baseline["count"]
    url = make_url(DEFAULT_ADMIN_DATABASE_URL)
    connection = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database=url.database,
        server_settings={"application_name": f"tg_r5_runtime_{nonce}"},
    )
    started = monotonic()
    sample = 0
    try:
        while True:
            sample += 1
            rows = [dict(row) for row in await connection.fetch(CATALOG_SQL)]
            record = {
                "sample": sample,
                "utc_timestamp": utc_now(),
                "elapsed_seconds": round(monotonic() - started, 3),
                "catalog_count": len(rows),
                "catalog_sha256": canonical_hash(rows),
                "identities": rows,
            }
            with timeline_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            if sample == 1:
                ready = {
                    "ready": True,
                    "observer_nonce": nonce,
                    "first_sample_count": len(rows),
                    "first_sample_sha256": record["catalog_sha256"],
                    "baseline_equal": len(rows) == baseline_count
                    and record["catalog_sha256"] == baseline_hash,
                }
                ready_path.write_text(
                    json.dumps(ready, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
            if stop_path.exists():
                break
            target = started + sample * 2
            await asyncio.sleep(max(0, target - monotonic()))
    finally:
        await connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
