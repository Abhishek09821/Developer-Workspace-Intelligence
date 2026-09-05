"""
Shared pytest fixtures for all test levels.

Uses SQLite + aiosqlite so no live PostgreSQL is required.
The pgvector VECTOR column type is not available in SQLite, so we swap it
out for a plain nullable Text column before the tables are created.
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from canary_api.core.config import Settings


# ---------------------------------------------------------------------------
# Test settings — SQLite in-memory, overrides all infra URLs
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        environment="test",
        debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        database_sync_url="sqlite:///:memory:",
        database_echo=False,
        redis_url="redis://localhost:6379/15",
        celery_broker_url="redis://localhost:6379/15",
        celery_result_backend="redis://localhost:6379/15",
        jwt_secret_key="test-secret-key-not-for-production",  # noqa: S106
        log_json=False,
        log_level="WARNING",
    )


# ---------------------------------------------------------------------------
# Engine: patch pgvector VECTOR → Text before table creation
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def engine(test_settings: Settings):
    """Session-scoped in-memory SQLite engine with all tables."""

    # Import models so Base.metadata is populated
    import canary_api.persistence.models  # noqa: F401

    # Patch pgvector VECTOR column so SQLite can create the table
    from sqlalchemy import Text
    from sqlalchemy.orm import mapped_column
    from canary_api.persistence.models.code import CodeEntity
    CodeEntity.embedding = mapped_column("embedding", Text, nullable=True)

    from canary_api.persistence.base import Base

    eng = create_async_engine(test_settings.database_url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


# ---------------------------------------------------------------------------
# Per-test DB session — rolled back after each test for isolation
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(engine):
    """Yields a transactional session rolled back after each test."""

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# FastAPI ASGI test client — wired to the same in-memory DB
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(test_settings: Settings, engine):
    """Async HTTP client with the test DB wired in via app.state."""

    from canary_api.core.config import get_settings
    from canary_api.main import create_app

    # Override the cached settings singleton for this test run
    get_settings.cache_clear()

    app = create_app()

    # Manually set app.state so lifespan doesn't create a second engine
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    app.state.engine = engine
    app.state.session_factory = factory

    # Patch get_settings so the app uses test config (no real DB URL)
    import unittest.mock as mock
    with mock.patch("canary_api.core.config.get_settings", return_value=test_settings), \
         mock.patch("canary_api.api.deps.config.get_settings", return_value=test_settings):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

    get_settings.cache_clear()
