"""Instrument API schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InstrumentRead(BaseModel):
    """Instrument response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    market: str
    currency: str
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class InstrumentSearchParams(BaseModel):
    """Validated instrument search parameters."""

    query: str = Field(min_length=1, max_length=128)
    limit: int = Field(default=10, ge=1, le=50)
