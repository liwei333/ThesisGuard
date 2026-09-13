"""Create research package and module tables.

Revision ID: 000000000003
Revises: 000000000002
Create Date: 2026-09-12 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000003"
down_revision: str | None = "000000000002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create WP-03 append-only Research persistence tables."""
    op.create_table(
        "research_package",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("instrument_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("previous_version_id", sa.String(length=36), nullable=True),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=128), nullable=False),
        sa.Column("expected_version", sa.Integer(), nullable=True),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_research_package_version_positive"),
        sa.CheckConstraint(
            "trigger_type IN ('INITIAL_FULL', 'INCREMENTAL_REFRESH')",
            name="ck_research_package_trigger_type",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'BUILDING', 'READY', 'FAILED')",
            name="ck_research_package_status",
        ),
        sa.CheckConstraint(
            "(version = 1 AND previous_version_id IS NULL) OR "
            "(version > 1 AND previous_version_id IS NOT NULL)",
            name="ck_research_package_lineage",
        ),
        sa.ForeignKeyConstraint(["instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["previous_version_id"],
            ["research_package.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instrument_id",
            "idempotency_key",
            name="uq_research_package_instrument_idempotency_key",
        ),
        sa.UniqueConstraint(
            "instrument_id",
            "version",
            name="uq_research_package_instrument_version",
        ),
    )
    op.create_index(
        "ix_research_package_instrument_id",
        "research_package",
        ["instrument_id"],
    )
    op.create_index(
        "ix_research_package_instrument_version",
        "research_package",
        ["instrument_id", "version"],
    )

    op.create_table(
        "research_module",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("research_package_id", sa.String(length=36), nullable=False),
        sa.Column("origin_module_id", sa.String(length=36), nullable=True),
        sa.Column("module_type", sa.String(length=32), nullable=False),
        sa.Column("module_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_refs", sa.JSON(), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stale_after", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("module_version >= 1", name="ck_research_module_version_positive"),
        sa.CheckConstraint(
            "module_type IN ("
            "'COMPANY', 'BUSINESS', 'INDUSTRY', 'ORDER', 'FINANCIAL', "
            "'EXPECTATION', 'VALUATION', 'RISK', 'CATALYST', 'COMPETITOR', 'MANAGEMENT'"
            ")",
            name="ck_research_module_type",
        ),
        sa.CheckConstraint(
            "status IN ('UNVERIFIED', 'PENDING', 'REFRESHING', 'READY', 'FAILED')",
            name="ck_research_module_status",
        ),
        sa.ForeignKeyConstraint(
            ["origin_module_id"],
            ["research_module.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["research_package_id"],
            ["research_package.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "research_package_id",
            "module_type",
            name="uq_research_module_package_type",
        ),
    )
    op.create_index(
        "ix_research_module_research_package_id",
        "research_module",
        ["research_package_id"],
    )
    op.create_index(
        "ix_research_module_package_type",
        "research_module",
        ["research_package_id", "module_type"],
    )


def downgrade() -> None:
    """Drop WP-03 Research persistence tables."""
    op.drop_index("ix_research_module_package_type", table_name="research_module")
    op.drop_index("ix_research_module_research_package_id", table_name="research_module")
    op.drop_table("research_module")
    op.drop_index("ix_research_package_instrument_version", table_name="research_package")
    op.drop_index("ix_research_package_instrument_id", table_name="research_package")
    op.drop_table("research_package")
