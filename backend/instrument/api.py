"""Instrument API endpoints."""

from backend.common.db.session import get_db
from backend.instrument.schemas import InstrumentRead
from backend.instrument.services import get_instrument_by_symbol, search_instruments
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/instruments", tags=["instrument"])


@router.get("/search", response_model=list[InstrumentRead])
async def search_instrument_endpoint(
    query: str = Query(min_length=1, max_length=128),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[InstrumentRead]:
    """Search instruments by symbol, name, alias, or tag."""
    instruments = await search_instruments(db, query=query, limit=limit)
    return [InstrumentRead.model_validate(item) for item in instruments]


@router.get("/{symbol}", response_model=InstrumentRead)
async def get_instrument_endpoint(
    symbol: str,
    db: AsyncSession = Depends(get_db),
) -> InstrumentRead:
    """Get an instrument by symbol."""
    instrument = await get_instrument_by_symbol(db, symbol.upper())
    if instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return InstrumentRead.model_validate(instrument)
