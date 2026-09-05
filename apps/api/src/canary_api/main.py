"""FastAPI application entrypoint.

Run locally with:
    uvicorn canary_api.main:app --reload
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from canary_api.api.exception_handlers import register_exception_handlers
from canary_api.api.v1.router import api_router
from canary_api.core.config import get_settings
from canary_api.logging import configure_logging, get_logger
from canary_api.persistence.session import create_engine, create_session_factory

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup/shutdown: initialize and dispose DB resources."""

    settings = get_settings()
    configure_logging(settings)

    engine = create_engine(settings)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    logger.info("canary_api.startup", environment=settings.environment)
    try:
        yield
    finally:
        await engine.dispose()
        logger.info("canary_api.shutdown")


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application instance."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
