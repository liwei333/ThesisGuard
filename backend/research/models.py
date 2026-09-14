"""Research Package SQLAlchemy models.

研究包模型是系统的核心数据结构之一，遵循"不可变历史"原则：
- 每个 ResearchPackage 是一个追加式版本，创建后永不修改
- 增量刷新（INCREMENTAL_REFRESH）创建新版本 N+1，旧版本 N 保持不变
- 模块快照（ResearchModule）随 package 版本一起复制，被刷新的模块
  重置为 UNVERIFIED 状态，未刷新的模块保留原有快照

状态流转：
  Package: PENDING → BUILDING → READY / FAILED
  Module:  UNVERIFIED → PENDING → REFRESHING → READY / FAILED

新鲜度（freshness）由 calculate_module_freshness 基于
last_verified_at 和 stale_after 时间戳确定性推导。
"""

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

# 11 种研究模块类型，覆盖公司、业务、行业、订单、财务、预期、估值、风险、催化剂、竞对、管理层
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
    """Append-only research package version for one instrument.

    追加式版本管理：每个 version 不可变，新版本通过 previous_version_id
    指向前驱，形成版本链。唯一约束 instrument_id+version 和
    instrument_id+idempotency_key 保证幂等写入安全。
    CheckConstraint ck_research_package_lineage 保证 v1 无前驱、
    v>1 必须有前驱。
    """

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
    """Module snapshot that belongs to exactly one research package version.

    模块快照：每个 package 版本包含全部 11 个模块。增量刷新时：
    - 被刷新的模块 → 新建 UNVERIFIED 状态的空模块
    - 未刷新的模块 → 复制上一版本的快照（保留 summary、source_refs 等）
    origin_module_id 指向本模块上一版本的来源，仅复制模块填充。
    """

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
    # 复制模块的来源模块 ID，刷新模块为 None
    origin_module_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("research_module.id", ondelete="SET NULL"),
        nullable=True,
    )
    module_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # module_version 与所属 package 的 version 保持一致
    module_version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UNVERIFIED")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 来源引用列表（URL、文件 key 等），以 JSON 数组存储
    source_refs: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    # 快照时间点：模块内容代表该时刻的事实
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # 最后一次验证时间，None 表示尚未验证过（freshness=UNVERIFIED）
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # 超过该时间戳后模块视为 STALE
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
