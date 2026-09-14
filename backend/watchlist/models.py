"""Watchlist SQLAlchemy models.

自选池条目。每个条目对应一个标的，并携带分类结果、研究状态和
自动生成的投资论点摘要。instrument_id 唯一约束保证同一标的不会
重复加入自选。
分类类型包括：INSTITUTIONAL_TREND（机构趋势）、HOT_MONEY（游资情绪）、
EVENT_DRIVEN（事件驱动）等，由 classify_instrument 服务决定。
"""

from datetime import UTC, datetime

from backend.common.db.session import Base
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class WatchlistItem(Base):
    """A user-tracked instrument with classification state."""

    __tablename__ = "watchlist_item"
    # 同一标的只能有一条自选记录，重复添加返回已有记录
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
    # 分类结果：INSTITUTIONAL_TREND / HOT_MONEY / EVENT_DRIVEN 等
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    # 分类置信度 0-100，用于 UI 展示和后续筛选
    classification_confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    # 分类理由，可解释性输出，供用户理解为何归入该类型
    classification_reason: Mapped[str] = mapped_column(Text, nullable=False)
    # 研究状态：ACTIVE（进行中）等，控制研究任务调度
    research_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    # 研究评分，可为 None（事件驱动类标的暂无评分）
    research_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 自动生成的投资论点摘要，由分类服务产出
    thesis_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Agent 建议的下一步操作（如"等分歧确认"、"回踩关注"）
    agent_action: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 用户自选的备注信息
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
