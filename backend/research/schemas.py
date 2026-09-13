"""Research Package Pydantic schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResearchModuleType(StrEnum):
    """Supported Research module types."""

    COMPANY = "COMPANY"
    BUSINESS = "BUSINESS"
    INDUSTRY = "INDUSTRY"
    ORDER = "ORDER"
    FINANCIAL = "FINANCIAL"
    EXPECTATION = "EXPECTATION"
    VALUATION = "VALUATION"
    RISK = "RISK"
    CATALYST = "CATALYST"
    COMPETITOR = "COMPETITOR"
    MANAGEMENT = "MANAGEMENT"


class ResearchFreshness(StrEnum):
    """Deterministic Research module freshness values."""

    UNVERIFIED = "UNVERIFIED"
    FRESH = "FRESH"
    STALE = "STALE"
    FAILED = "FAILED"


class ResearchErrorCode(StrEnum):
    """Stable public Research API error codes."""

    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"
    RESEARCH_PACKAGE_NOT_FOUND = "RESEARCH_PACKAGE_NOT_FOUND"
    RESEARCH_PACKAGE_ALREADY_EXISTS = "RESEARCH_PACKAGE_ALREADY_EXISTS"
    RESEARCH_VERSION_CONFLICT = "RESEARCH_VERSION_CONFLICT"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    RESEARCH_VALIDATION_ERROR = "RESEARCH_VALIDATION_ERROR"
    RESEARCH_PERSISTENCE_CONFLICT = "RESEARCH_PERSISTENCE_CONFLICT"
    RESEARCH_DOMAIN_ERROR = "RESEARCH_DOMAIN_ERROR"


class ResearchErrorDetail(BaseModel):
    """Stable public Research API error detail."""

    code: ResearchErrorCode
    message: str
    expected_version: int | None = None
    current_version: int | None = None


class ResearchErrorResponse(BaseModel):
    """Stable public Research API error response."""

    detail: ResearchErrorDetail


class ResearchRefreshRequest(BaseModel):
    """Request to create an incremental Research Package version."""

    expected_version: int = Field(ge=1)
    module_types: list[ResearchModuleType] = Field(min_length=1, max_length=11)

    @field_validator("module_types")
    @classmethod
    def reject_duplicate_module_types(
        cls,
        module_types: list[ResearchModuleType],
    ) -> list[ResearchModuleType]:
        """Require a refresh request to identify each module at most once."""
        if len(set(module_types)) != len(module_types):
            raise ValueError("module_types must not contain duplicate values")
        return module_types


class ResearchModuleRead(BaseModel):
    """Research module snapshot response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    research_package_id: str
    origin_module_id: str | None = None
    module_type: str
    module_version: int
    status: str
    freshness: ResearchFreshness = Field(
        description=(
            "Deterministic content freshness. UNVERIFIED means no source-backed "
            "verification exists; FRESH/STALE are derived from last_verified_at "
            "and stale_after; FAILED means module refresh failed."
        ),
    )
    summary: str | None = None
    source_refs: list[str]
    as_of: datetime
    last_verified_at: datetime | None = None
    stale_after: datetime
    created_at: datetime


class ResearchPackageRead(BaseModel):
    """Research package version response schema.

    Package status is a build lifecycle state. Module freshness is the content
    freshness signal. PENDING or UNVERIFIED content is not ACTIVE verified
    research, and stale content must not be silently displayed as current.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    instrument_id: str
    version: int
    previous_version_id: str | None = None
    trigger_type: str
    status: str = Field(
        description=(
            "Build lifecycle status for the package version, not a content "
            "freshness verdict. PENDING does not mean ACTIVE verified research."
        ),
    )
    expected_version: int | None = None
    as_of: datetime
    started_at: datetime
    completed_at: datetime | None = None
    last_verified_at: datetime | None = None
    created_at: datetime
    modules: list[ResearchModuleRead]
