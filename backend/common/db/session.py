"""SQLAlchemy async session and engine configuration.

提供全局异步引擎与 Session 工厂，FastAPI 通过 get_db 依赖注入获取 Session。
注意：get_db 在 yield 后自动 commit，异常时自动 rollback，确保事务边界清晰。
生产环境使用 Alembic 管理迁移，init_db 仅作为开发期建表兜底。
"""

from collections.abc import AsyncGenerator

from backend.common.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# 全局异步引擎，pool_pre_ping 防止连接池拿到断开的连接
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session 工厂：expire_on_commit=False 避免 commit 后再访问属性触发额外查询
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session.

    使用 try/except/finally 保证：
    - 正常路径 yield 后 commit
    - 异常路径 rollback 后重新抛出
    - 无论成功与否都关闭 session，避免连接泄漏
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables)."""
    # Import all models to register them with Base metadata
    from backend.common.db import models_registry  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
