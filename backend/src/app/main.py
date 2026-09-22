from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.errors import DomainError
from app.core.logging import configure_logging
from app.shared.db.session import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.app_log_level)
    init_engine(settings)
    Path(settings.resolved_data_root()).mkdir(parents=True, exist_ok=True)
    Path(settings.resolved_index_root()).mkdir(parents=True, exist_ok=True)
    yield
    await dispose_engine()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="AIC Video Retrieval",
        version="0.1.0",
        description="Agentic video retrieval backend (FastAPI clean architecture).",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.features.analysis.presentation.api.v1 import router as analysis_router
    from app.features.dashboard.presentation.api.v1 import router as dashboard_router
    from app.features.evaluation.presentation.api.v1 import router as evaluation_router
    from app.features.history.presentation.api.v1 import router as history_router
    from app.features.search_run.presentation.api.v1 import router as runs_router
    from app.features.video_search.presentation.api.v1 import (
        router as video_router,
    )
    from app.features.video_search.presentation.api.v1 import (
        tools_router as video_tools_router,
    )

    api_prefix = "/api/v1"
    app.include_router(video_router, prefix=api_prefix)
    app.include_router(video_tools_router, prefix=api_prefix)
    app.include_router(runs_router, prefix=api_prefix)
    app.include_router(dashboard_router, prefix=api_prefix)
    app.include_router(history_router, prefix=api_prefix)
    app.include_router(analysis_router, prefix=api_prefix)
    app.include_router(evaluation_router, prefix=api_prefix)

    @app.get("/api/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request, exc: DomainError):  # type: ignore[no-untyped-def]
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.to_payload()},
        )

    return app


app = create_app()
