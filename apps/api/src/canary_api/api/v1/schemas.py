"""Pydantic request/response schemas for API v1."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from canary_api.domain.projects.enums import ProjectSourceType, ProjectStatus


class HealthResponse(BaseModel):
    """Response body for the liveness/health endpoint."""

    status: str
    environment: str
    version: str = "0.1.0"


# --- Auth ---


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None
    is_active: bool


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Projects ---


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source_type: ProjectSourceType
    description: str | None = Field(default=None, max_length=4000)


class ProjectResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None
    source_type: ProjectSourceType
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
