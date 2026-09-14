"""Event definitions for ThesisGuard.

Events are published via Redis Streams. This module defines the event names
and helper functions for publishing events.

In V1, events are internal to the modular monolith.
Future WPs will use these for cross-module communication.

事件系统是模块间解耦的异步通信机制。当前 V1 仅用于内部触发
（如 instrument.created 触发后续初始化），后续 WP 将扩展为
跨模块状态同步。事件 payload 序列化为 JSON 字符串存储。
"""

import json
from datetime import UTC, datetime
from typing import Any

# Event names - grouped by domain
# 事件命名遵循 domain.action 格式，便于 stream 消费者按前缀过滤
EVENTS = {
    # Instrument
    "instrument.created": "instrument.created",
    "instrument.updated": "instrument.updated",
    # Watchlist
    "watchlist.added": "watchlist.added",
    "watchlist.removed": "watchlist.removed",
    "watchlist.classified": "watchlist.classified",
    # Research
    "research.requested": "research.requested",
    "research.completed": "research.completed",
    "research.module_updated": "research.module_updated",
    # Evidence
    "evidence.created": "evidence.created",
    # Thesis
    "thesis.created": "thesis.created",
    "thesis.updated": "thesis.updated",
    "thesis.invalidated": "thesis.invalidated",
    # Market
    "market.regime_changed": "market.regime_changed",
    # Worker
    "worker.task_completed": "worker.task_completed",
}


def make_event(
    event_type: str,
    data: dict[str, Any],
    event_id: str | None = None,
) -> dict[str, Any]:
    """Create a standardized event envelope."""
    return {
        "event_type": event_type,
        "event_id": event_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "payload": json.dumps(data),
    }


async def publish_event(
    event_type: str,
    data: dict[str, Any],
    stream: str = "thesisguard:events",
) -> str:
    """Publish an event to Redis Streams.

    Returns the stream entry ID.
    每次发布都新建连接并在 finally 中关闭，保证异常场景下不泄漏连接。
    高频场景后续可优化为连接池复用。
    """
    import redis.asyncio as aioredis
    from backend.common.config import settings

    r = aioredis.Redis.from_url(
        settings.redis_url_resolved,
        decode_responses=True,
    )
    try:
        event = make_event(event_type, data)
        entry_id = await r.xadd(stream, event)
        return str(entry_id)
    finally:
        await r.close()
