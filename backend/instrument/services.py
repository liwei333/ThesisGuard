"""Instrument domain services.

提供标的搜索与内置目录管理。内置目录（CATALOG）是 V1 阶段的
种子数据：在尚未接入行情数据源前，用户可通过目录快速添加观察标的。
ensure_instrument 实现了幂等写入：先查 symbol 是否已存在，不存在则新建。
搜索策略：先查数据库，无结果时回退到内置目录并自动持久化匹配项。
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from backend.instrument.models import Instrument, InstrumentAlias, InstrumentTag
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


@dataclass(frozen=True)
class CatalogInstrument:
    """Built-in seed instrument used before a market-data provider exists."""

    symbol: str
    name: str
    instrument_type: str
    exchange: str
    market: str = "CN"
    currency: str = "CNY"
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    aliases: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


CATALOG: tuple[CatalogInstrument, ...] = (
    CatalogInstrument(
        symbol="301128",
        name="强瑞技术",
        instrument_type="STOCK",
        exchange="SZSE",
        sector="先进制造",
        industry="AI液冷与半导体设备",
        description="AI服务器液冷、半导体精密零部件与自动化设备标的。",
        aliases=("强瑞", "Qiangrui", "Qiangrui Technology"),
        tags=("AI液冷", "半导体设备", "订单验证", "机构趋势"),
    ),
    CatalogInstrument(
        symbol="301018",
        name="申菱环境",
        instrument_type="STOCK",
        exchange="SZSE",
        sector="先进制造",
        industry="液冷温控",
        description="数据中心液冷与工业温控设备标的。",
        aliases=("申菱", "Shenling"),
        tags=("AI液冷", "温控", "机构趋势"),
    ),
    CatalogInstrument(
        symbol="300260",
        name="新莱应材",
        instrument_type="STOCK",
        exchange="SZSE",
        sector="半导体",
        industry="半导体材料与洁净应用",
        description="半导体洁净材料、食品医药洁净应用与国产替代标的。",
        aliases=("新莱", "Kinglai"),
        tags=("国产替代", "半导体", "机构趋势"),
    ),
    CatalogInstrument(
        symbol="000722",
        name="湖南发展",
        instrument_type="STOCK",
        exchange="SZSE",
        sector="公用事业",
        industry="电力与题材交易",
        description="电力题材、市场记忆与情绪周期观察标的。",
        aliases=("湖南", "Hunan Development"),
        tags=("电力题材", "梯队", "连板记忆", "游资情绪"),
    ),
    CatalogInstrument(
        symbol="FOMC",
        name="FOMC 事件篮子",
        instrument_type="EVENT_BASKET",
        exchange="EVENT",
        market="GLOBAL",
        currency="USD",
        sector="宏观事件",
        industry="利率决议",
        description="议息会议相关高 Beta 暴露与事件后恢复观察篮子。",
        aliases=("美联储", "议息会议", "FOMC event basket"),
        tags=("政策", "事件驱动", "宏观"),
    ),
)


def normalize_query(query: str) -> str:
    """Normalize user search text."""
    return query.strip().lower()


def search_catalog(query: str, limit: int = 10) -> list[CatalogInstrument]:
    """Search the built-in instrument catalog."""
    needle = normalize_query(query)
    if not needle:
        return []

    matches: list[CatalogInstrument] = []
    for item in CATALOG:
        haystack = [
            item.symbol.lower(),
            item.name.lower(),
            item.exchange.lower(),
            *(alias.lower() for alias in item.aliases),
            *(tag.lower() for tag in item.tags),
        ]
        if any(needle in value for value in haystack):
            matches.append(item)
        if len(matches) >= limit:
            break
    return matches


def _search_statement(query: str, limit: int) -> Select[tuple[Instrument]]:
    like = f"%{query}%"
    return (
        select(Instrument)
        .outerjoin(InstrumentAlias)
        .options(selectinload(Instrument.aliases), selectinload(Instrument.tags))
        .where(
            or_(
                Instrument.symbol.ilike(like),
                Instrument.name.ilike(like),
                InstrumentAlias.alias.ilike(like),
            )
        )
        .order_by(Instrument.symbol)
        .limit(limit)
    )


async def search_instruments(
    db: AsyncSession,
    query: str,
    limit: int = 10,
) -> list[Instrument]:
    """Search persisted instruments, falling back to the built-in catalog.

    搜索优先级：
    1. 数据库精确/模糊匹配（symbol、name、alias）
    2. 内置目录匹配 + 自动持久化（首次搜索到的新标的写入 DB）
    """
    normalized = query.strip()
    if not normalized:
        return []

    result = await db.execute(_search_statement(normalized, limit))
    instruments = list(result.scalars().unique().all())
    if instruments:
        return instruments

    # 数据库无匹配时回退到内置目录，并通过 ensure_instrument 幂等写入
    catalog_matches = search_catalog(normalized, limit)
    created: list[Instrument] = []
    for item in catalog_matches:
        created.append(await ensure_instrument(db, item))
    return created


async def get_instrument_by_symbol(
    db: AsyncSession,
    symbol: str,
) -> Instrument | None:
    """Fetch an instrument by symbol."""
    result = await db.execute(
        select(Instrument)
        .options(selectinload(Instrument.aliases), selectinload(Instrument.tags))
        .where(Instrument.symbol == symbol.upper())
    )
    return result.scalar_one_or_none()


async def resolve_instrument(db: AsyncSession, query: str) -> Instrument | None:
    """Resolve user input to a single instrument."""
    matches = await search_instruments(db, query, limit=1)
    return matches[0] if matches else None


async def ensure_instrument(
    db: AsyncSession,
    catalog_item: CatalogInstrument,
) -> Instrument:
    """Persist a catalog instrument if it does not already exist.

    幂等写入：symbol 已存在则直接返回，否则新建并级联写入
    aliases 和 tags。flush 后立即 refresh 以获取关联对象。
    """
    existing = await get_instrument_by_symbol(db, catalog_item.symbol)
    if existing is not None:
        return existing

    now = datetime.now(UTC)
    instrument = Instrument(
        symbol=catalog_item.symbol,
        name=catalog_item.name,
        instrument_type=catalog_item.instrument_type,
        exchange=catalog_item.exchange,
        market=catalog_item.market,
        currency=catalog_item.currency,
        sector=catalog_item.sector,
        industry=catalog_item.industry,
        description=catalog_item.description,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )
    # 级联写入别名和标签，Instrument 模型配置了 cascade="all, delete-orphan"
    instrument.aliases = [
        InstrumentAlias(alias=alias, alias_type="NAME")
        for alias in catalog_item.aliases
    ]
    instrument.tags = [InstrumentTag(tag=tag) for tag in catalog_item.tags]
    db.add(instrument)
    await db.flush()
    await db.refresh(instrument, attribute_names=["aliases", "tags"])
    return instrument
