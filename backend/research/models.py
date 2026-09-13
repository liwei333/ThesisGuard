"""Research Package SQLAlchemy models."""

from datetime import UTC, datetime

from backend.common.db.session import Base
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

RESEARCH_MODULE_TYPES: tuple[str, ...] = (
    "COMPANY",
    "BUSINESS",
    "INDUSTRY",
    "ORDER",
    "FINANCIAL",
    "EXPECTATION",
    "VALUATION",
    "RISK",
    "CATALYST",
    "COMPETITOR",
    "MANAGEMENT",
)

PACKAGE_TRIGGER_TYPES: tuple[str, ...] = ("INITIAL_FULL", "INCREMENTAL_REFRESH")
PACKAGE_STATUSES: tuple[str, ...] = ("PENDING", "BUILDING", "READY", "FAILED")
MODULE_STATUSES: tuple[str, ...] = ("UNVERIFIED", "PENDING", "REFRESHING", "READY", "FAILED")


def _quoted_values(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class ResearchPackage(Base):
    """Append-only research package version for one instrument."""

    __tablename__ = "research_package"
    __table_args__ = (
        UniqueConstraint("instrument_id", "version", name="uq_research_package_instrument_version"),
        UniqueConstraint(
            "instrument_id",
            "idempotency_key",
            name="uq_research_package_instrument_idempotency_key",
        ),
        CheckConstraint("version >= 1", name="ck_research_package_version_positive"),
        CheckConstraint(
            f"trigger_type IN ({_quoted_values(PACKAGE_TRIGGER_TYPES)})",
            name="ck_research_package_trigger_type",
        ),
        CheckConstraint(
            f"status IN ({_quoted_values(PACKAGE_STATUSES)})",
            name="ck_research_package_status",
        ),
        CheckConstraint(
            "(version = 1 AND previous_version_id IS NULL) OR "
            "(version > 1 AND previous_version_id IS NOT NULL)",
            name="ck_research_package_lineage",
        ),
        Index("ix_research_package_instrument_version", "instrument_id", "version"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("research_package.id", ondelete="RESTRICT"),
        nullable=True,
    )
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expected_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    instrument: Mapped[Instrument] = relationship()
    previous_version: Mapped["ResearchPackage | None"] = relationship(
        remote_side=[id],
        foreign_keys=[previous_version_id],
    )
    modules: Mapped[list["ResearchModule"]] = relationship(
        back_populates="research_package",
        cascade="all, delete-orphan",
        order_by="ResearchModule.module_type",
    )


class ResearchModule(Base):
    """Module snapshot that belongs to exactly one research package version."""

    __tablename__ = "research_module"
    __table_args__ = (
        UniqueConstraint(
            "research_package_id",
            "module_type",
            name="uq_research_module_package_type",
        ),
        CheckConstraint("module_version >= 1", name="ck_research_module_version_positive"),
        CheckConstraint(
            f"module_type IN ({_quoted_values(RESEARCH_MODULE_TYPES)})",
            name="ck_research_module_type",
        ),
        CheckConstraint(
            f"status IN ({_quoted_values(MODULE_STATUSES)})",
            name="ck_research_module_status",
        ),
        Index("ix_research_module_package_type", "research_package_id", "module_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    research_package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("research_package.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    origin_module_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("research_module.id", ondelete="SET NULL"),
        nullable=True,
    )
    module_type: Mapped[str] = mapped_column(String(32), nullable=False)
    module_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UNVERIFIED")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    stale_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    research_package: Mapped[ResearchPackage] = relationship(back_populates="modules")
    origin_module: Mapped["ResearchModule | None"] = relationship(
        remote_side=[id],
        foreign_keys=[origin_module_id],
    )
