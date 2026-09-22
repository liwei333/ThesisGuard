"""Fail closed if collect-only code attempts any Python socket connection."""

from __future__ import annotations

import json
import os
import socket
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_ORIGINAL_CONNECT = socket.socket.connect


def _deny_connect(sock: socket.socket, address: Any) -> Any:
    log_path = Path(os.environ["TG_SOCKET_GUARD_LOG"])
    record = {
        "time_utc": datetime.now(UTC).isoformat(),
        "address_repr": repr(address),
    }
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    raise RuntimeError("socket connection denied during collect-only verification")


socket.socket.connect = _deny_connect
