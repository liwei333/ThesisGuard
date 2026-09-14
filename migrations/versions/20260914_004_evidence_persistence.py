"""Create Evidence persistence tables.

Revision ID: 000000000004
Revises: 000000000003
Create Date: 2026-09-14 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000004"
down_revision: str | None = "000000000003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_TYPES = (
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
ACTORS = ("SYSTEM", "USER", "LLM_PROPOSAL", "IMPORTER", "ADMIN_SCRIPT")
SOURCE_STATUS_ACTORS = ("SYSTEM", "USER", "IMPORTER", "ADMIN_SCRIPT")
SOURCE_GRADES = ("S", "A", "B", "C", "D", "E", "F")
SOURCE_VERSION_REASONS = (
    "NEW_CONTENT",
    "CORRECTION",
    "REFETCH_CHANGED",
    "GRADE_RECLASSIFICATION",
    "METADATA_CORRECTION",
    "RETRACTION_NOTICE",
)
SOURCE_STATUSES = ("ACTIVE", "RETRACTED", "SUPERSEDED")
SCOPE_TYPES = ("INSTRUMENT", "MARKET", "SECTOR", "POLICY", "CROSS_INSTRUMENT")
INFORMATION_TYPES = ("FACT", "ESTIMATE", "THESIS_INFERENCE", "USER_HYPOTHESIS")
PROVENANCE_KINDS = ("SOURCE_BACKED", "MANUAL", "DERIVED")
VERIFICATION_STATUSES = (
    "UNREVIEWED",
    "PENDING_REVIEW",
    "VERIFIED",
    "REJECTED",
    "DISPUTED",
    "INVALIDATED",
    "RETRACTED",
)
STATUS_CHANGE_KINDS = (
    "INITIAL_VERIFICATION",
    "REVIEW_REQUEST",
    "REVIEW_DECISION",
    "DISPUTE",
    "INVALIDATION",
    "RETRACTION",
    "CORRECTION",
)
LOCATOR_TYPES = (
    "PAGE",
    "PAGE_PARAGRAPH",
    "SECTION",
    "TABLE",
    "TABLE_CELL",
    "WEB_ANCHOR",
    "TIME_RANGE",
)
INSTRUMENT_LINK_ROLES = (
    "PRIMARY_SCOPE",
    "RELATED_COMPANY",
    "SECTOR_MEMBER",
    "PEER",
    "POLICY_TARGET",
)
CORROBORATION_RELATION_TYPES = ("CORROBORATES", "CONFLICTS_WITH", "PARTIALLY_SUPPORTS")
DERIVATION_LINK_ROLES = ("SUPPORTS_INFERENCE", "INPUT_FACT", "INPUT_ESTIMATE", "MANUAL_CONTEXT")
IDEMPOTENCY_STATUSES = ("COMMITTED", "UNKNOWN_OUTCOME")
AUDIT_AGGREGATE_TYPES = ("SourceDocument", "EvidenceSeries", "EvidenceVersion")

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


def quoted_values(values: tuple[str, ...]) -> str:
    """Return SQL string literals for a CHECK IN expression."""
    return ", ".join(f"'{value}'" for value in values)


def upgrade() -> None:
    """Create WP-04 Evidence tables."""
    op.create_table(
        "source_document",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("publisher_key", sa.String(length=128), nullable=False),
        sa.Column("publisher_name", sa.String(length=256), nullable=False),
        sa.Column("issuer_key", sa.String(length=128), nullable=True),
        sa.Column("issuer_name", sa.String(length=256), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("external_document_id", sa.String(length=256), nullable=True),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("document_language", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_actor", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            f"source_type IN ({quoted_values(SOURCE_TYPES)})",
            name="ck_source_document_source_type",
        ),
        sa.CheckConstraint(
            f"created_by_actor IN ({quoted_values(ACTORS)})",
            name="ck_source_document_created_by_actor",
        ),
        sa.CheckConstraint(
            "external_document_id IS NOT NULL OR canonical_url IS NOT NULL",
            name="ck_source_document_identity_present",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_source_document_external_identity",
        "source_document",
        ["publisher_key", "source_type", "external_document_id"],
        unique=True,
        postgresql_where=sa.text("external_document_id IS NOT NULL"),
    )
    op.create_index(
        "uq_source_document_url_identity",
        "source_document",
        ["publisher_key", "source_type", "canonical_url"],
        unique=True,
        postgresql_where=sa.text("external_document_id IS NULL AND canonical_url IS NOT NULL"),
    )
    op.create_index("ix_source_document_issuer_key", "source_document", ["issuer_key"])
    op.create_index("ix_source_document_source_type", "source_document", ["source_type"])
    op.create_index("ix_source_document_canonical_url", "source_document", ["canonical_url"])

    op.create_table(
        "source_document_version",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_document_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("version_reason", sa.String(length=64), nullable=False),
        sa.Column("source_grade", sa.String(length=1), nullable=False),
        sa.Column("version_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("source_version_label", sa.String(length=128), nullable=True),
        sa.Column("source_revision_id", sa.String(length=128), nullable=True),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("object_key", sa.Text(), nullable=False),
        sa.Column("text_object_key", sa.Text(), nullable=True),
        sa.Column("text_object_hash", sa.String(length=128), nullable=True),
        sa.Column("parser_name", sa.String(length=128), nullable=True),
        sa.Column("parser_version", sa.String(length=64), nullable=True),
        sa.Column("versioned_metadata", sa.JSON(), nullable=False),
        sa.Column("source_status", sa.String(length=32), nullable=False),
        sa.Column("source_status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_status_actor", sa.String(length=32), nullable=True),
        sa.Column("source_status_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_source_document_version_positive"),
        sa.CheckConstraint(
            f"version_reason IN ({quoted_values(SOURCE_VERSION_REASONS)})",
            name="ck_source_document_version_reason",
        ),
        sa.CheckConstraint(
            f"source_grade IN ({quoted_values(SOURCE_GRADES)})",
            name="ck_source_document_version_source_grade",
        ),
        sa.CheckConstraint(
            f"source_status IN ({quoted_values(SOURCE_STATUSES)})",
            name="ck_source_document_version_source_status",
        ),
        sa.CheckConstraint(
            "(source_status = 'ACTIVE' AND source_status_changed_at IS NULL "
            "AND source_status_actor IS NULL AND source_status_reason IS NULL) OR "
            "(source_status IN ('RETRACTED', 'SUPERSEDED') "
            "AND source_status_changed_at IS NOT NULL "
            "AND source_status_actor IS NOT NULL "
            "AND source_status_reason IS NOT NULL)",
            name="ck_source_document_version_source_status_metadata",
        ),
        sa.CheckConstraint(
            "source_status_actor IS NULL OR "
            f"source_status_actor IN ({quoted_values(SOURCE_STATUS_ACTORS)})",
            name="ck_source_document_version_source_status_actor",
        ),
        sa.ForeignKeyConstraint(["source_document_id"], ["source_document.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_document_id",
            "version",
            name="uq_source_document_version_document_version",
        ),
        sa.UniqueConstraint(
            "source_document_id",
            "version_fingerprint",
            name="uq_source_document_version_fingerprint",
        ),
    )
    op.create_index(
        "ix_source_document_version_source_document_id",
        "source_document_version",
        ["source_document_id"],
    )
    op.create_index("ix_source_document_version_content_hash", "source_document_version", ["content_hash"])
    op.create_index(
        "ix_source_document_version_fingerprint",
        "source_document_version",
        ["version_fingerprint"],
    )
    op.create_index("ix_source_document_version_source_grade", "source_document_version", ["source_grade"])
    op.create_index(
        "ix_source_document_version_source_status",
        "source_document_version",
        ["source_status"],
    )
    op.create_index("ix_source_document_version_observed_at", "source_document_version", ["observed_at"])
    op.create_index("ix_source_document_version_published_at", "source_document_version", ["published_at"])

    op.create_table(
        "evidence_series",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_key", sa.String(length=256), nullable=False),
        sa.Column("information_type", sa.String(length=32), nullable=False),
        sa.Column("claim_key", sa.String(length=256), nullable=False),
        sa.Column("metric_key", sa.String(length=128), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provenance_kind", sa.String(length=32), nullable=False),
        sa.Column("primary_source_document_id", sa.String(length=36), nullable=True),
        sa.Column("origin_key", sa.String(length=256), nullable=True),
        sa.Column("series_identity_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_actor", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            f"scope_type IN ({quoted_values(SCOPE_TYPES)})",
            name="ck_evidence_series_scope_type",
        ),
        sa.CheckConstraint(
            f"information_type IN ({quoted_values(INFORMATION_TYPES)})",
            name="ck_evidence_series_information_type",
        ),
        sa.CheckConstraint(
            f"provenance_kind IN ({quoted_values(PROVENANCE_KINDS)})",
            name="ck_evidence_series_provenance_kind",
        ),
        sa.CheckConstraint(
            "(provenance_kind = 'SOURCE_BACKED' "
            "AND primary_source_document_id IS NOT NULL AND origin_key IS NULL) OR "
            "(provenance_kind IN ('MANUAL', 'DERIVED') "
            "AND primary_source_document_id IS NULL AND origin_key IS NOT NULL)",
            name="ck_evidence_series_provenance_origin",
        ),
        sa.CheckConstraint(
            "period_start IS NULL OR period_end IS NULL OR period_start <= period_end",
            name="ck_evidence_series_period_order",
        ),
        sa.CheckConstraint(
            f"created_by_actor IN ({quoted_values(ACTORS)})",
            name="ck_evidence_series_created_by_actor",
        ),
        sa.ForeignKeyConstraint(
            ["primary_source_document_id"],
            ["source_document.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_identity_hash", name="uq_evidence_series_identity_hash"),
    )
    op.create_index("ix_evidence_series_scope_type", "evidence_series", ["scope_type"])
    op.create_index("ix_evidence_series_scope_key", "evidence_series", ["scope_key"])
    op.create_index(
        "ix_evidence_series_primary_source_document_id",
        "evidence_series",
        ["primary_source_document_id"],
    )
    op.create_index("ix_evidence_series_information_type", "evidence_series", ["information_type"])
    op.create_index("ix_evidence_series_claim_key", "evidence_series", ["claim_key"])
    op.create_index("ix_evidence_series_metric_key", "evidence_series", ["metric_key"])

    op.create_table(
        "evidence_version",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_series_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("source_document_version_id", sa.String(length=36), nullable=True),
        sa.Column("information_type", sa.String(length=32), nullable=False),
        sa.Column("provenance_kind", sa.String(length=32), nullable=False),
        sa.Column("source_grade_snapshot", sa.String(length=1), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status_changed_by_actor", sa.String(length=32), nullable=True),
        sa.Column("status_change_kind", sa.String(length=32), nullable=True),
        sa.Column("status_reason", sa.Text(), nullable=True),
        sa.Column("display_title", sa.Text(), nullable=False),
        sa.Column("display_text", sa.Text(), nullable=False),
        sa.Column("claim_key", sa.String(length=256), nullable=False),
        sa.Column("metric_key", sa.String(length=128), nullable=True),
        sa.Column("raw_value", sa.Text(), nullable=True),
        sa.Column("raw_unit", sa.String(length=64), nullable=True),
        sa.Column("normalized_value", sa.Numeric(), nullable=True),
        sa.Column("normalized_text_value", sa.Text(), nullable=True),
        sa.Column("normalized_unit", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=16), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("supersedes_evidence_version_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_actor", sa.String(length=32), nullable=False),
        sa.Column("extractor_name", sa.String(length=128), nullable=True),
        sa.Column("extractor_version", sa.String(length=64), nullable=True),
        sa.Column("prompt_template_version", sa.String(length=128), nullable=True),
        sa.Column("manual_entry_reason", sa.Text(), nullable=True),
        sa.Column("manual_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trusted_correction_rule", sa.String(length=128), nullable=True),
        sa.CheckConstraint("version >= 1", name="ck_evidence_version_positive"),
        sa.CheckConstraint(
            f"information_type IN ({quoted_values(INFORMATION_TYPES)})",
            name="ck_evidence_version_information_type",
        ),
        sa.CheckConstraint(
            f"source_grade_snapshot IS NULL OR source_grade_snapshot IN ({quoted_values(SOURCE_GRADES)})",
            name="ck_evidence_version_source_grade_snapshot",
        ),
        sa.CheckConstraint(
            f"verification_status IN ({quoted_values(VERIFICATION_STATUSES)})",
            name="ck_evidence_version_verification_status",
        ),
        sa.CheckConstraint(
            f"provenance_kind IN ({quoted_values(PROVENANCE_KINDS)})",
            name="ck_evidence_version_provenance_kind",
        ),
        sa.CheckConstraint(
            "period_start IS NULL OR period_end IS NULL OR period_start <= period_end",
            name="ck_evidence_version_period_order",
        ),
        sa.CheckConstraint(
            "effective_from IS NULL OR effective_to IS NULL OR effective_from <= effective_to",
            name="ck_evidence_version_effective_order",
        ),
        sa.CheckConstraint(
            "(provenance_kind = 'SOURCE_BACKED' "
            "AND source_document_version_id IS NOT NULL AND source_grade_snapshot IS NOT NULL) OR "
            "(provenance_kind IN ('MANUAL', 'DERIVED') "
            "AND source_document_version_id IS NULL AND source_grade_snapshot IS NULL)",
            name="ck_evidence_version_source_provenance",
        ),
        sa.CheckConstraint(
            "information_type <> 'FACT' OR provenance_kind = 'SOURCE_BACKED'",
            name="ck_evidence_version_fact_source_backed",
        ),
        sa.CheckConstraint(
            "information_type <> 'ESTIMATE' OR provenance_kind <> 'MANUAL' OR "
            "(manual_entry_reason IS NOT NULL AND manual_observed_at IS NOT NULL)",
            name="ck_evidence_version_manual_estimate_metadata",
        ),
        sa.CheckConstraint(
            "information_type <> 'USER_HYPOTHESIS' OR "
            "(provenance_kind = 'MANUAL' AND created_by_actor = 'USER' "
            "AND manual_entry_reason IS NOT NULL AND manual_observed_at IS NOT NULL)",
            name="ck_evidence_version_user_hypothesis_manual",
        ),
        sa.CheckConstraint(
            "information_type <> 'THESIS_INFERENCE' OR provenance_kind = 'DERIVED'",
            name="ck_evidence_version_thesis_inference_derived",
        ),
        sa.CheckConstraint(
            f"({STATUS_AUDIT_ALL_NULL}) OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_status_audit_all_null_or_all_set",
        ),
        sa.CheckConstraint(
            f"NOT ({STATUS_AUDIT_ALL_NULL}) OR "
            "(version = 1 AND verification_status = 'UNREVIEWED' "
            "AND supersedes_evidence_version_id IS NULL)",
            name="ck_evidence_version_status_audit_null_only_initial",
        ),
        sa.CheckConstraint(
            f"supersedes_evidence_version_id IS NULL OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_supersedes_requires_audit",
        ),
        sa.CheckConstraint(
            "NOT (version = 1 AND supersedes_evidence_version_id IS NOT NULL) OR "
            "status_change_kind = 'CORRECTION'",
            name="ck_evidence_version_replacement_v1_kind",
        ),
        sa.CheckConstraint(
            f"version = 1 OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_n_plus_one_requires_audit",
        ),
        sa.CheckConstraint(
            f"NOT (version = 1 AND verification_status = 'VERIFIED') OR ({STATUS_AUDIT_ALL_SET})",
            name="ck_evidence_version_initial_verified_requires_audit",
        ),
        sa.CheckConstraint(
            INITIAL_STATE_CHECK,
            name="ck_evidence_version_initial_state",
        ),
        sa.CheckConstraint(
            f"status_change_kind IS NULL OR status_change_kind IN ({quoted_values(STATUS_CHANGE_KINDS)})",
            name="ck_evidence_version_status_change_kind",
        ),
        sa.CheckConstraint(
            f"status_changed_by_actor IS NULL OR status_changed_by_actor IN ({quoted_values(ACTORS)})",
            name="ck_evidence_version_status_changed_by_actor",
        ),
        sa.CheckConstraint(
            f"created_by_actor IN ({quoted_values(ACTORS)})",
            name="ck_evidence_version_created_by_actor",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'INITIAL_VERIFICATION' OR "
            "(version = 1 AND verification_status = 'VERIFIED')",
            name="ck_evidence_version_initial_verification_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'REVIEW_REQUEST' OR verification_status = 'PENDING_REVIEW'",
            name="ck_evidence_version_review_request_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'REVIEW_DECISION' OR "
            "verification_status IN ('VERIFIED', 'REJECTED')",
            name="ck_evidence_version_review_decision_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'DISPUTE' OR "
            "verification_status IN ('DISPUTED', 'VERIFIED', 'REJECTED')",
            name="ck_evidence_version_dispute_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'INVALIDATION' OR verification_status = 'INVALIDATED'",
            name="ck_evidence_version_invalidation_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'RETRACTION' OR verification_status = 'RETRACTED'",
            name="ck_evidence_version_retraction_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'CORRECTION' OR "
            "verification_status IN ('UNREVIEWED', 'VERIFIED')",
            name="ck_evidence_version_correction_status",
        ),
        sa.CheckConstraint(
            "status_change_kind <> 'CORRECTION' OR supersedes_evidence_version_id IS NOT NULL",
            name="ck_evidence_version_correction_requires_predecessor",
        ),
        sa.CheckConstraint(
            "NOT (status_change_kind = 'CORRECTION' AND verification_status = 'VERIFIED') OR "
            "trusted_correction_rule IS NOT NULL",
            name="ck_evidence_version_trusted_verified_correction_rule",
        ),
        sa.CheckConstraint(
            "verification_status NOT IN ('RETRACTED', 'INVALIDATED') OR "
            "supersedes_evidence_version_id IS NOT NULL",
            name="ck_evidence_version_tombstone_requires_predecessor",
        ),
        sa.ForeignKeyConstraint(["evidence_series_id"], ["evidence_series.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["source_document_version_id"],
            ["source_document_version.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_evidence_version_id"],
            ["evidence_version.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evidence_series_id",
            "version",
            name="uq_evidence_version_series_version",
        ),
    )
    op.create_index("ix_evidence_version_series_id", "evidence_version", ["evidence_series_id"])
    op.create_index(
        "ix_evidence_version_source_document_version_id",
        "evidence_version",
        ["source_document_version_id"],
    )
    op.create_index(
        "ix_evidence_version_verification_status",
        "evidence_version",
        ["verification_status"],
    )
    op.create_index(
        "ix_evidence_version_source_grade_snapshot",
        "evidence_version",
        ["source_grade_snapshot"],
    )
    op.create_index("ix_evidence_version_provenance_kind", "evidence_version", ["provenance_kind"])
    op.create_index("ix_evidence_version_as_of", "evidence_version", ["as_of"])

    op.create_table(
        "evidence_source_locator",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("source_document_version_id", sa.String(length=36), nullable=False),
        sa.Column("locator_type", sa.String(length=32), nullable=False),
        sa.Column("raw_locator", sa.Text(), nullable=False),
        sa.Column("short_citation", sa.String(length=256), nullable=False),
        sa.Column("locator_payload", sa.JSON(), nullable=False),
        sa.Column("quote_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"locator_type IN ({quoted_values(LOCATOR_TYPES)})",
            name="ck_evidence_source_locator_type",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_version_id"],
            ["evidence_version.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_document_version_id"],
            ["source_document_version.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evidence_version_id",
            "source_document_version_id",
            "locator_type",
            "raw_locator",
            name="uq_evidence_source_locator_identity",
        ),
    )
    op.create_index(
        "ix_evidence_source_locator_evidence_version_id",
        "evidence_source_locator",
        ["evidence_version_id"],
    )
    op.create_index(
        "ix_evidence_source_locator_source_document_version_id",
        "evidence_source_locator",
        ["source_document_version_id"],
    )

    op.create_table(
        "evidence_instrument_link",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("instrument_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("link_order", sa.Integer(), nullable=True),
        sa.Column("link_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"role IN ({quoted_values(INSTRUMENT_LINK_ROLES)})",
            name="ck_evidence_instrument_link_role",
        ),
        sa.ForeignKeyConstraint(["evidence_version_id"], ["evidence_version.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["instrument_id"], ["instrument.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evidence_version_id",
            "instrument_id",
            "role",
            name="uq_evidence_instrument_link_identity",
        ),
    )
    op.create_index(
        "ix_evidence_instrument_link_instrument_id",
        "evidence_instrument_link",
        ["instrument_id"],
    )
    op.create_index(
        "ix_evidence_instrument_link_evidence_version_id",
        "evidence_instrument_link",
        ["evidence_version_id"],
    )
    op.create_index("ix_evidence_instrument_link_role", "evidence_instrument_link", ["role"])

    op.create_table(
        "evidence_corroboration_link",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("left_evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("right_evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_actor", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "left_evidence_version_id < right_evidence_version_id",
            name="ck_evidence_corroboration_link_ordering",
        ),
        sa.CheckConstraint(
            f"relation_type IN ({quoted_values(CORROBORATION_RELATION_TYPES)})",
            name="ck_evidence_corroboration_link_relation_type",
        ),
        sa.CheckConstraint(
            f"created_by_actor IN ({quoted_values(ACTORS)})",
            name="ck_evidence_corroboration_link_created_by_actor",
        ),
        sa.ForeignKeyConstraint(
            ["left_evidence_version_id"],
            ["evidence_version.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["right_evidence_version_id"],
            ["evidence_version.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "left_evidence_version_id",
            "right_evidence_version_id",
            "relation_type",
            name="uq_evidence_corroboration_link_identity",
        ),
    )
    op.create_index(
        "ix_evidence_corroboration_link_left_version_id",
        "evidence_corroboration_link",
        ["left_evidence_version_id"],
    )
    op.create_index(
        "ix_evidence_corroboration_link_right_version_id",
        "evidence_corroboration_link",
        ["right_evidence_version_id"],
    )

    op.create_table(
        "evidence_derivation_link",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("derived_evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("supporting_evidence_version_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("support_order", sa.Integer(), nullable=True),
        sa.Column("support_weight", sa.Numeric(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "derived_evidence_version_id <> supporting_evidence_version_id",
            name="ck_evidence_derivation_link_no_self_link",
        ),
        sa.CheckConstraint(
            f"role IN ({quoted_values(DERIVATION_LINK_ROLES)})",
            name="ck_evidence_derivation_link_role",
        ),
        sa.ForeignKeyConstraint(
            ["derived_evidence_version_id"],
            ["evidence_version.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supporting_evidence_version_id"],
            ["evidence_version.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "derived_evidence_version_id",
            "supporting_evidence_version_id",
            "role",
            name="uq_evidence_derivation_link_identity",
        ),
    )
    op.create_index(
        "ix_evidence_derivation_link_derived_version_id",
        "evidence_derivation_link",
        ["derived_evidence_version_id"],
    )
    op.create_index(
        "ix_evidence_derivation_link_supporting_version_id",
        "evidence_derivation_link",
        ["supporting_evidence_version_id"],
    )

    op.create_table(
        "evidence_idempotency_record",
        sa.Column("scope", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("response_ref_type", sa.String(length=64), nullable=False),
        sa.Column("response_ref_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"status IN ({quoted_values(IDEMPOTENCY_STATUSES)})",
            name="ck_evidence_idempotency_record_status",
        ),
        sa.PrimaryKeyConstraint("scope", "idempotency_key"),
    )
    op.create_index(
        "ix_evidence_idempotency_record_request_hash",
        "evidence_idempotency_record",
        ["request_hash"],
    )

    op.create_table(
        "evidence_audit_event",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            f"aggregate_type IN ({quoted_values(AUDIT_AGGREGATE_TYPES)})",
            name="ck_evidence_audit_event_aggregate_type",
        ),
        sa.CheckConstraint(
            f"actor IN ({quoted_values(ACTORS)})",
            name="ck_evidence_audit_event_actor",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_evidence_audit_event_aggregate",
        "evidence_audit_event",
        ["aggregate_type", "aggregate_id"],
    )
    op.create_index("ix_evidence_audit_event_occurred_at", "evidence_audit_event", ["occurred_at"])


def downgrade() -> None:
    """Drop WP-04 Evidence tables."""
    op.drop_index("ix_evidence_audit_event_occurred_at", table_name="evidence_audit_event")
    op.drop_index("ix_evidence_audit_event_aggregate", table_name="evidence_audit_event")
    op.drop_table("evidence_audit_event")
    op.drop_index(
        "ix_evidence_idempotency_record_request_hash",
        table_name="evidence_idempotency_record",
    )
    op.drop_table("evidence_idempotency_record")
    op.drop_index(
        "ix_evidence_derivation_link_supporting_version_id",
        table_name="evidence_derivation_link",
    )
    op.drop_index(
        "ix_evidence_derivation_link_derived_version_id",
        table_name="evidence_derivation_link",
    )
    op.drop_table("evidence_derivation_link")
    op.drop_index(
        "ix_evidence_corroboration_link_right_version_id",
        table_name="evidence_corroboration_link",
    )
    op.drop_index(
        "ix_evidence_corroboration_link_left_version_id",
        table_name="evidence_corroboration_link",
    )
    op.drop_table("evidence_corroboration_link")
    op.drop_index("ix_evidence_instrument_link_role", table_name="evidence_instrument_link")
    op.drop_index(
        "ix_evidence_instrument_link_evidence_version_id",
        table_name="evidence_instrument_link",
    )
    op.drop_index(
        "ix_evidence_instrument_link_instrument_id",
        table_name="evidence_instrument_link",
    )
    op.drop_table("evidence_instrument_link")
    op.drop_index(
        "ix_evidence_source_locator_source_document_version_id",
        table_name="evidence_source_locator",
    )
    op.drop_index(
        "ix_evidence_source_locator_evidence_version_id",
        table_name="evidence_source_locator",
    )
    op.drop_table("evidence_source_locator")
    op.drop_index("ix_evidence_version_as_of", table_name="evidence_version")
    op.drop_index("ix_evidence_version_provenance_kind", table_name="evidence_version")
    op.drop_index("ix_evidence_version_source_grade_snapshot", table_name="evidence_version")
    op.drop_index("ix_evidence_version_verification_status", table_name="evidence_version")
    op.drop_index("ix_evidence_version_source_document_version_id", table_name="evidence_version")
    op.drop_index("ix_evidence_version_series_id", table_name="evidence_version")
    op.drop_table("evidence_version")
    op.drop_index("ix_evidence_series_metric_key", table_name="evidence_series")
    op.drop_index("ix_evidence_series_claim_key", table_name="evidence_series")
    op.drop_index("ix_evidence_series_information_type", table_name="evidence_series")
    op.drop_index(
        "ix_evidence_series_primary_source_document_id",
        table_name="evidence_series",
    )
    op.drop_index("ix_evidence_series_scope_key", table_name="evidence_series")
    op.drop_index("ix_evidence_series_scope_type", table_name="evidence_series")
    op.drop_table("evidence_series")
    op.drop_index("ix_source_document_version_published_at", table_name="source_document_version")
    op.drop_index("ix_source_document_version_observed_at", table_name="source_document_version")
    op.drop_index("ix_source_document_version_source_status", table_name="source_document_version")
    op.drop_index("ix_source_document_version_source_grade", table_name="source_document_version")
    op.drop_index("ix_source_document_version_fingerprint", table_name="source_document_version")
    op.drop_index("ix_source_document_version_content_hash", table_name="source_document_version")
    op.drop_index(
        "ix_source_document_version_source_document_id",
        table_name="source_document_version",
    )
    op.drop_table("source_document_version")
    op.drop_index("ix_source_document_canonical_url", table_name="source_document")
    op.drop_index("ix_source_document_source_type", table_name="source_document")
    op.drop_index("ix_source_document_issuer_key", table_name="source_document")
    op.drop_index("uq_source_document_url_identity", table_name="source_document")
    op.drop_index("uq_source_document_external_identity", table_name="source_document")
    op.drop_table("source_document")
