"""WP-04 Evidence Alembic migration contract tests."""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator
from uuid import uuid4

import asyncpg
import pytest_asyncio
from sqlalchemy.engine import make_url

DEFAULT_ADMIN_DATABASE_URL = (
    "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
)
WP04_TABLES = {
    "source_document",
    "source_document_version",
    "evidence_series",
    "evidence_version",
    "evidence_source_locator",
    "evidence_instrument_link",
    "evidence_corroboration_link",
    "evidence_derivation_link",
    "evidence_idempotency_record",
    "evidence_audit_event",
}


@pytest_asyncio.fixture
async def disposable_database_url() -> AsyncIterator[str]:
    """Create a disposable PostgreSQL database for migration-cycle checks."""
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", DEFAULT_ADMIN_DATABASE_URL))
    test_db_name = f"tg_wp04_migration_{uuid4().hex}"
    admin_db = admin_url.database or "postgres"
    admin_conn = await asyncpg.connect(
        user=admin_url.username,
        password=admin_url.password,
        host=admin_url.host or "127.0.0.1",
        port=admin_url.port or 5432,
        database=admin_db,
    )
    await admin_conn.execute(f'CREATE DATABASE "{test_db_name}"')
    await admin_conn.close()

    try:
        yield admin_url.set(database=test_db_name).render_as_string(hide_password=False)
    finally:
        cleanup_conn = await asyncpg.connect(
            user=admin_url.username,
            password=admin_url.password,
            host=admin_url.host or "127.0.0.1",
            port=admin_url.port or 5432,
            database=admin_db,
        )
        await cleanup_conn.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1 AND pid <> pg_backend_pid()
            """,
            test_db_name,
        )
        await cleanup_conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        await cleanup_conn.close()


def run_alembic(database_url: str, *args: str) -> None:
    """Run Alembic against a disposable database."""
    subprocess.run(  # noqa: ASYNC221
        ["alembic", "-c", "migrations/alembic.ini", *args],
        check=True,
        env={**os.environ, "DATABASE_URL": database_url},
        capture_output=True,
        text=True,
    )


async def table_names(conn: asyncpg.Connection) -> set[str]:
    """Return public table names."""
    rows = await conn.fetch(
        """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        """
    )
    return {row["tablename"] for row in rows}


async def constraint_names(conn: asyncpg.Connection) -> set[str]:
    """Return public constraint names."""
    rows = await conn.fetch(
        """
        SELECT conname
        FROM pg_constraint
        WHERE connamespace = 'public'::regnamespace
        """
    )
    return {row["conname"] for row in rows}


async def index_names(conn: asyncpg.Connection) -> set[str]:
    """Return public index names."""
    rows = await conn.fetch(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        """
    )
    return {row["indexname"] for row in rows}


async def test_evidence_migration_round_trip_preserves_prior_tables_and_contract_objects(
    disposable_database_url: str,
) -> None:
    """Revision 4 upgrades and downgrades without touching WP01-WP03 tables."""
    run_alembic(disposable_database_url, "upgrade", "000000000003")
    conn = await asyncpg.connect(disposable_database_url.replace("+asyncpg", ""))
    try:
        pre_tables = await table_names(conn)
        assert {"instrument", "watchlist_item", "research_package", "research_module"}.issubset(
            pre_tables
        )
        assert WP04_TABLES.isdisjoint(pre_tables)
        assert "research_module_evidence_link" not in pre_tables
    finally:
        await conn.close()

    run_alembic(disposable_database_url, "upgrade", "000000000004")
    conn = await asyncpg.connect(disposable_database_url.replace("+asyncpg", ""))
    try:
        upgraded_tables = await table_names(conn)
        assert upgraded_tables - pre_tables == WP04_TABLES
        assert WP04_TABLES.issubset(upgraded_tables)
        assert "research_module_evidence_link" not in upgraded_tables

        constraints = await constraint_names(conn)
        indexes = await index_names(conn)
        assert {
            "source_document_pkey",
            "source_document_version_pkey",
            "evidence_series_pkey",
            "evidence_version_pkey",
            "evidence_idempotency_record_pkey",
            "ck_source_document_identity_present",
            "ck_source_document_source_type",
            "ck_source_document_version_source_grade",
            "ck_evidence_version_status_audit_null_only_initial",
            "ck_evidence_version_initial_state",
            "ck_evidence_version_supersedes_requires_audit",
            "ck_evidence_version_replacement_v1_kind",
            "ck_evidence_version_correction_requires_predecessor",
            "ck_evidence_version_tombstone_requires_predecessor",
            "uq_source_document_version_fingerprint",
            "uq_evidence_series_identity_hash",
            "uq_evidence_version_series_version",
        }.issubset(constraints)
        assert {
            "uq_source_document_external_identity",
            "uq_source_document_url_identity",
            "ix_evidence_version_series_id",
            "ix_evidence_idempotency_record_request_hash",
        }.issubset(indexes)

        await conn.execute(
            """
            INSERT INTO source_document (
                id, publisher_key, publisher_name, source_type,
                external_document_id, canonical_url, created_at, created_by_actor
            )
            VALUES (
                'migration-valid-source', 'publisher', 'Publisher',
                'COMPANY_ANNOUNCEMENT', 'external-1', NULL, now(), 'LLM_PROPOSAL'
            )
            """
        )
        await conn.execute(
            """
            INSERT INTO source_document (
                id, publisher_key, publisher_name, source_type,
                external_document_id, canonical_url, created_at, created_by_actor
            )
            VALUES (
                'migration-valid-url-source', 'publisher', 'Publisher',
                'WEB_PAGE', NULL, 'https://example.test/source', now(), 'IMPORTER'
            )
            """
        )

        removed_source_type = "EXCHANGE_" + "ANNOUNCEMENT"
        for statement in (
            f"""
            INSERT INTO source_document (
                id, publisher_key, publisher_name, source_type,
                external_document_id, canonical_url, created_at, created_by_actor
            )
            VALUES (
                'migration-bad-source-type', 'publisher', 'Publisher',
                '{removed_source_type}', 'external-bad', NULL, now(), 'IMPORTER'
            )
            """,
            """
            INSERT INTO source_document (
                id, publisher_key, publisher_name, source_type,
                external_document_id, canonical_url, created_at, created_by_actor
            )
            VALUES (
                'migration-missing-identity', 'publisher', 'Publisher',
                'WEB_PAGE', NULL, NULL, now(), 'IMPORTER'
            )
            """,
        ):
            try:
                await conn.execute(statement)
            except asyncpg.PostgresError:
                pass
            else:  # pragma: no cover - assertion path
                raise AssertionError("expected PostgreSQL to reject invalid migration probe")
    finally:
        await conn.close()

    run_alembic(disposable_database_url, "downgrade", "000000000003")
    conn = await asyncpg.connect(disposable_database_url.replace("+asyncpg", ""))
    try:
        downgraded_tables = await table_names(conn)
        assert {"instrument", "watchlist_item", "research_package", "research_module"}.issubset(
            downgraded_tables
        )
        assert WP04_TABLES.isdisjoint(downgraded_tables)
        version = await conn.fetchval("SELECT version_num FROM alembic_version")
        assert version == "000000000003"
    finally:
        await conn.close()

    run_alembic(disposable_database_url, "upgrade", "head")
    conn = await asyncpg.connect(disposable_database_url.replace("+asyncpg", ""))
    try:
        assert WP04_TABLES.issubset(await table_names(conn))
        version = await conn.fetchval("SELECT version_num FROM alembic_version")
        assert version == "000000000004"
    finally:
        await conn.close()
