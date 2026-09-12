"""Tests for configuration management."""

import pytest
from backend.common.config import Settings


@pytest.fixture
def clean_settings(monkeypatch):
    """Override env vars to isolate from .env file for URL construction tests."""
    # Set these to known values so .env file doesn't interfere
    monkeypatch.setenv("POSTGRES_USER", "default_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "default_pass")
    monkeypatch.setenv("POSTGRES_DB", "default_db")
    monkeypatch.setenv("POSTGRES_HOST", "default_host")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("REDIS_HOST", "default_redis")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("API_CORS_ORIGINS", "http://localhost:5173")

    # Clear the lru_cache so we get fresh Settings
    from backend.common.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestSettings:
    """Test Settings configuration."""

    def test_default_app_name(self, clean_settings):
        """Default app name should be ThesisGuard."""
        settings = Settings()
        assert settings.APP_NAME == "ThesisGuard"

    def test_default_version(self, clean_settings):
        """Default version should be 0.1.0."""
        settings = Settings()
        assert settings.APP_VERSION == "0.1.0"

    def test_async_database_url_from_explicit_url(self, clean_settings):
        """When DATABASE_URL is set, it should be used directly."""
        settings = Settings(DATABASE_URL="postgresql+asyncpg://u:p@h:5433/mydb")
        assert settings.async_database_url == "postgresql+asyncpg://u:p@h:5433/mydb"

    def test_async_database_url_construction(self, clean_settings):
        """Async database URL should be constructed from components when no DATABASE_URL."""
        settings = Settings(
            DATABASE_URL="",
            POSTGRES_USER="test",
            POSTGRES_PASSWORD="pass",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="testdb",
        )
        expected = "postgresql+asyncpg://test:pass@localhost:5432/testdb"
        assert settings.async_database_url == expected

    def test_sync_database_url_construction(self, clean_settings):
        """Sync database URL should replace asyncpg protocol."""
        settings = Settings(
            DATABASE_URL="",
            POSTGRES_USER="test",
            POSTGRES_PASSWORD="pass",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_DB="testdb",
        )
        expected = "postgresql://test:pass@localhost:5432/testdb"
        assert settings.sync_database_url == expected

    def test_redis_url_construction(self, clean_settings):
        """Redis URL should be constructed from host and port when no REDIS_URL."""
        settings = Settings(REDIS_URL="", REDIS_HOST="redis-host", REDIS_PORT=6380)
        assert settings.redis_url_resolved == "redis://redis-host:6380/0"

    def test_redis_url_explicit(self, clean_settings):
        """When REDIS_URL is set, it should be used directly."""
        settings = Settings(REDIS_URL="redis://custom:6379/3")
        assert settings.redis_url_resolved == "redis://custom:6379/3"

    def test_cors_origins_default(self, clean_settings):
        """Default CORS origins should include localhost."""
        settings = Settings(API_CORS_ORIGINS="http://localhost:5173")
        assert "localhost:5173" in settings.API_CORS_ORIGINS

    def test_cors_origins_list_property(self, clean_settings):
        """cors_origins_list should parse the string into a list."""
        settings = Settings(API_CORS_ORIGINS="http://a.com,http://b.com")
        assert settings.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_cors_origins_list_empty_filtered(self, clean_settings):
        """Empty entries should be filtered out."""
        settings = Settings(API_CORS_ORIGINS="http://a.com,,http://b.com,")
        assert settings.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_minio_settings(self, clean_settings):
        """MinIO settings should have correct defaults."""
        settings = Settings()
        assert settings.MINIO_BUCKET == "thesisguard-documents"
        assert settings.MINIO_SECURE is False

    def test_worker_settings(self, clean_settings):
        """Worker settings should have correct defaults."""
        settings = Settings()
        assert settings.WORKER_CONCURRENCY == 4
        assert settings.WORKER_LOG_LEVEL == "INFO"
