"""Research Package domain services."""

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
    """Base class for stable Research domain errors."""

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
    """Raised when expected_version does not match the current package version."""

    code = "RESEARCH_VERSION_CONFLICT"

    def __init__(self, expected_version: int, current_version: int | None) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            f"Expected research version {expected_version}, current version is {current_version}"
        )


class IdempotencyConflict(ResearchDomainError):
    """Raised when an idempotency key is reused for a different request."""

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
    """Derive module freshness deterministically from status and timestamps."""
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
    """Create the first append-only Research Package version for an instrument."""
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
    """Create version N+1 without modifying version N or its module snapshots."""
    await _ensure_instrument_exists(db, instrument_id)
    existing = await _get_package_by_idempotency_key(db, instrument_id, idempotency_key)
    if existing is not None:
        _ensure_same_request(existing, request_hash)
        return existing

    refresh_set = _validate_module_types(refresh_module_types or ())
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
    if should_refresh:
        return _new_unverified_module(
            package_version=package_version,
            module_type=previous_module.module_type,
            as_of=as_of,
        )

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
    try:
        async with db.begin_nested():
            db.add(package)
            await db.flush()
    except IntegrityError as exc:
        existing = await _get_package_by_idempotency_key(
            db,
            package.instrument_id,
            package.idempotency_key,
        )
        if existing is not None:
            _ensure_same_request(existing, package.request_hash)
            return existing
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
