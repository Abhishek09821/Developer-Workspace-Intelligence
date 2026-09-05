"""Centralized application configuration.

All runtime configuration must flow through this module. Never read
environment variables directly elsewhere in the codebase - inject a
``Settings`` instance instead (see ``core.deps``/``api.deps``).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CANARY_",
        extra="ignore",
    )

    # --- General ---
    app_name: str = "Canary API"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Database ---
    database_url: str = (
        "postgresql+asyncpg://canary:canary@localhost:5433/canary"
    )
    database_sync_url: str = (
        "postgresql+psycopg://canary:canary@localhost:5433/canary"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 5
    database_echo: bool = False

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- Auth ---
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_ENVIRONMENT"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 7

    # --- CORS ---
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    # --- AI Provider Abstraction ---
    ai_provider: Literal["none", "openai", "anthropic", "bedrock"] = "none"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"

    # --- GitHub Integration ---
    github_client_id: str | None = None
    github_client_secret: str | None = None

    # --- Import / Upload limits ---
    max_zip_upload_size_mb: int = 200
    max_zip_uncompressed_size_mb: int = 1000
    max_zip_entry_count: int = 50_000

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    Cached so repeated dependency-injection lookups don't re-parse the
    environment on every request.
    """

    return Settings()
