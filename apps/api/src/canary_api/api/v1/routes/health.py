"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from canary_api.api.deps.config import SettingsDep
from canary_api.api.v1.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def get_health(settings: SettingsDep) -> HealthResponse:
    """Return basic liveness information about the running API."""

    return HealthResponse(status="ok", environment=settings.environment)
