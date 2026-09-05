"""Application service for user registration and login."""

from __future__ import annotations

from dataclasses import dataclass

from canary_api.application.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from canary_api.core.config import Settings
from canary_api.core.errors import ConflictError, UnauthorizedError
from canary_api.persistence.models.user import User
from canary_api.persistence.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class RegisterUserInput:
    """Input required to register a new account."""

    email: str
    password: str
    full_name: str | None = None


@dataclass(frozen=True)
class LoginInput:
    """Input required to authenticate an existing account."""

    email: str
    password: str


@dataclass(frozen=True)
class AuthResult:
    """Result of a successful register/login: the user and an access token."""

    user: User
    access_token: str


class AuthService:
    """Use cases for registering and authenticating users."""

    def __init__(self, repository: UserRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    async def register(self, data: RegisterUserInput) -> AuthResult:
        existing = await self._repository.get_by_email(data.email)
        if existing is not None:
            raise ConflictError("A user with this email already exists.")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        user = await self._repository.add(user)
        token = create_access_token(subject=user.id, settings=self._settings)
        return AuthResult(user=user, access_token=token)

    async def login(self, data: LoginInput) -> AuthResult:
        user = await self._repository.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("This account is inactive.")

        token = create_access_token(subject=user.id, settings=self._settings)
        return AuthResult(user=user, access_token=token)
