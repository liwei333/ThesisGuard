"""Watchlist API endpoints."""

from backend.common.db.session import get_db
from backend.watchlist.schemas import (
    WatchlistAddRequest,
    WatchlistItemRead,
    WatchlistUpdateRequest,
)
from backend.watchlist.services import (
    add_to_watchlist,
    get_watchlist_item,
    list_watchlist,
    remove_watchlist_item,
    update_watchlist_item,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemRead])
async def list_watchlist_endpoint(
    classification: str | None = Query(default=None, max_length=32),
    db: AsyncSession = Depends(get_db),
) -> list[WatchlistItemRead]:
    """List watchlist items."""
    items = await list_watchlist(db, classification=classification)
    return [WatchlistItemRead.model_validate(item) for item in items]


@router.post("", response_model=WatchlistItemRead, status_code=status.HTTP_201_CREATED)
async def add_watchlist_endpoint(
    payload: WatchlistAddRequest,
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemRead:
    """Add an instrument to watchlist and classify it."""
    try:
        item = await add_to_watchlist(db, query=payload.query, notes=payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return WatchlistItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=WatchlistItemRead)
async def update_watchlist_endpoint(
    item_id: str,
    payload: WatchlistUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemRead:
    """Update a watchlist item."""
    item = await get_watchlist_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    updated = await update_watchlist_item(
        db,
        item,
        classification=payload.classification,
        research_status=payload.research_status,
        agent_action=payload.agent_action,
        notes=payload.notes,
    )
    return WatchlistItemRead.model_validate(updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist_endpoint(
    item_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a watchlist item."""
    item = await get_watchlist_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    await remove_watchlist_item(db, item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
