"""Event definitions for ThesisGuard.

Events are published via Redis Streams. This module defines the event names
and helper functions for publishing events.

In V1, events are internal to the modular monolith.
Future WPs will use these for cross-module communication.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timezone
import json

from backend.common.redis_client import redis_client


# Event names - grouped by domain
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
    data: Dict[str, Any],
    event_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized event envelope."""
    return {
        "event_type": event_type,
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": json.dumps(data),
    }


async def publish_event(
    event_type: str,
    data: Dict[str, Any],
    stream: str = "thesisguard:events",
) -> str:
    """Publish an event to Redis Streams.

    Returns the stream entry ID.
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
        return entry_id
    finally:
        await r.close()
