"""ThesisGuard FastAPI application entry point.

应用工厂模式创建 FastAPI 实例，注册中间件和路由。
启动时确保 MinIO bucket 存在，关闭时释放数据库连接。
新增领域模块时，在下方 include_router 处注册路由。
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apps.api.routers import health, system, tasks
from backend.common.config import settings
from backend.common.db.session import close_db
from backend.common.storage import storage
from backend.instrument.api import router as instrument_router
from backend.research.api import router as research_router
from backend.watchlist.api import router as watchlist_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown events."""
    # 启动时确保 MinIO 存储桶存在（幂等操作）
    storage.ensure_bucket()
    yield
    # 关闭时释放异步引擎连接池
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="论衡 ThesisGuard — Personal Trading Research & Decision System",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS 中间件，允许前端开发服务器跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册各模块路由，统一使用 /api/v1 前缀
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(system.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(instrument_router, prefix="/api/v1")
    app.include_router(research_router, prefix="/api/v1")
    app.include_router(watchlist_router, prefix="/api/v1")

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }

    return app


app = create_app()
