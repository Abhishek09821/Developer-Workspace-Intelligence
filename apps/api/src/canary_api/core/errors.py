"""Centralized application error hierarchy.

Domain and application layers raise these typed exceptions. The API layer
translates them into HTTP responses in a single place
(``api.exception_handlers``), so route handlers never need to know about
HTTP status codes.
"""

from __future__ import annotations


class CanaryError(Exception):
    """Base class for all application-raised errors."""

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(CanaryError):
    """Raised when a requested resource does not exist."""


class ValidationError(CanaryError):
    """Raised when input fails domain-level validation."""


class ConflictError(CanaryError):
    """Raised when an operation conflicts with current state."""


class UnauthorizedError(CanaryError):
    """Raised when authentication is missing or invalid."""


class ForbiddenError(CanaryError):
    """Raised when an authenticated principal lacks permission."""


class UnsafeArchiveError(CanaryError):
    """Raised when an uploaded archive fails security validation."""
