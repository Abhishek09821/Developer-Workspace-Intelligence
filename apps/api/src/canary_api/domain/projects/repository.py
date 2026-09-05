"""Repository port (interface) for Project persistence.

The domain/application layers depend only on this abstract interface.
Concrete implementations live in ``canary_api.persistence.repositories``
and are provided via dependency injection.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from canary_api.domain.projects.entities import Project


class ProjectRepository(ABC):
    """Persistence port for the ``Project`` aggregate."""

    @abstractmethod
    async def add(self, project: Project) -> Project:
        """Persist a new project."""

    @abstractmethod
    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Fetch a project by its identifier, or ``None`` if not found."""

    @abstractmethod
    async def list_for_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """List all projects owned by a given user."""

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """Persist changes to an existing project."""
