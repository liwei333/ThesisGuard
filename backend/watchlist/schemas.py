"""Watchlist API schemas."""

from datetime import datetime

from backend.instrument.schemas import InstrumentRead
from pydantic import BaseModel, ConfigDict, Field


class WatchlistAddRequest(BaseModel):
    """Request to add an instrument to the watchlist."""

    query: str = Field(min_length=1, max_length=128)
    notes: str | None = Field(default=None, max_length=2000)


class WatchlistUpdateRequest(BaseModel):
    """Request to update a watchlist item."""

    classification: str | None = Field(default=None, max_length=32)
    research_status: str | None = Field(default=None, max_length=32)
    agent_action: str | None = Field(default=None, max_length=128)
    notes: str | None = Field(default=None, max_length=2000)


class WatchlistItemRead(BaseModel):
    """Watchlist item response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    instrument_id: str
    instrument: InstrumentRead
    classification: str
    classification_confidence: int
    classification_reason: str
    research_status: str
    research_score: int | None = None
    thesis_summary: str | None = None
    agent_action: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
