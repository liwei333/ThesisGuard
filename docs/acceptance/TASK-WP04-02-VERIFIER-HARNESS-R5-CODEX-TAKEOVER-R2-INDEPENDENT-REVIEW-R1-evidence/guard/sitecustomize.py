"""Fail-closed socket guard for independent R2 collect-only acceptance."""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path

_LOG = Path(
    "/private/tmp/tg-wp04-02-r5-r2-independent-r1-20260921/socket-attempts.jsonl"
)


def _block(address: object) -> None:
    with _LOG.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps({"utc": datetime.now(UTC).isoformat(), "address": repr(address)})
            + "\n"
        )
    raise RuntimeError("socket connection blocked by independent collect-only guard")


def _guarded_connect(self: socket.socket, address: object) -> None:
    del self
    _block(address)


def _guarded_connect_ex(self: socket.socket, address: object) -> int:
    del self
    _block(address)
    return 1


def _guarded_create_connection(
    address: object, *args: object, **kwargs: object
) -> None:
    del args, kwargs
    _block(address)


socket.socket.connect = _guarded_connect
socket.socket.connect_ex = _guarded_connect_ex
socket.create_connection = _guarded_create_connection
