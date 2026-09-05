"""Centralized translation of domain/application errors to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from canary_api.core.errors import (
    CanaryError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    UnsafeArchiveError,
    ValidationError,
)

_STATUS_BY_ERROR: dict[type[CanaryError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ConflictError: status.HTTP_409_CONFLICT,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    UnsafeArchiveError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Register handlers that map ``CanaryError`` subclasses to HTTP responses."""

    @app.exception_handler(CanaryError)
    async def _handle_canary_error(request: Request, exc: CanaryError) -> JSONResponse:
        status_code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )
