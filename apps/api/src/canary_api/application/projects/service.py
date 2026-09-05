"""Application service for Project use cases.

Route handlers call into this service; the service coordinates domain
entities and repository ports. No SQLAlchemy or FastAPI imports belong
here.
"""

from __future__ import annotations

import uuid

from canary_api.application.projects.dtos import CreateProjectInput
from canary_api.core.errors import NotFoundError, ValidationError
from canary_api.domain.projects.entities import Project
from canary_api.domain.projects.repository import ProjectRepository


class ProjectService:
    """Use cases for creating, listing, and retrieving projects."""

    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def create_project(self, data: CreateProjectInput) -> Project:
        """Create a new project in the ``CREATED`` state."""

        name = data.name.strip()
        if not name:
            raise ValidationError("Project name must not be empty.")

        project = Project.create(
            owner_id=data.owner_id,
            name=name,
            source_type=data.source_type,
            description=data.description,
        )
        return await self._repository.add(project)

    async def get_project(self, project_id: uuid.UUID) -> Project:
        """Fetch a project by ID, raising ``NotFoundError`` if missing."""

        project = await self._repository.get_by_id(project_id)
        if project is None:
            raise NotFoundError(f"Project {project_id} not found.")
        return project

    async def list_projects(self, owner_id: uuid.UUID) -> list[Project]:
        """List all non-archived projects owned by ``owner_id``."""

        return await self._repository.list_for_owner(owner_id)
