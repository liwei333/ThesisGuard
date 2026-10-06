"""Knowledge base tables.

Revision ID: 20261006_005
Revises: 20260914_004
Create Date: 2026-10-06

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20261006_005"
down_revision = "000000000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("weknora_kb_id", sa.String(128), nullable=True),
        sa.Column("weknora_version", sa.String(64), nullable=True),
        sa.Column("document_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("weknora_kb_id", name="uq_knowledge_base_weknora_kb_id"),
        sa.CheckConstraint(
            "category IN ('TRADING_METHOD', 'COMPANY_INDUSTRY', "
            "'POLICY_DOCUMENT', 'PERSONAL_REVIEW')",
            name="ck_knowledge_base_category",
        ),
    )
    op.create_index("ix_knowledge_base_category", "knowledge_base", ["category"])
    op.create_index("ix_knowledge_base_status", "knowledge_base", ["status"])

    op.create_table(
        "knowledge_document",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "knowledge_base_id",
            sa.String(36),
            sa.ForeignKey("knowledge_base.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "source_document_version_id",
            sa.String(36),
            sa.ForeignKey("source_document_version.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("object_key", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(128), nullable=False),
        sa.Column("media_type", sa.String(128), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=False),
        sa.Column("processing_status", sa.String(32), nullable=False),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("weknora_document_id", sa.String(128), nullable=True),
        sa.Column("index_generation", sa.Integer, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata_json",
            sa.JSON,
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "processing_status IN ('PENDING', 'SUBMITTING', 'PROCESSING', "
            "'READY', 'FAILED', 'RETIRED')",
            name="ck_knowledge_document_processing_status",
        ),
        sa.UniqueConstraint(
            "knowledge_base_id",
            "weknora_document_id",
            name="uq_knowledge_document_weknora_id",
        ),
    )
    op.create_index("ix_knowledge_document_kb_id", "knowledge_document", ["knowledge_base_id"])
    op.create_index(
        "ix_knowledge_document_processing_status",
        "knowledge_document",
        ["processing_status"],
    )
    op.create_index(
        "ix_knowledge_document_source_version",
        "knowledge_document",
        ["source_document_version_id"],
    )

    op.create_table(
        "knowledge_import_task",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "knowledge_document_id",
            sa.String(36),
            sa.ForeignKey("knowledge_document.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_hash", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("weknora_task_id", sa.String(128), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')",
            name="ck_knowledge_import_task_status",
        ),
        sa.UniqueConstraint(
            "knowledge_document_id",
            "idempotency_key",
            name="uq_knowledge_import_task_idempotency",
        ),
    )
    op.create_index(
        "ix_knowledge_import_task_document",
        "knowledge_import_task",
        ["knowledge_document_id"],
    )
    op.create_index(
        "ix_knowledge_import_task_status",
        "knowledge_import_task",
        ["status"],
    )

    op.create_table(
        "knowledge_instrument_link",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "knowledge_base_id",
            sa.String(36),
            sa.ForeignKey("knowledge_base.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "instrument_id",
            sa.String(36),
            sa.ForeignKey("instrument.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "link_metadata",
            sa.JSON,
            nullable=True,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "knowledge_base_id",
            "instrument_id",
            name="uq_knowledge_instrument_link",
        ),
    )
    op.create_index(
        "ix_knowledge_instrument_link_instrument",
        "knowledge_instrument_link",
        ["instrument_id"],
    )


def downgrade() -> None:
    op.drop_table("knowledge_instrument_link")
    op.drop_table("knowledge_import_task")
    op.drop_table("knowledge_document")
    op.drop_table("knowledge_base")
