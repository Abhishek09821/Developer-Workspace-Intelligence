"""Registration and login routes."""

from __future__ import annotations

from fastapi import APIRouter, status

from canary_api.api.deps.auth import AuthServiceDep
from canary_api.api.v1.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from canary_api.application.auth.service import LoginInput, RegisterUserInput

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthServiceDep) -> AuthResponse:
    """Register a new user account and return an access token."""

    result = await auth_service.register(
        RegisterUserInput(email=payload.email, password=payload.password, full_name=payload.full_name)
    )
    return AuthResponse(access_token=result.access_token, user=UserResponse.model_validate(result.user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, auth_service: AuthServiceDep) -> AuthResponse:
    """Authenticate an existing user and return an access token."""

    result = await auth_service.login(LoginInput(email=payload.email, password=payload.password))
    return AuthResponse(access_token=result.access_token, user=UserResponse.model_validate(result.user))
