"""ThesisGuard FastAPI application entry point."""

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
    # Startup
    storage.ensure_bucket()
    yield
    # Shutdown
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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
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
