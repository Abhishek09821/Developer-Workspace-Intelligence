"""Project management routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from canary_api.api.deps.auth import CurrentUserDep
from canary_api.api.deps.services import ProjectServiceDep
from canary_api.api.v1.schemas import CreateProjectRequest, ProjectListResponse, ProjectResponse
from canary_api.application.projects.dtos import CreateProjectInput
from canary_api.core.errors import ForbiddenError

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: CreateProjectRequest,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> ProjectResponse:
    """Create a new project owned by the current user."""

    project = await project_service.create_project(
        CreateProjectInput(
            owner_id=current_user.id,
            name=payload.name,
            source_type=payload.source_type,
            description=payload.description,
        )
    )
    return ProjectResponse(**project.__dict__)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> ProjectListResponse:
    """List all projects owned by the current user."""

    projects = await project_service.list_projects(current_user.id)
    items = [ProjectResponse(**p.__dict__) for p in projects]
    return ProjectListResponse(items=items, total=len(items))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> ProjectResponse:
    """Fetch a single project by ID."""

    project = await project_service.get_project(project_id)
    if project.owner_id != current_user.id:
        raise ForbiddenError("You do not have access to this project.")
    return ProjectResponse(**project.__dict__)
