"""Research Package API endpoints."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Annotated, Any

from backend.common.db.session import get_db
from backend.research.models import ResearchModule, ResearchPackage
from backend.research.schemas import (
    ResearchErrorCode,
    ResearchErrorDetail,
    ResearchErrorResponse,
    ResearchFreshness,
    ResearchModuleRead,
    ResearchPackageRead,
    ResearchRefreshRequest,
)
from backend.research.services import (
    IdempotencyConflict,
    InstrumentNotFound,
    ResearchDomainError,
    ResearchPackageAlreadyExists,
    ResearchPackageNotFound,
    ResearchPersistenceConflict,
    ResearchValidationError,
    ResearchVersionConflict,
    calculate_module_freshness,
    create_incremental_refresh,
    create_initial_package,
    get_current_package,
    get_package_version,
    list_package_history,
    utc_now,
)
from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/research", tags=["research"])

RESEARCH_NOT_FOUND_RESPONSE = {
    "model": ResearchErrorResponse,
    "description": "Research resource not found",
}
RESEARCH_CONFLICT_RESPONSE = {
    "model": ResearchErrorResponse,
    "description": "Research write, version, or idempotency conflict",
}
HTTP_VALIDATION_RESPONSE = {
    "description": "FastAPI request validation error",
    "content": {
        "application/json": {
            "schema": {"$ref": "#/components/schemas/HTTPValidationError"},
        },
    },
}
RESEARCH_OR_HTTP_VALIDATION_RESPONSE = {
    "description": "FastAPI request validation or Research domain validation error",
    "content": {
        "application/json": {
            "schema": {
                "oneOf": [
                    {"$ref": "#/components/schemas/HTTPValidationError"},
                    {"$ref": "#/components/schemas/ResearchErrorResponse"},
                ],
            },
        },
    },
}

IdempotencyKey = Annotated[
    str,
    Header(
        alias="Idempotency-Key",
        min_length=1,
        max_length=128,
        description="Required idempotency key for Research Package mutations.",
    ),
]


def require_idempotency_key(idempotency_key: IdempotencyKey) -> str:
    """Validate and normalize the required idempotency header."""
    normalized = idempotency_key.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResearchErrorDetail(
                code=ResearchErrorCode.RESEARCH_VALIDATION_ERROR,
                message="Idempotency-Key must not be blank",
            ).model_dump(mode="json", exclude_none=True),
        )
    return normalized


def build_request_hash(operation: str, instrument_id: str, body: dict[str, Any]) -> str:
    """Hash the canonical semantic request body, excluding Idempotency-Key."""
    payload = {
        "operation": operation,
        "instrument_id": instrument_id,
        "body": body,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_initial_request_hash(instrument_id: str) -> str:
    """Build the deterministic request hash for initial package creation."""
    return build_request_hash("research_package.initial", instrument_id, {})


def build_refresh_request_hash(instrument_id: str, payload: ResearchRefreshRequest) -> str:
    """Build the deterministic request hash for refresh creation."""
    module_types = sorted(module_type.value for module_type in payload.module_types)
    return build_request_hash(
        "research_package.refresh",
        instrument_id,
        {
            "expected_version": payload.expected_version,
            "module_types": module_types,
        },
    )


def research_http_exception(error: ResearchDomainError) -> HTTPException:
    """Map Research domain errors to stable HTTP responses."""
    try:
        error_code = ResearchErrorCode(error.code)
    except ValueError:
        error_code = ResearchErrorCode.RESEARCH_DOMAIN_ERROR

    detail = ResearchErrorDetail(
        code=error_code,
        message=str(error),
    )

    if isinstance(error, InstrumentNotFound | ResearchPackageNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, ResearchPackageAlreadyExists | IdempotencyConflict):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(error, ResearchVersionConflict):
        status_code = status.HTTP_409_CONFLICT
        detail.expected_version = error.expected_version
        detail.current_version = error.current_version
    elif isinstance(error, ResearchValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(error, ResearchPersistenceConflict):
        status_code = status.HTTP_409_CONFLICT
        detail.message = "Research package write conflict"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = ResearchErrorDetail(
            code=ResearchErrorCode.RESEARCH_DOMAIN_ERROR,
            message="Research domain operation failed",
        )

    return HTTPException(
        status_code=status_code,
        detail=detail.model_dump(mode="json", exclude_none=True),
    )


def package_to_read(package: ResearchPackage) -> ResearchPackageRead:
    """Serialize one package version with a single freshness observation time."""
    observed_at = utc_now()
    modules = [
        module_to_read(module=module, observed_at=observed_at)
        for module in sorted(package.modules, key=lambda item: item.module_type)
    ]
    return ResearchPackageRead(
        id=package.id,
        instrument_id=package.instrument_id,
        version=package.version,
        previous_version_id=package.previous_version_id,
        trigger_type=package.trigger_type,
        status=package.status,
        expected_version=package.expected_version,
        as_of=package.as_of,
        started_at=package.started_at,
        completed_at=package.completed_at,
        last_verified_at=package.last_verified_at,
        created_at=package.created_at,
        modules=modules,
    )


def module_to_read(module: ResearchModule, observed_at: datetime) -> ResearchModuleRead:
    """Serialize one module snapshot with derived freshness."""
    return ResearchModuleRead(
        id=module.id,
        research_package_id=module.research_package_id,
        origin_module_id=module.origin_module_id,
        module_type=module.module_type,
        module_version=module.module_version,
        status=module.status,
        freshness=ResearchFreshness(calculate_module_freshness(module, now=observed_at)),
        summary=module.summary,
        source_refs=module.source_refs,
        as_of=module.as_of,
        last_verified_at=module.last_verified_at,
        stale_after=module.stale_after,
        created_at=module.created_at,
    )


@router.post(
    "/instruments/{instrument_id}/packages",
    response_model=ResearchPackageRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: RESEARCH_NOT_FOUND_RESPONSE,
        409: RESEARCH_CONFLICT_RESPONSE,
        422: RESEARCH_OR_HTTP_VALIDATION_RESPONSE,
    },
)
async def create_initial_research_package_endpoint(
    instrument_id: str,
    idempotency_key: Annotated[str, Depends(require_idempotency_key)],
    db: AsyncSession = Depends(get_db),
) -> ResearchPackageRead:
    """Create initial Research Package version 1 for an instrument."""
    try:
        package = await create_initial_package(
            db=db,
            instrument_id=instrument_id,
            idempotency_key=idempotency_key,
            request_hash=build_initial_request_hash(instrument_id),
        )
    except ResearchDomainError as error:
        raise research_http_exception(error) from error
    return package_to_read(package)


@router.get(
    "/instruments/{instrument_id}/packages/current",
    response_model=ResearchPackageRead,
    responses={404: RESEARCH_NOT_FOUND_RESPONSE},
)
async def get_current_research_package_endpoint(
    instrument_id: str,
    db: AsyncSession = Depends(get_db),
) -> ResearchPackageRead:
    """Get the current Research Package version for an instrument."""
    package = await get_current_package(db=db, instrument_id=instrument_id)
    if package is None:
        raise research_http_exception(
            ResearchPackageNotFound(
                f"No Research package exists for instrument {instrument_id}"
            )
        )
    return package_to_read(package)


@router.get(
    "/instruments/{instrument_id}/packages",
    response_model=list[ResearchPackageRead],
)
async def list_research_package_history_endpoint(
    instrument_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ResearchPackageRead]:
    """List all Research Package versions for an instrument."""
    packages = await list_package_history(db=db, instrument_id=instrument_id)
    return [package_to_read(package) for package in packages]


@router.get(
    "/instruments/{instrument_id}/packages/versions/{version}",
    response_model=ResearchPackageRead,
    responses={
        404: RESEARCH_NOT_FOUND_RESPONSE,
        422: HTTP_VALIDATION_RESPONSE,
    },
)
async def get_research_package_version_endpoint(
    instrument_id: str,
    version: Annotated[int, Path(ge=1)],
    db: AsyncSession = Depends(get_db),
) -> ResearchPackageRead:
    """Get a specified Research Package version for an instrument."""
    package = await get_package_version(
        db=db,
        instrument_id=instrument_id,
        version=version,
    )
    if package is None:
        raise research_http_exception(
            ResearchPackageNotFound(
                f"Research package version {version} not found for instrument {instrument_id}"
            )
        )
    return package_to_read(package)


@router.post(
    "/instruments/{instrument_id}/packages/refresh",
    response_model=ResearchPackageRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: RESEARCH_NOT_FOUND_RESPONSE,
        409: RESEARCH_CONFLICT_RESPONSE,
        422: RESEARCH_OR_HTTP_VALIDATION_RESPONSE,
    },
)
async def refresh_research_package_endpoint(
    instrument_id: str,
    payload: ResearchRefreshRequest,
    idempotency_key: Annotated[str, Depends(require_idempotency_key)],
    db: AsyncSession = Depends(get_db),
) -> ResearchPackageRead:
    """Create an append-only incremental Research Package version."""
    try:
        package = await create_incremental_refresh(
            db=db,
            instrument_id=instrument_id,
            expected_version=payload.expected_version,
            idempotency_key=idempotency_key,
            request_hash=build_refresh_request_hash(instrument_id, payload),
            refresh_module_types=[module_type.value for module_type in payload.module_types],
        )
    except ResearchDomainError as error:
        raise research_http_exception(error) from error
    return package_to_read(package)
