"""Research Package domain services.

研究包领域服务，实现追加式版本管理的核心逻辑。
关键设计：
1. 幂等性：通过 idempotency_key + request_hash 保证同一请求多次
   提交只创建一个版本。request_hash 基于规范化请求体计算，
   module_types 排序后哈希使得不同顺序的相同集合等价。
2. 乐观并发：增量刷新使用 expected_version + SELECT FOR UPDATE
   防止并发创建重复版本。
3. 事务安全：_persist_new_package 使用 begin_nested（savepoint），
   IntegrityError 后回滚到保存点，不影响外层事务。
4. 不可变历史：所有写操作都是 INSERT，不 UPDATE 已有版本。
"""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from backend.instrument.models import Instrument
from backend.research.models import ResearchModule, ResearchPackage
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

DEFAULT_RESEARCH_MODULE_TYPES: tuple[str, ...] = (
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
DEFAULT_MODULE_FRESHNESS_DAYS = 30


class ResearchDomainError(Exception):
    """Base class for stable Research domain errors.

    每个子类携带一个稳定的 code 字符串，API 层据此映射到
    HTTP 状态码和错误响应。code 值与 ResearchErrorCode 枚举保持一致。
    """

    code = "RESEARCH_DOMAIN_ERROR"


class InstrumentNotFound(ResearchDomainError):
    """Raised when the target instrument does not exist."""

    code = "INSTRUMENT_NOT_FOUND"


class ResearchPackageNotFound(ResearchDomainError):
    """Raised when no package exists for the requested operation."""

    code = "RESEARCH_PACKAGE_NOT_FOUND"


class ResearchPackageAlreadyExists(ResearchDomainError):
    """Raised when creating a second initial package for an instrument."""

    code = "RESEARCH_PACKAGE_ALREADY_EXISTS"


class ResearchVersionConflict(ResearchDomainError):
    """Raised when expected_version does not match the current package version.

    携带 expected_version 和 current_version，API 层将其放入错误详情，
    便于客户端据此决定下一步操作（如刷新 expected_version 后重试）。
    """

    code = "RESEARCH_VERSION_CONFLICT"

    def __init__(self, expected_version: int, current_version: int | None) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            f"Expected research version {expected_version}, current version is {current_version}"
        )


class IdempotencyConflict(ResearchDomainError):
    """Raised when an idempotency key is reused for a different request.

    幂等键可安全重放相同请求（返回同一版本），但若用同一 key
    提交不同语义内容则报错，防止幂等机制被误用。
    """

    code = "IDEMPOTENCY_CONFLICT"


class ResearchPersistenceConflict(ResearchDomainError):
    """Raised when a database constraint rejects a research write."""

    code = "RESEARCH_PERSISTENCE_CONFLICT"


class ResearchValidationError(ResearchDomainError):
    """Raised when service inputs violate the Research contract."""

    code = "RESEARCH_VALIDATION_ERROR"


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def calculate_module_freshness(module: ResearchModule, now: datetime | None = None) -> str:
    """Derive module freshness deterministically from status and timestamps.

    推导规则（优先级从高到低）：
    - FAILED → 模块刷新失败
    - last_verified_at 为 None → UNVERIFIED（从未被验证过，无事实依据）
    - 当前时间超过 stale_after → STALE（已过期，不应作为当前研究依据）
    - 其他 → FRESH

    此函数为纯计算，不含 LLM 判断，保证结果可复现。
    """
    if module.status == "FAILED":
        return "FAILED"
    if module.last_verified_at is None:
        return "UNVERIFIED"

    observed_at = now or utc_now()
    if observed_at > module.stale_after:
        return "STALE"
    return "FRESH"


async def create_initial_package(
    db: AsyncSession,
    instrument_id: str,
    idempotency_key: str,
    request_hash: str,
    as_of: datetime | None = None,
) -> ResearchPackage:
    """Create the first append-only Research Package version for an instrument.

    流程：
    1. 校验标的存
    2. 幂等键查重（同一 key + 同一 hash → 返回已有版本）
    3. 检查是否已有初始版本（有 → ResearchPackageAlreadyExists）
    4. 创建 v1，包含全部 11 个 UNVERIFIED 状态的模块
    """
    await _ensure_instrument_exists(db, instrument_id)
    existing = await _get_package_by_idempotency_key(db, instrument_id, idempotency_key)
    if existing is not None:
        _ensure_same_request(existing, request_hash)
        return existing

    current = await get_current_package(db, instrument_id)
    if current is not None:
        raise ResearchPackageAlreadyExists(
            f"Research package already exists for instrument {instrument_id}"
        )

    timestamp = as_of or utc_now()
    package = ResearchPackage(
        instrument_id=instrument_id,
        version=1,
        trigger_type="INITIAL_FULL",
        status="PENDING",
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        expected_version=None,
        as_of=timestamp,
        started_at=timestamp,
        created_at=timestamp,
    )
    package.modules = [
        _new_unverified_module(
            package_version=1,
            module_type=module_type,
            as_of=timestamp,
        )
        for module_type in DEFAULT_RESEARCH_MODULE_TYPES
    ]

    return await _persist_new_package(db, package)


async def get_current_package(
    db: AsyncSession,
    instrument_id: str,
) -> ResearchPackage | None:
    """Get the latest Research Package version for an instrument."""
    result = await db.execute(
        _package_select()
        .where(ResearchPackage.instrument_id == instrument_id)
        .order_by(ResearchPackage.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_package_history(
    db: AsyncSession,
    instrument_id: str,
) -> list[ResearchPackage]:
    """List all Research Package versions for an instrument in version order."""
    result = await db.execute(
        _package_select()
        .where(ResearchPackage.instrument_id == instrument_id)
        .order_by(ResearchPackage.version.asc())
    )
    return list(result.scalars().unique().all())


async def get_package_version(
    db: AsyncSession,
    instrument_id: str,
    version: int,
) -> ResearchPackage | None:
    """Get one Research Package version by instrument and version number."""
    result = await db.execute(
        _package_select().where(
            ResearchPackage.instrument_id == instrument_id,
            ResearchPackage.version == version,
        )
    )
    return result.scalar_one_or_none()


async def create_incremental_refresh(
    db: AsyncSession,
    instrument_id: str,
    expected_version: int,
    idempotency_key: str,
    request_hash: str,
    refresh_module_types: Sequence[str] | None = None,
    as_of: datetime | None = None,
) -> ResearchPackage:
    """Create version N+1 without modifying version N or its module snapshots.

    流程：
    1. 校验标的存
    2. 幂等键查重
    3. 校验要刷新的模块类型合
    4. SELECT FOR UPDATE 锁定当前版本（防并发）
    5. 校验 expected_version == 当前版本（防过期请求）
    6. 创建新版本：刷新模块 → 新建空模块；未刷新模块 → 复制上一版本快照
    """
    await _ensure_instrument_exists(db, instrument_id)
    existing = await _get_package_by_idempotency_key(db, instrument_id, idempotency_key)
    if existing is not None:
        _ensure_same_request(existing, request_hash)
        return existing

    refresh_set = _validate_module_types(refresh_module_types or ())
    # SELECT FOR UPDATE 保证并发场景下只有一个请求能成功创建下一版本
    current = await _get_current_package_for_update(db, instrument_id)
    if current is None:
        raise ResearchPackageNotFound(f"No Research package exists for instrument {instrument_id}")
    if current.version != expected_version:
        raise ResearchVersionConflict(expected_version, current.version)

    timestamp = as_of or utc_now()
    next_version = current.version + 1
    package = ResearchPackage(
        instrument_id=instrument_id,
        version=next_version,
        previous_version_id=current.id,
        trigger_type="INCREMENTAL_REFRESH",
        status="PENDING",
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        expected_version=expected_version,
        as_of=timestamp,
        started_at=timestamp,
        created_at=timestamp,
    )
    package.modules = [
        _copy_or_refresh_module(
            previous_module=module,
            package_version=next_version,
            as_of=timestamp,
            should_refresh=module.module_type in refresh_set,
        )
        for module in current.modules
    ]

    return await _persist_new_package(
        db,
        package,
        expected_version=expected_version,
        instrument_id=instrument_id,
    )


def _package_select() -> Select[tuple[ResearchPackage]]:
    return select(ResearchPackage).options(selectinload(ResearchPackage.modules))


async def _ensure_instrument_exists(db: AsyncSession, instrument_id: str) -> None:
    instrument = await db.get(Instrument, instrument_id)
    if instrument is None:
        raise InstrumentNotFound(f"Instrument {instrument_id} not found")


async def _get_package_by_idempotency_key(
    db: AsyncSession,
    instrument_id: str,
    idempotency_key: str,
) -> ResearchPackage | None:
    result = await db.execute(
        _package_select().where(
            ResearchPackage.instrument_id == instrument_id,
            ResearchPackage.idempotency_key == idempotency_key,
        )
    )
    return result.scalar_one_or_none()


async def _get_current_package_for_update(
    db: AsyncSession,
    instrument_id: str,
) -> ResearchPackage | None:
    result = await db.execute(
        _package_select()
        .where(ResearchPackage.instrument_id == instrument_id)
        .order_by(ResearchPackage.version.desc())
        .limit(1)
        .with_for_update()
    )
    return result.scalar_one_or_none()


def _ensure_same_request(package: ResearchPackage, request_hash: str) -> None:
    if package.request_hash != request_hash:
        raise IdempotencyConflict(
            "Idempotency key was already used for a different Research request"
        )


def _validate_module_types(module_types: Sequence[str]) -> set[str]:
    module_set = set(module_types)
    unknown = module_set.difference(DEFAULT_RESEARCH_MODULE_TYPES)
    if unknown:
        unknown_text = ", ".join(sorted(unknown))
        raise ResearchValidationError(f"Unknown Research module type(s): {unknown_text}")
    return module_set


def _new_unverified_module(
    package_version: int,
    module_type: str,
    as_of: datetime,
) -> ResearchModule:
    return ResearchModule(
        module_type=module_type,
        module_version=package_version,
        status="UNVERIFIED",
        summary=None,
        source_refs=[],
        as_of=as_of,
        stale_after=as_of + timedelta(days=DEFAULT_MODULE_FRESHNESS_DAYS),
        created_at=as_of,
    )


def _copy_or_refresh_module(
    previous_module: ResearchModule,
    package_version: int,
    as_of: datetime,
    should_refresh: bool,
) -> ResearchModule:
    """Copy-on-write 模块复制逻辑。

    - should_refresh=True：新建 UNVERIFIED 空模块，丢弃旧快照
    - should_refresh=False：完整复制上一版本的状态和时间戳，
      仅更新 module_version 和 created_at
    """
    if should_refresh:
        return _new_unverified_module(
            package_version=package_version,
            module_type=previous_module.module_type,
            as_of=as_of,
        )

    # 复制模式：保留来源引用以便追溯模块演变历史
    module = ResearchModule(
        origin_module_id=previous_module.id,
        module_type=previous_module.module_type,
        module_version=package_version,
        status=previous_module.status,
        summary=previous_module.summary,
        source_refs=list(previous_module.source_refs),
        as_of=previous_module.as_of,
        last_verified_at=previous_module.last_verified_at,
        stale_after=previous_module.stale_after,
        created_at=as_of,
    )
    return module


async def _persist_new_package(
    db: AsyncSession,
    package: ResearchPackage,
    expected_version: int | None = None,
    instrument_id: str | None = None,
) -> ResearchPackage:
    """持久化新包版本，处理并发冲突和完整性错误。

    使用 begin_nested（savepoint）保证失败时只回滚当前包写入，
    不影响外层事务。IntegrityError 后的处理逻辑：
    1. 若是 idempotency_key 冲突 → 校验 request_hash 后返回已有版本
    2. 若是版本唯一约束冲突 → 抛出 ResearchVersionConflict
    3. 其他约束冲突 → ResearchPersistenceConflict
    """
    try:
        async with db.begin_nested():
            db.add(package)
            await db.flush()
    except IntegrityError as exc:
        # 并发场景：另一个请求可能已写入相同 idempotency_key 的包
        existing = await _get_package_by_idempotency_key(
            db,
            package.instrument_id,
            package.idempotency_key,
        )
        if existing is not None:
            _ensure_same_request(existing, package.request_hash)
            return existing
        # 版本号唯一约束冲突，说明并发创建了同一版本
        if expected_version is not None and instrument_id is not None:
            current = await get_current_package(db, instrument_id)
            raise ResearchVersionConflict(
                expected_version,
                current.version if current is not None else None,
            ) from exc
        raise ResearchPersistenceConflict("Research package write violated constraints") from exc

    persisted = await _get_package_by_idempotency_key(
        db,
        package.instrument_id,
        package.idempotency_key,
    )
    if persisted is None:
        raise ResearchPersistenceConflict("Research package was not persisted")
    return persisted
