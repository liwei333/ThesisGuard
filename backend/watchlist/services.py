"""Watchlist domain services.

自选池领域服务。核心职责：
1. classify_instrument：根据标的特征自动分类并生成可解释的分类理由、
   研究评分和 Agent 建议动作。分类规则基于标签、symbol 和类型组合。
2. add_to_watchlist：解析标的 → 幂等去重 → 分类 → 写入。
3. 增删改查封装，上层 API 层通过本服务访问自选数据。

分类设计原则：不同类别的标的适用不同的研究框架。例如：
- 事件驱动：关注政策/会议窗口，不依赖 PE 估值
- 游资情绪：关注梯队、连板、换手，而非远期 PE
- 机构趋势：沿订单、收入、利润、现金流、一致预期验证
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from backend.instrument.models import Instrument
from backend.instrument.services import CatalogInstrument, resolve_instrument
from backend.watchlist.models import WatchlistItem
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


@dataclass(frozen=True)
class ClassificationResult:
    """Explainable classification result."""

    classification: str
    confidence: int
    reason: str
    research_score: int | None
    thesis_summary: str
    agent_action: str


def classify_instrument(instrument: CatalogInstrument | Instrument) -> ClassificationResult:
    """Classify an instrument into the research model it should use."""
    symbol = instrument.symbol
    name = instrument.name
    tags = _tags_for(instrument)
    instrument_type = instrument.instrument_type

    if instrument_type == "EVENT_BASKET" or "事件驱动" in tags:
        return ClassificationResult(
            classification="EVENT_DRIVEN",
            confidence=76,
            reason="事件篮子以政策、会议、突发事件为主，应按事件前后暴露与验证窗口管理。",
            research_score=None,
            thesis_summary="事件前控制高 Beta 暴露，事件后按结果恢复或撤销观察。",
            agent_action="等待事件落地",
        )

    if symbol == "000722" or "游资情绪" in tags:
        return ClassificationResult(
            classification="HOT_MONEY",
            confidence=68,
            reason="题材强度、板块梯队、连板记忆和换手质量比远期 PE 更重要。",
            research_score=68,
            thesis_summary=f"{name} 需要按情绪周期、梯队地位和市场记忆观察。",
            agent_action="等分歧确认",
        )

    if symbol == "301128":
        return ClassificationResult(
            classification="INSTITUTIONAL_TREND",
            confidence=82,
            reason="AI液冷与半导体设备逻辑需要沿订单、收入、利润、现金流和一致预期验证。",
            research_score=82,
            thesis_summary="AI服务器液冷业务进入订单放量期，后续重点验证利润兑现与现金流质量。",
            agent_action="回踩关注",
        )

    return ClassificationResult(
        classification="INSTITUTIONAL_TREND",
        confidence=72,
        reason="该标的更适合按产业逻辑、订单兑现、盈利质量、估值和机构预期持续验证。",
        research_score=72,
        thesis_summary=f"{name} 已进入机构趋势模型观察，等待结构化事实继续验证。",
        agent_action="等待价格与事实确认",
    )


def _tags_for(instrument: CatalogInstrument | Instrument) -> set[str]:
    if isinstance(instrument, CatalogInstrument):
        return set(instrument.tags)
    return {tag.tag for tag in instrument.tags}


async def list_watchlist(
    db: AsyncSession,
    classification: str | None = None,
) -> list[WatchlistItem]:
    """List watchlist items."""
    statement = select(WatchlistItem).options(joinedload(WatchlistItem.instrument))
    if classification:
        statement = statement.where(WatchlistItem.classification == classification)
    statement = statement.order_by(WatchlistItem.created_at.desc())
    result = await db.execute(statement)
    return list(result.scalars().unique().all())


async def add_to_watchlist(
    db: AsyncSession,
    query: str,
    notes: str | None = None,
) -> WatchlistItem:
    """Resolve an instrument, classify it, and add it to watchlist.

    幂等性保证：同一 instrument_id 已存在时直接返回已有记录，
    不重复写入。新标的自动分类并生成 thesis_summary 与 agent_action。
    """
    instrument = await resolve_instrument(db, query)
    if instrument is None:
        raise ValueError("Instrument not found")

    existing = await get_watchlist_item_by_instrument(db, instrument.id)
    if existing is not None:
        return existing

    classification = classify_instrument(instrument)
    now = datetime.now(UTC)
    item = WatchlistItem(
        instrument_id=instrument.id,
        classification=classification.classification,
        classification_confidence=classification.confidence,
        classification_reason=classification.reason,
        research_status="ACTIVE",
        research_score=classification.research_score,
        thesis_summary=classification.thesis_summary,
        agent_action=classification.agent_action,
        notes=notes,
        created_at=now,
        updated_at=now,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item, attribute_names=["instrument"])
    return item


async def get_watchlist_item(db: AsyncSession, item_id: str) -> WatchlistItem | None:
    """Fetch a watchlist item by ID."""
    result = await db.execute(
        select(WatchlistItem)
        .options(joinedload(WatchlistItem.instrument))
        .where(WatchlistItem.id == item_id)
    )
    return result.scalar_one_or_none()


async def get_watchlist_item_by_instrument(
    db: AsyncSession,
    instrument_id: str,
) -> WatchlistItem | None:
    """Fetch a watchlist item by instrument ID."""
    result = await db.execute(
        select(WatchlistItem)
        .options(joinedload(WatchlistItem.instrument))
        .where(WatchlistItem.instrument_id == instrument_id)
    )
    return result.scalar_one_or_none()


async def update_watchlist_item(
    db: AsyncSession,
    item: WatchlistItem,
    classification: str | None = None,
    research_status: str | None = None,
    agent_action: str | None = None,
    notes: str | None = None,
) -> WatchlistItem:
    """Update editable watchlist fields."""
    if classification is not None:
        item.classification = classification
    if research_status is not None:
        item.research_status = research_status
    if agent_action is not None:
        item.agent_action = agent_action
    if notes is not None:
        item.notes = notes
    item.updated_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(item, attribute_names=["instrument"])
    return item


async def remove_watchlist_item(db: AsyncSession, item: WatchlistItem) -> None:
    """Remove a watchlist item."""
    await db.delete(item)
    await db.flush()
