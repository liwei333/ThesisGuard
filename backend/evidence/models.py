"""Evidence SQLAlchemy models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from backend.common.db.session import Base
from backend.instrument.models import Instrument, uuid_str
from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

SOURCE_TYPES: tuple[str, ...] = (
    "COMPANY_ANNOUNCEMENT",
    "FINANCIAL_REPORT",
    "EXCHANGE_FILING",
    "REGULATORY_DATA",
    "OFFICIAL_DATA",
    "POLICY_DOCUMENT",
    "INVESTOR_RELATIONS",
    "INSTITUTIONAL_SURVEY",
    "BROKER_RESEARCH",
    "INDUSTRY_REPORT",
    "FINANCIAL_MEDIA",
    "SOCIAL_MEDIA",
    "RUMOR",
    "WEB_PAGE",
    "USER_NOTE",
)
ACTORS: tuple[str, ...] = ("SYSTEM", "USER", "LLM_PROPOSAL", "IMPORTER", "ADMIN_SCRIPT")
SOURCE_STATUS_ACTORS: tuple[str, ...] = ("SYSTEM", "USER", "IMPORTER", "ADMIN_SCRIPT")
SOURCE_GRADES: tuple[str, ...] = ("S", "A", "B", "C", "D", "E", "F")
SOURCE_VERSION_REASONS: tuple[str, ...] = (
    "NEW_CONTENT",
    "CORRECTION",
    "REFETCH_CHANGED",
    "GRADE_RECLASSIFICATION",
    "METADATA_CORRECTION",
    "RETRACTION_NOTICE",
)
SOURCE_STATUSES: tuple[str, ...] = ("ACTIVE", "RETRACTED", "SUPERSEDED")
SCOPE_TYPES: tuple[str, ...] = ("INSTRUMENT", "MARKET", "SECTOR", "POLICY", "CROSS_INSTRUMENT")
INFORMATION_TYPES: tuple[str, ...] = ("FACT", "ESTIMATE", "THESIS_INFERENCE", "USER_HYPOTHESIS")
PROVENANCE_KINDS: tuple[str, ...] = ("SOURCE_BACKED", "MANUAL", "DERIVED")
VERIFICATION_STATUSES: tuple[str, ...] = (
    "UNREVIEWED",
    "PENDING_REVIEW",
    "VERIFIED",
    "REJECTED",
    "DISPUTED",
    "INVALIDATED",
    "RETRACTED",
)
STATUS_CHANGE_KINDS: tuple[str, ...] = (
    "INITIAL_VERIFICATION",
    "REVIEW_REQUEST",
    "REVIEW_DECISION",
    "DISPUTE",
    "INVALIDATION",
    "RETRACTION",
    "CORRECTION",
)
LOCATOR_TYPES: tuple[str, ...] = (
    "PAGE",
    "PAGE_PARAGRAPH",
    "SECTION",
    "TABLE",
    "TABLE_CELL",
    "WEB_ANCHOR",
    "TIME_RANGE",
)
INSTRUMENT_LINK_ROLES: tuple[str, ...] = (
    "PRIMARY_SCOPE",
    "RELATED_COMPANY",
    "SECTOR_MEMBER",
    "PEER",
    "POLICY_TARGET",
)
CORROBORATION_RELATION_TYPES: tuple[str, ...] = (
    "CORROBORATES",
    "CONFLICTS_WITH",
    "PARTIALLY_SUPPORTS",
)
DERIVATION_LINK_ROLES: tuple[str, ...] = (
    "SUPPORTS_INFERENCE",
    "INPUT_FACT",
    "INPUT_ESTIMATE",
    "MANUAL_CONTEXT",
)
IDEMPOTENCY_STATUSES: tuple[str, ...] = ("COMMITTED", "UNKNOWN_OUTCOME")
AUDIT_AGGREGATE_TYPES: tuple[str, ...] = (
    "SourceDocument",
    "EvidenceSeries",
    "EvidenceVersion",
)

STATUS_AUDIT_ALL_NULL = (
    "status_changed_at IS NULL AND "
    "status_changed_by_actor IS NULL AND "
    "status_change_kind IS NULL AND "
    "status_reason IS NULL"
)
STATUS_AUDIT_ALL_SET = (
    "status_changed_at IS NOT NULL AND "
    "status_changed_by_actor IS NOT NULL AND "
    "status_change_kind IS NOT NULL AND "
    "status_reason IS NOT NULL"
)
INITIAL_STATE_CHECK = (
    "NOT (version = 1 AND supersedes_evidence_version_id IS NULL) OR "
    f"((verification_status = 'UNREVIEWED' AND {STATUS_AUDIT_ALL_NULL}) OR "
    "(verification_status = 'VERIFIED' AND "
    f"{STATUS_AUDIT_ALL_SET} AND status_change_kind = 'INITIAL_VERIFICATION'))"
)


def _quoted_values(values: tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


class SourceDocument(Base):
    """Canonical source identity before versioned source content."""

    __tablename__ = "source_document"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN ({_quoted_values(SOURCE_TYPES)})",
            name="ck_source_document_source_type",
        ),
        CheckConstraint(
            f"created_by_actor IN ({_quoted_values(ACTORS)})",
            name="ck_source_document_created_by_actor",
        ),
        CheckConstraint(
            "external_document_id IS NOT NULL OR canonical_url IS NOT NULL",
            name="ck_source_document_identity_present",
        ),
        Index(
            "uq_source_document_external_identity",
            "publisher_key",
            "source_type",
            "external_document_id",
            unique=True,
            postgresql_where=text("external_document_id IS NOT NULL"),
        ),
        Index(
            "uq_source_document_url_identity",
            "publisher_key",
            "source_type",
            "canonical_url",
            unique=True,
            postgresql_where=text(
                "external_document_id IS NULL AND canonical_url IS NOT NULL"
            ),
        ),
        Index("ix_source_document_issuer_key", "issuer_key"),
        Index("ix_source_document_source_type", "source_type"),
        Index("ix_source_document_canonical_url", "canonical_url"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    publisher_key: Mapped[str] = mapped_column(String(128), nullable=False)
    publisher_name: Mapped[str] = mapped_column(String(256), nullable=False)
    issuer_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    issuer_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    external_document_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by_actor: Mapped[str] = mapped_column(String(32), nullable=False)

    versions: Mapped[list[SourceDocumentVersion]] = relationship(
        back_populates="source_document",
        order_by="SourceDocumentVersion.version",
    )


class SourceDocumentVersion(Base):
    """Immutable versioned source content and source lifecycle snapshot."""

    __tablename__ = "source_document_version"
    __table_args__ = (
        UniqueConstraint(
            "source_document_id",
            "version",
            name="uq_source_document_version_document_version",
        ),
        UniqueConstraint(
            "source_document_id",
            "version_fingerprint",
            name="uq_source_document_version_fingerprint",
        ),
        CheckConstraint("version >= 1", name="ck_source_document_version_positive"),
        CheckConstraint(
            f"version_reason IN ({_quoted_values(SOURCE_VERSION_REASONS)})",
            name="ck_source_document_version_reason",
        ),
        CheckConstraint(
            f"source_grade IN ({_quoted_values(SOURCE_GRADES)})",
            name="ck_source_document_version_source_grade",
        ),
        CheckConstraint(
            f"source_status IN ({_quoted_values(SOURCE_STATUSES)})",
            name="ck_source_document_version_source_status",
        ),
        CheckConstraint(
            "(source_status = 'ACTIVE' AND source_status_changed_at IS NULL "
            "AND source_status_actor IS NULL AND source_status_reason IS NULL) OR "
            "(source_status IN ('RETRACTED', 'SUPERSEDED') "
            "AND source_status_changed_at IS NOT NULL "
            "AND source_status_actor IS NOT NULL "
            "AND source_status_reason IS NOT NULL)",
            name="ck_source_document_version_source_status_metadata",
        ),
        CheckConstraint(
            "source_status_actor IS NULL OR "
            f"source_status_actor IN ({_quoted_values(SOURCE_STATUS_ACTORS)})",
            name="ck_source_document_version_source_status_actor",
        ),
        Index("ix_source_document_version_content_hash", "content_hash"),
        Index("ix_source_document_version_fingerprint", "version_fingerprint"),
        Index("ix_source_document_version_source_grade", "source_grade"),
        Index("ix_source_document_version_source_status", "source_status"),
        Index("ix_source_document_version_observed_at", "observed_at"),
        Index("ix_source_document_version_published_at", "published_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    source_document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_document.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    version_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    source_grade: Mapped[str] = mapped_column(String(1), nullable=False)
    version_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_version_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_revision_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    text_object_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_object_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parser_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    versioned_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    source_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_status_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source_status_actor: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_status_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    source_document: Mapped[SourceDocument] = relationship(back_populates="versions")


class EvidenceSeries(Base):
    """Stable Evidence identity across immutable EvidenceVersion snapshots."""

    __tablename__ = "evidence_series"
    __table_args__ = (
        UniqueConstraint("series_identity_hash", name="uq_evidence_series_identity_hash"),
        CheckConstraint(
            f"scope_type IN ({_quoted_values(SCOPE_TYPES)})",
            name="ck_evidence_series_scope_type",
        ),
        CheckConstraint(
            f"information_type IN ({_quoted_values(INFORMATION_TYPES)})",
            name="ck_evidence_series_information_type",
        ),
        CheckConstraint(
            f"provenance_kind IN ({_quoted_values(PROVENANCE_KINDS)})",
            name="ck_evidence_series_provenance_kind",
        ),
        CheckConstraint(
            "(provenance_kind = 'SOURCE_BACKED' "
            "AND primary_source_document_id IS NOT NULL AND origin_key IS NULL) OR "
            "(provenance_kind IN ('MANUAL', 'DERIVED') "
            "AND primary_source_document_id IS NULL AND origin_key IS NOT NULL)",
            name="ck_evidence_series_provenance_origin",
        ),
        CheckConstraint(
            "period_start IS NULL OR period_end IS NULL OR period_start <= period_end",
            name="ck_evidence_series_period_order",
        ),
        CheckConstraint(
            f"created_by_actor IN ({_quoted_values(ACTORS)})",
            name="ck_evidence_series_created_by_actor",
        ),
        Index("ix_evidence_series_scope_type", "scope_type"),
        Index("ix_evidence_series_scope_key", "scope_key"),
        Index("ix_evidence_series_primary_source_document_id", "primary_source_document_id"),
        Index("ix_evidence_series_information_type", "information_type"),
        Index("ix_evidence_series_claim_key", "claim_key"),
        Index("ix_evidence_series_metric_key", "metric_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(256), nullable=False)
    information_type: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_key: Mapped[str] = mapped_column(String(256), nullable=False)
    metric_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provenance_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    primary_source_document_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("source_document.id", ondelete="RESTRICT"),
        nullable=True,
    )
    origin_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    series_identity_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by_actor: Mapped[str] = mapped_column(String(32), nullable=False)

    primary_source_document: Mapped[SourceDocument | None] = relationship()
    versions: Mapped[list[EvidenceVersion]] = relationship(
        back_populates="series",
        order_by="EvidenceVersion.version",
    )


class EvidenceVersion(Base):
    """Immutable atomic Evidence value, status, provenance, and lineage snapshot."""

    __tablename__ = "evidence_version"
    __table_args__ = (
        UniqueConstraint(
            "evidence_series_id",
            "version",
            name="uq_evidence_version_series_version",
        ),
        CheckConstraint("version >= 1", name="ck_evidence_version_positive"),
        CheckConstraint(
            f"information_type IN ({_quoted_values(INFORMATION_TYPES)})",
            name="ck_evidence_version_information_type",
        ),
        CheckConstraint(
            f"source_grade_snapshot IS NULL OR source_grade_snapshot IN ({_quoted_values(SOURCE_GRADES)})",
            name="ck_evidence_version_source_grade_snapshot",
        ),
        CheckConstraint(
            f"verification_status IN ({_quoted_values(VERIFICATION_STATUSES)})",
            name="ck_evidence_version_verification_status",
        ),
        CheckConstraint(
            f"provenance_kind IN ({_quoted_values(PROVENANCE_KINDS)})",
            name="ck_evidence_version_provenance_kind",
        ),
        CheckConstraint(
            "period_start IS NULL OR period_end IS NULL OR period_start <= period_end",
            name="ck_evidence_version_period_order",
        ),
        CheckConstraint(
            "effective_from IS NULL OR effective_to IS NULL OR effective_from <= effective_to",
            name="ck_evidence_version_effective_order",
        ),
        CheckConstraint(
            "(provenance_kind = 'SOURCE_BACKED' "
            "AND source_document_version_id IS NOT NULL AND source_grade_snapshot IS NOT NULL) OR "
            "(provenance_kind IN ('MANUAL', 'DERIVED') "
            "AND source_document_version_id IS NULL AND source_grade_snapshot IS NULL)",
            name="ck_evidence_version_source_provenance",
        ),
        CheckConstraint(
            "information_type <> 'FACT' OR provenance_kind = 'SOURCE_BACKED'",
            name="ck_evidence_version_fact_source_backed",
        ),
        CheckConstraint(
            "information_type <> 'ESTIMATE' OR provenance_kind <> 'MANUAL' OR "
            "(manual_entry_reason IS NOT NULL AND manual_observed_at IS NOT NULL)",
            name="ck_evidence_version_manual_estimate_metadata",
        ),
        CheckConstraint(
            "information_type <> 'USER_HYPOTHESIS' OR "
            "(provenance_kind = 'MANUAL' AND created_by_actor = 'USER' "
            "AND manual_entry_reason IS NOT NULL AND manual_observed_at IS NOT NULL)",
            name="ck_evidence_version_user_hypothesis_manual",
        ),
        CheckConstraint(
            "information_type <> 'THESIS_INFERENCE' OR provenance_kind = 'DERIVED'",
            name="ck_evidence_version_thesis_inference_derived",
        ),
        CheckConstraint(
            f"({STATUS_AUDIT_ALL_NULL}) OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_status_audit_all_null_or_all_set",
        ),
        CheckConstraint(
            f"NOT ({STATUS_AUDIT_ALL_NULL}) OR "
            "(version = 1 AND verification_status = 'UNREVIEWED' "
            "AND supersedes_evidence_version_id IS NULL)",
            name="ck_evidence_version_status_audit_null_only_initial",
        ),
        CheckConstraint(
            f"supersedes_evidence_version_id IS NULL OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_supersedes_requires_audit",
        ),
        CheckConstraint(
            "NOT (version = 1 AND supersedes_evidence_version_id IS NOT NULL) OR "
            "status_change_kind = 'CORRECTION'",
            name="ck_evidence_version_replacement_v1_kind",
        ),
        CheckConstraint(
            f"version = 1 OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_n_plus_one_requires_audit",
        ),
        CheckConstraint(
            f"NOT (version = 1 AND verification_status = 'VERIFIED') OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_initial_verified_requires_audit",
        ),
        CheckConstraint(
            INITIAL_STATE_CHECK,
            name="ck_evidence_version_initial_state",
        ),
        CheckConstraint(
            f"status_change_kind IS NULL OR status_change_kind IN ({_quoted_values(STATUS_CHANGE_KINDS)})",
            name="ck_evidence_version_status_change_kind",
        ),
        CheckConstraint(
            "status_changed_by_actor IS NULL OR "
            f"status_changed_by_actor IN ({_quoted_values(ACTORS)})",
            name="ck_evidence_version_status_changed_by_actor",
        ),
        CheckConstraint(
            "created_by_actor IN "
            f"({_quoted_values(ACTORS)})",
            name="ck_evidence_version_created_by_actor",
        ),
        CheckConstraint(
            "status_change_kind <> 'INITIAL_VERIFICATION' OR "
            "(version = 1 AND verification_status = 'VERIFIED')",
            name="ck_evidence_version_initial_verification_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'REVIEW_REQUEST' OR verification_status = 'PENDING_REVIEW'",
            name="ck_evidence_version_review_request_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'REVIEW_DECISION' OR "
            "verification_status IN ('VERIFIED', 'REJECTED')",
            name="ck_evidence_version_review_decision_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'DISPUTE' OR "
            "verification_status IN ('DISPUTED', 'VERIFIED', 'REJECTED')",
            name="ck_evidence_version_dispute_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'INVALIDATION' OR verification_status = 'INVALIDATED'",
            name="ck_evidence_version_invalidation_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'RETRACTION' OR verification_status = 'RETRACTED'",
            name="ck_evidence_version_retraction_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'CORRECTION' OR "
            "verification_status IN ('UNREVIEWED', 'VERIFIED')",
            name="ck_evidence_version_correction_status",
        ),
        CheckConstraint(
            "status_change_kind <> 'CORRECTION' OR supersedes_evidence_version_id IS NOT NULL",
            name="ck_evidence_version_correction_requires_predecessor",
        ),
        CheckConstraint(
            "NOT (status_change_kind = 'CORRECTION' AND verification_status = 'VERIFIED') OR "
            "trusted_correction_rule IS NOT NULL",
            name="ck_evidence_version_trusted_verified_correction_rule",
        ),
        CheckConstraint(
            "verification_status NOT IN ('RETRACTED', 'INVALIDATED') OR "
            "supersedes_evidence_version_id IS NOT NULL",
            name="ck_evidence_version_tombstone_requires_predecessor",
        ),
        Index("ix_evidence_version_series_id", "evidence_series_id"),
        Index("ix_evidence_version_source_document_version_id", "source_document_version_id"),
        Index("ix_evidence_version_verification_status", "verification_status"),
        Index("ix_evidence_version_source_grade_snapshot", "source_grade_snapshot"),
        Index("ix_evidence_version_provenance_kind", "provenance_kind"),
        Index("ix_evidence_version_as_of", "as_of"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    evidence_series_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_series.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    source_document_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("source_document_version.id", ondelete="RESTRICT"),
        nullable=True,
    )
    information_type: Mapped[str] = mapped_column(String(32), nullable=False)
    provenance_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    source_grade_snapshot: Mapped[str | None] = mapped_column(String(1), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status_changed_by_actor: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status_change_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_title: Mapped[str] = mapped_column(Text, nullable=False)
    display_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_key: Mapped[str] = mapped_column(String(256), nullable=False)
    metric_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    raw_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    normalized_value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    normalized_text_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_evidence_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by_actor: Mapped[str] = mapped_column(String(32), nullable=False)
    extractor_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    extractor_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_template_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    manual_entry_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    manual_observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trusted_correction_rule: Mapped[str | None] = mapped_column(String(128), nullable=True)

    series: Mapped[EvidenceSeries] = relationship(back_populates="versions")
    source_document_version: Mapped[SourceDocumentVersion | None] = relationship()
    supersedes_evidence_version: Mapped[EvidenceVersion | None] = relationship(
        remote_side=[id],
        foreign_keys=[supersedes_evidence_version_id],
    )
    source_locators: Mapped[list[EvidenceSourceLocator]] = relationship(
        back_populates="evidence_version",
        cascade="all, delete-orphan",
        order_by="EvidenceSourceLocator.raw_locator",
    )
    instrument_links: Mapped[list[EvidenceInstrumentLink]] = relationship(
        back_populates="evidence_version",
        cascade="all, delete-orphan",
        order_by="EvidenceInstrumentLink.link_order",
    )
    left_corroboration_links: Mapped[list[EvidenceCorroborationLink]] = relationship(
        back_populates="left_evidence_version",
        foreign_keys="EvidenceCorroborationLink.left_evidence_version_id",
        cascade="all, delete-orphan",
    )
    right_corroboration_links: Mapped[list[EvidenceCorroborationLink]] = relationship(
        back_populates="right_evidence_version",
        foreign_keys="EvidenceCorroborationLink.right_evidence_version_id",
        cascade="all, delete-orphan",
    )
    derived_links: Mapped[list[EvidenceDerivationLink]] = relationship(
        back_populates="derived_evidence_version",
        foreign_keys="EvidenceDerivationLink.derived_evidence_version_id",
        cascade="all, delete-orphan",
    )
    supporting_derivation_links: Mapped[list[EvidenceDerivationLink]] = relationship(
        back_populates="supporting_evidence_version",
        foreign_keys="EvidenceDerivationLink.supporting_evidence_version_id",
        cascade="all, delete-orphan",
    )


class EvidenceSourceLocator(Base):
    """Exact locator tying one EvidenceVersion to one SourceDocumentVersion."""

    __tablename__ = "evidence_source_locator"
    __table_args__ = (
        UniqueConstraint(
            "evidence_version_id",
            "source_document_version_id",
            "locator_type",
            "raw_locator",
            name="uq_evidence_source_locator_identity",
        ),
        CheckConstraint(
            f"locator_type IN ({_quoted_values(LOCATOR_TYPES)})",
            name="ck_evidence_source_locator_type",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_document_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_document_version.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    locator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    raw_locator: Mapped[str] = mapped_column(Text, nullable=False)
    short_citation: Mapped[str] = mapped_column(String(256), nullable=False)
    locator_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    quote_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    evidence_version: Mapped[EvidenceVersion] = relationship(back_populates="source_locators")
    source_document_version: Mapped[SourceDocumentVersion] = relationship()


class EvidenceInstrumentLink(Base):
    """Immutable instrument fan-out row for one exact EvidenceVersion."""

    __tablename__ = "evidence_instrument_link"
    __table_args__ = (
        UniqueConstraint(
            "evidence_version_id",
            "instrument_id",
            "role",
            name="uq_evidence_instrument_link_identity",
        ),
        CheckConstraint(
            f"role IN ({_quoted_values(INSTRUMENT_LINK_ROLES)})",
            name="ck_evidence_instrument_link_role",
        ),
        Index("ix_evidence_instrument_link_instrument_id", "instrument_id"),
        Index("ix_evidence_instrument_link_evidence_version_id", "evidence_version_id"),
        Index("ix_evidence_instrument_link_role", "role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=False,
    )
    instrument_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("instrument.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    link_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    evidence_version: Mapped[EvidenceVersion] = relationship(back_populates="instrument_links")
    instrument: Mapped[Instrument] = relationship()


class EvidenceCorroborationLink(Base):
    """Symmetric support/conflict relation between exact EvidenceVersion rows."""

    __tablename__ = "evidence_corroboration_link"
    __table_args__ = (
        UniqueConstraint(
            "left_evidence_version_id",
            "right_evidence_version_id",
            "relation_type",
            name="uq_evidence_corroboration_link_identity",
        ),
        CheckConstraint(
            "left_evidence_version_id < right_evidence_version_id",
            name="ck_evidence_corroboration_link_ordering",
        ),
        CheckConstraint(
            f"relation_type IN ({_quoted_values(CORROBORATION_RELATION_TYPES)})",
            name="ck_evidence_corroboration_link_relation_type",
        ),
        CheckConstraint(
            f"created_by_actor IN ({_quoted_values(ACTORS)})",
            name="ck_evidence_corroboration_link_created_by_actor",
        ),
        Index("ix_evidence_corroboration_link_left_version_id", "left_evidence_version_id"),
        Index("ix_evidence_corroboration_link_right_version_id", "right_evidence_version_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    left_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=False,
    )
    right_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    created_by_actor: Mapped[str] = mapped_column(String(32), nullable=False)

    left_evidence_version: Mapped[EvidenceVersion] = relationship(
        back_populates="left_corroboration_links",
        foreign_keys=[left_evidence_version_id],
    )
    right_evidence_version: Mapped[EvidenceVersion] = relationship(
        back_populates="right_corroboration_links",
        foreign_keys=[right_evidence_version_id],
    )


class EvidenceDerivationLink(Base):
    """Directed derivation edge between exact EvidenceVersion rows."""

    __tablename__ = "evidence_derivation_link"
    __table_args__ = (
        UniqueConstraint(
            "derived_evidence_version_id",
            "supporting_evidence_version_id",
            "role",
            name="uq_evidence_derivation_link_identity",
        ),
        CheckConstraint(
            "derived_evidence_version_id <> supporting_evidence_version_id",
            name="ck_evidence_derivation_link_no_self_link",
        ),
        CheckConstraint(
            f"role IN ({_quoted_values(DERIVATION_LINK_ROLES)})",
            name="ck_evidence_derivation_link_role",
        ),
        Index("ix_evidence_derivation_link_derived_version_id", "derived_evidence_version_id"),
        Index("ix_evidence_derivation_link_supporting_version_id", "supporting_evidence_version_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    derived_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=False,
    )
    supporting_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("evidence_version.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    support_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    support_weight: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    derived_evidence_version: Mapped[EvidenceVersion] = relationship(
        back_populates="derived_links",
        foreign_keys=[derived_evidence_version_id],
    )
    supporting_evidence_version: Mapped[EvidenceVersion] = relationship(
        back_populates="supporting_derivation_links",
        foreign_keys=[supporting_evidence_version_id],
    )


class EvidenceIdempotencyRecord(Base):
    """Idempotency record for source and Evidence write commands."""

    __tablename__ = "evidence_idempotency_record"
    __table_args__ = (
        CheckConstraint(
            f"status IN ({_quoted_values(IDEMPOTENCY_STATUSES)})",
            name="ck_evidence_idempotency_record_status",
        ),
        Index("ix_evidence_idempotency_record_request_hash", "request_hash"),
    )

    scope: Mapped[str] = mapped_column(String(128), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    response_ref_type: Mapped[str] = mapped_column(String(64), nullable=False)
    response_ref_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )


class EvidenceAuditEvent(Base):
    """Append-only audit event for source and Evidence aggregates."""

    __tablename__ = "evidence_audit_event"
    __table_args__ = (
        CheckConstraint(
            f"aggregate_type IN ({_quoted_values(AUDIT_AGGREGATE_TYPES)})",
            name="ck_evidence_audit_event_aggregate_type",
        ),
        CheckConstraint(
            f"actor IN ({_quoted_values(ACTORS)})",
            name="ck_evidence_audit_event_actor",
        ),
        Index("ix_evidence_audit_event_aggregate", "aggregate_type", "aggregate_id"),
        Index("ix_evidence_audit_event_occurred_at", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    actor: Mapped[str] = mapped_column(String(32), nullable=False)
