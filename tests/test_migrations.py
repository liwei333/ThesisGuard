"""Migration command regression tests."""

from pathlib import Path


def test_alembic_uses_asyncpg_runtime_not_sync_psycopg_driver() -> None:
    """WP-01 migrations should run with the project's async PostgreSQL stack."""
    env = Path("migrations/env.py").read_text(encoding="utf-8")

    assert "async_engine_from_config" in env
    assert "settings.async_database_url" in env
    assert "from sqlalchemy import engine_from_config" not in env
    assert "settings.sync_database_url" not in env
