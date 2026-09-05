"""Password hashing and JWT token helpers.

This is the foundation for authentication. It intentionally covers only
password hashing + token issuance/verification for this phase; route
protection wiring lives in ``api.deps.auth``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from canary_api.core.config import Settings
from canary_api.core.errors import UnauthorizedError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""

    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""

    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, subject: uuid.UUID, settings: Settings) -> str:
    """Create a signed JWT access token for the given user ID."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, *, settings: Settings) -> uuid.UUID:
    """Decode and validate a JWT access token, returning the user ID.

    Raises ``UnauthorizedError`` if the token is invalid, expired, or
    malformed.
    """

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc

    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("Token missing subject claim.")

    try:
        return uuid.UUID(subject)
    except ValueError as exc:
        raise UnauthorizedError("Token subject is not a valid user ID.") from exc
