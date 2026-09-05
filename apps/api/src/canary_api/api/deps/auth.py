"""Authentication dependencies: current user extraction from JWT bearer token."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from canary_api.api.deps.config import SettingsDep
from canary_api.api.deps.database import DbSessionDep
from canary_api.application.auth.security import decode_access_token
from canary_api.application.auth.service import AuthService
from canary_api.core.errors import UnauthorizedError
from canary_api.persistence.models.user import User
from canary_api.persistence.repositories.user_repository import UserRepository

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_auth_service(session: DbSessionDep, settings: SettingsDep) -> AuthService:
    """Provide an ``AuthService`` bound to the request's DB session."""

    return AuthService(UserRepository(session), settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[str | None, Depends(_oauth2_scheme)],
    session: DbSessionDep,
    settings: SettingsDep,
) -> User:
    """Resolve the current authenticated user from the bearer token."""

    if token is None:
        raise UnauthorizedError("Missing authentication credentials.")

    user_id = decode_access_token(token, settings=settings)
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
