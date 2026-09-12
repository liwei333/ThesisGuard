"""Create instrument and watchlist tables.

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-09-12 00:00:00.000000

"""

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000002"
down_revision: str | None = "000000000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create WP-02 tables and seed initial instruments."""
    op.create_table(
        "instrument",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("instrument_type", sa.String(length=32), nullable=False),
        sa.Column("exchange", sa.String(length=32), nullable=False),
        sa.Column("market", sa.String(length=32), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=False),
        sa.Column("sector", sa.String(length=64), nullable=True),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", "exchange", name="uq_instrument_symbol_exchange"),
    )
    op.create_index("ix_instrument_symbol", "instrument", ["symbol"])
    op.create_index("ix_instrument_name", "instrument", ["name"])

    op.create_table(
        "instrument_alias",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("instrument_id", sa.String(length=36), nullable=False),
        sa.Column("alias", sa.String(length=128), nullable=False),
        sa.Column("alias_type", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id", "alias", name="uq_instrument_alias"),
    )
    op.create_index("ix_instrument_alias_instrument_id", "instrument_alias", ["instrument_id"])
    op.create_index("ix_instrument_alias_alias", "instrument_alias", ["alias"])

    op.create_table(
        "instrument_tag",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("instrument_id", sa.String(length=36), nullable=False),
        sa.Column("tag", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id", "tag", name="uq_instrument_tag"),
    )
    op.create_index("ix_instrument_tag_instrument_id", "instrument_tag", ["instrument_id"])
    op.create_index("ix_instrument_tag_tag", "instrument_tag", ["tag"])

    op.create_table(
        "instrument_relation",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_instrument_id", sa.String(length=36), nullable=False),
        sa.Column("target_instrument_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_instrument_id",
            "target_instrument_id",
            "relation_type",
            name="uq_instrument_relation",
        ),
    )
    op.create_index(
        "ix_instrument_relation_source_instrument_id",
        "instrument_relation",
        ["source_instrument_id"],
    )
    op.create_index(
        "ix_instrument_relation_target_instrument_id",
        "instrument_relation",
        ["target_instrument_id"],
    )

    op.create_table(
        "watchlist_item",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("instrument_id", sa.String(length=36), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("classification_confidence", sa.Integer(), nullable=False),
        sa.Column("classification_reason", sa.Text(), nullable=False),
        sa.Column("research_status", sa.String(length=32), nullable=False),
        sa.Column("research_score", sa.Integer(), nullable=True),
        sa.Column("thesis_summary", sa.Text(), nullable=True),
        sa.Column("agent_action", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["instrument_id"], ["instrument.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instrument_id", name="uq_watchlist_instrument"),
    )
    op.create_index("ix_watchlist_item_instrument_id", "watchlist_item", ["instrument_id"])

    seed_instruments()


def downgrade() -> None:
    """Drop WP-02 tables."""
    op.drop_index("ix_watchlist_item_instrument_id", table_name="watchlist_item")
    op.drop_table("watchlist_item")
    op.drop_index("ix_instrument_relation_target_instrument_id", table_name="instrument_relation")
    op.drop_index("ix_instrument_relation_source_instrument_id", table_name="instrument_relation")
    op.drop_table("instrument_relation")
    op.drop_index("ix_instrument_tag_tag", table_name="instrument_tag")
    op.drop_index("ix_instrument_tag_instrument_id", table_name="instrument_tag")
    op.drop_table("instrument_tag")
    op.drop_index("ix_instrument_alias_alias", table_name="instrument_alias")
    op.drop_index("ix_instrument_alias_instrument_id", table_name="instrument_alias")
    op.drop_table("instrument_alias")
    op.drop_index("ix_instrument_name", table_name="instrument")
    op.drop_index("ix_instrument_symbol", table_name="instrument")
    op.drop_table("instrument")


def seed_instruments() -> None:
    """Seed a tiny catalog for WP-02 local development."""
    now = datetime.now(UTC)
    instruments = [
        {
            "id": "11111111-1111-4111-8111-111111111111",
            "symbol": "301128",
            "name": "强瑞技术",
            "instrument_type": "STOCK",
            "exchange": "SZSE",
            "market": "CN",
            "currency": "CNY",
            "sector": "先进制造",
            "industry": "AI液冷与半导体设备",
            "description": "AI服务器液冷、半导体精密零部件与自动化设备标的。",
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "22222222-2222-4222-8222-222222222222",
            "symbol": "301018",
            "name": "申菱环境",
            "instrument_type": "STOCK",
            "exchange": "SZSE",
            "market": "CN",
            "currency": "CNY",
            "sector": "先进制造",
            "industry": "液冷温控",
            "description": "数据中心液冷与工业温控设备标的。",
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "33333333-3333-4333-8333-333333333333",
            "symbol": "000722",
            "name": "湖南发展",
            "instrument_type": "STOCK",
            "exchange": "SZSE",
            "market": "CN",
            "currency": "CNY",
            "sector": "公用事业",
            "industry": "电力与题材交易",
            "description": "电力题材、市场记忆与情绪周期观察标的。",
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        },
    ]
    aliases = [
        ("a1111111-1111-4111-8111-111111111111", instruments[0]["id"], "强瑞", "NAME"),
        ("a2222222-2222-4222-8222-222222222222", instruments[1]["id"], "申菱", "NAME"),
        ("a3333333-3333-4333-8333-333333333333", instruments[2]["id"], "湖南", "NAME"),
    ]
    tags = [
        ("t1111111-1111-4111-8111-111111111111", instruments[0]["id"], "AI液冷"),
        ("t1111111-1111-4111-8111-111111111112", instruments[0]["id"], "机构趋势"),
        ("t2222222-2222-4222-8222-222222222222", instruments[1]["id"], "机构趋势"),
        ("t3333333-3333-4333-8333-333333333333", instruments[2]["id"], "游资情绪"),
    ]

    instrument_table = sa.table(
        "instrument",
        sa.column("id"),
        sa.column("symbol"),
        sa.column("name"),
        sa.column("instrument_type"),
        sa.column("exchange"),
        sa.column("market"),
        sa.column("currency"),
        sa.column("sector"),
        sa.column("industry"),
        sa.column("description"),
        sa.column("status"),
        sa.column("created_at"),
        sa.column("updated_at"),
    )
    alias_table = sa.table(
        "instrument_alias",
        sa.column("id"),
        sa.column("instrument_id"),
        sa.column("alias"),
        sa.column("alias_type"),
    )
    tag_table = sa.table(
        "instrument_tag",
        sa.column("id"),
        sa.column("instrument_id"),
        sa.column("tag"),
    )

    op.bulk_insert(instrument_table, instruments)
    op.bulk_insert(
        alias_table,
        [
            {"id": item[0], "instrument_id": item[1], "alias": item[2], "alias_type": item[3]}
            for item in aliases
        ],
    )
    op.bulk_insert(
        tag_table,
        [{"id": item[0], "instrument_id": item[1], "tag": item[2]} for item in tags],
    )
