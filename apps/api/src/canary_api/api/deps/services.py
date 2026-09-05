"""Application service dependency providers.

These wire together repositories (persistence) and application services,
keeping route handlers free of direct persistence knowledge.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from canary_api.api.deps.database import DbSessionDep
from canary_api.application.projects.service import ProjectService
from canary_api.persistence.repositories.project_repository import SqlAlchemyProjectRepository


def get_project_service(session: DbSessionDep) -> ProjectService:
    """Provide a ``ProjectService`` bound to the request's DB session."""

    repository = SqlAlchemyProjectRepository(session)
    return ProjectService(repository)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
