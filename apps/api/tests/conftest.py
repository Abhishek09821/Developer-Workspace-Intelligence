"""
Shared pytest fixtures for all test levels.

Architecture:
  - Unit tests  (tests/unit/)          — pure Python, no DB
  - Integration tests (tests/integration/) — real PostgreSQL via Docker

Integration tests require postgres on localhost:5433:
    docker compose up postgres -d

Each integration test gets its own fresh asyncpg connection (NullPool)
to avoid event-loop and "operation in progress" issues with asyncpg.
The test database (canary_test) is created once per session and dropped
on teardown.

Settings are overridden via a pytest fixture that clears the lru_cache
and injects test values, covering every call site.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from canary_api.core.config import Settings

# ---------------------------------------------------------------------------
# Test database URL
# ---------------------------------------------------------------------------

_DEFAULT_TEST_DB = "postgresql+asyncpg://canary:canary@localhost:5433/canary_test"
TEST_DB_URL = os.environ.get("CANARY_TEST_DATABASE_URL", _DEFAULT_TEST_DB)


# ---------------------------------------------------------------------------
# Test settings fixture (session-scoped — same object reused)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        environment="test",
        debug=True,
        database_url=TEST_DB_URL,
        database_sync_url=TEST_DB_URL.replace("+asyncpg", "+psycopg"),
        database_echo=False,
        redis_url="redis://localhost:6379/15",
        celery_broker_url="redis://localhost:6379/15",
        celery_result_backend="redis://localhost:6379/15",
        jwt_secret_key="test-secret-key-not-for-production",  # noqa: S106
        log_json=False,
        log_level="WARNING",
    )


# ---------------------------------------------------------------------------
# Create canary_test database once; migrate; drop on teardown
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def _test_database(test_settings: Settings):
    """Create canary_test, run migrations, yield, drop."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine as _cae

    admin_url = TEST_DB_URL.rsplit("/", 1)[0] + "/canary"
    admin_eng = _cae(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with admin_eng.connect() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS canary_test"))
        await conn.execute(text("CREATE DATABASE canary_test"))
    await admin_eng.dispose()

    # Run Alembic in a subprocess so it uses its own event loop
    api_dir = os.path.dirname(os.path.dirname(__file__))  # apps/api/
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=api_dir,
        env={**os.environ, "CANARY_DATABASE_URL": TEST_DB_URL,
             "PYTHONPATH": os.path.join(api_dir, "src")},
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Alembic migration failed:\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}")

    yield  # tests run here

    # Teardown
    admin_eng2 = _cae(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with admin_eng2.connect() as conn:
        await conn.execute(text(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = 'canary_test' AND pid <> pg_backend_pid()"
        ))
        await conn.execute(text("DROP DATABASE IF EXISTS canary_test"))
    await admin_eng2.dispose()


# ---------------------------------------------------------------------------
# Per-test async engine using NullPool — avoids asyncpg event-loop issues
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def engine(_test_database):
    """Fresh NullPool engine per test — no connection reuse across event loops."""
    eng = create_async_engine(TEST_DB_URL, poolclass=NullPool, echo=False)
    yield eng
    await eng.dispose()


# ---------------------------------------------------------------------------
# Per-test DB session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(engine):
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# FastAPI ASGI test client — fresh engine + overridden settings per test
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(test_settings: Settings, engine):
    """
    Async HTTP client with:
      - test_settings injected at every call site
      - fresh NullPool engine wired into app.state
    """
    from unittest.mock import patch
    from canary_api.core import config as cfg_module
    from canary_api.api.deps import config as dep_cfg_module
    from canary_api.main import create_app

    # Clear lru_cache so our patched version is used
    cfg_module.get_settings.cache_clear()

    app = create_app()
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    app.state.engine = engine
    app.state.session_factory = factory

    with patch.object(cfg_module, "get_settings", return_value=test_settings), \
         patch.object(dep_cfg_module, "get_settings", return_value=test_settings):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac

    cfg_module.get_settings.cache_clear()