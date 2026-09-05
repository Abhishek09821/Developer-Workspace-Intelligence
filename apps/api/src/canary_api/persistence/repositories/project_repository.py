"""SQLAlchemy-backed implementation of ``ProjectRepository``."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from canary_api.domain.projects.entities import Project as ProjectEntity
from canary_api.domain.projects.repository import ProjectRepository
from canary_api.persistence.models.project import Project as ProjectModel


class SqlAlchemyProjectRepository(ProjectRepository):
    """Persists ``Project`` aggregates using SQLAlchemy's async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, project: ProjectEntity) -> ProjectEntity:
        model = _to_model(project)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)

    async def get_by_id(self, project_id: uuid.UUID) -> ProjectEntity | None:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def list_for_owner(self, owner_id: uuid.UUID) -> list[ProjectEntity]:
        result = await self._session.execute(
            select(ProjectModel)
            .where(ProjectModel.owner_id == owner_id, ProjectModel.is_archived.is_(False))
            .order_by(ProjectModel.created_at.desc())
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def update(self, project: ProjectEntity) -> ProjectEntity:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one()
        model.name = project.name
        model.description = project.description
        model.status = project.status
        await self._session.flush()
        return _to_entity(model)


def _to_model(entity: ProjectEntity) -> ProjectModel:
    return ProjectModel(
        id=entity.id,
        owner_id=entity.owner_id,
        name=entity.name,
        description=entity.description,
        source_type=entity.source_type,
        status=entity.status,
    )


def _to_entity(model: ProjectModel) -> ProjectEntity:
    return ProjectEntity(
        id=model.id,
        owner_id=model.owner_id,
        name=model.name,
        description=model.description,
        source_type=model.source_type,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
