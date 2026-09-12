"""Instrument SQLAlchemy models."""

from datetime import UTC, datetime
from uuid import uuid4

from backend.common.db.session import Base
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


def uuid_str() -> str:
    """Generate a string UUID for database primary keys."""
    return str(uuid4())


class Instrument(Base):
    """Tradable or trackable instrument."""

    __tablename__ = "instrument"
    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_instrument_symbol_exchange"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    instrument_type: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(32), nullable=False, default="CN")
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="CNY")
    sector: Mapped[str | None] = mapped_column(String(64), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
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

    aliases: Mapped[list["InstrumentAlias"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["InstrumentTag"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan",
    )


class InstrumentAlias(Base):
    """Search alias for an instrument."""

    __tablename__ = "instrument_alias"
    __table_args__ = (
        UniqueConstraint("instrument_id", "alias", name="uq_instrument_alias"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alias: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    alias_type: Mapped[str] = mapped_column(String(32), nullable=False, default="NAME")

    instrument: Mapped[Instrument] = relationship(back_populates="aliases")


class InstrumentTag(Base):
    """Lightweight domain tag attached to an instrument."""

    __tablename__ = "instrument_tag"
    __table_args__ = (
        UniqueConstraint("instrument_id", "tag", name="uq_instrument_tag"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    instrument: Mapped[Instrument] = relationship(back_populates="tags")


class InstrumentRelation(Base):
    """Directed relation between two instruments."""

    __tablename__ = "instrument_relation"
    __table_args__ = (
        UniqueConstraint(
            "source_instrument_id",
            "target_instrument_id",
            "relation_type",
            name="uq_instrument_relation",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    source_instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
