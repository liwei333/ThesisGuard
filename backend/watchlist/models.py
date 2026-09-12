"""Watchlist SQLAlchemy models."""

from datetime import UTC, datetime

from backend.common.db.session import Base
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WatchlistItem(Base):
    """A user-tracked instrument with classification state."""

    __tablename__ = "watchlist_item"
    __table_args__ = (
        UniqueConstraint("instrument_id", name="uq_watchlist_instrument"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    classification_confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    classification_reason: Mapped[str] = mapped_column(Text, nullable=False)
    research_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    research_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thesis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_action: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    instrument: Mapped[Instrument] = relationship(lazy="joined")
