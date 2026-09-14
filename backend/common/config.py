"""ThesisGuard application configuration.

Loads settings from environment variables with sensible defaults for development.
配置层是整个系统的单一配置来源，所有模块通过此处读取环境变量。
Redis 使用三个逻辑 DB：/0 通用、/1 缓存、/2 队列，避免 key 冲突。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "ThesisGuard"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    # SECRET_KEY 仅用于 JWT 签名，生产环境必须通过环境变量覆盖
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [o.strip() for o in self.API_CORS_ORIGINS.split(",") if o.strip()]

    # PostgreSQL
    POSTGRES_USER: str = "thesisguard"
    POSTGRES_PASSWORD: str = "thesisguard"
    POSTGRES_DB: str = "thesisguard"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = ""

    @property
    def async_database_url(self) -> str:
        """Return the async PostgreSQL URL."""
        # 显式 DATABASE_URL 优先，便于 Docker 等环境统一注入连接串
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        """Return the sync PostgreSQL URL (for Alembic)."""
        # Alembic 离线/在线模式都需要同步驱动，这里把 asyncpg 替换为 psycopg2 协议头
        async_url = self.async_database_url
        return async_url.replace("postgresql+asyncpg://", "postgresql://")

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = ""
    REDIS_CACHE_URL: str = ""
    REDIS_QUEUE_URL: str = ""

    @property
    def redis_url_resolved(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def redis_cache_url_resolved(self) -> str:
        if self.REDIS_CACHE_URL:
            return self.REDIS_CACHE_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    @property
    def redis_queue_url_resolved(self) -> str:
        if self.REDIS_QUEUE_URL:
            return self.REDIS_QUEUE_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "thesisguard-documents"
    MINIO_REGION: str = "us-east-1"
    MINIO_SECURE: bool = False

    # Worker
    WORKER_CONCURRENCY: int = 4
    WORKER_LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# 全局单例，所有模块通过 from backend.common.config import settings 引用
settings = get_settings()
