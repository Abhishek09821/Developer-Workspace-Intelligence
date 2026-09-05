"""Unit tests for the Project domain entity."""

from __future__ import annotations

import uuid
import pytest

from canary_api.domain.projects.entities import Project
from canary_api.domain.projects.enums import ProjectSourceType, ProjectStatus


class TestProjectEntity:
    def test_create_sets_created_status(self):
        project = Project.create(
            owner_id=uuid.uuid4(),
            name="my-app",
            source_type=ProjectSourceType.LOCAL_WORKSPACE,
        )
        assert project.status == ProjectStatus.CREATED

    def test_create_assigns_uuid(self):
        p1 = Project.create(owner_id=uuid.uuid4(), name="p1", source_type=ProjectSourceType.ZIP_UPLOAD)
        p2 = Project.create(owner_id=uuid.uuid4(), name="p2", source_type=ProjectSourceType.ZIP_UPLOAD)
        assert p1.id != p2.id

    def test_create_stores_description(self):
        project = Project.create(
            owner_id=uuid.uuid4(),
            name="test",
            source_type=ProjectSourceType.GITHUB_REPOSITORY,
            description="A test project",
        )
        assert project.description == "A test project"

    def test_transition_to_changes_status(self):
        project = Project.create(
            owner_id=uuid.uuid4(),
            name="test",
            source_type=ProjectSourceType.LOCAL_WORKSPACE,
        )
        project.transition_to(ProjectStatus.IMPORTING)
        assert project.status == ProjectStatus.IMPORTING

    def test_transition_to_updates_timestamp(self):
        project = Project.create(
            owner_id=uuid.uuid4(),
            name="test",
            source_type=ProjectSourceType.LOCAL_WORKSPACE,
        )
        before = project.updated_at
        import time; time.sleep(0.01)
        project.transition_to(ProjectStatus.READY)
        assert project.updated_at >= before


class TestProjectService:
    """Integration between ProjectService and an in-memory repository."""

    @pytest.mark.asyncio
    async def test_create_project_trims_name(self):
        from unittest.mock import AsyncMock
        from canary_api.application.projects.service import ProjectService
        from canary_api.application.projects.dtos import CreateProjectInput

        repo = AsyncMock()
        repo.add.side_effect = lambda p: p  # echo back
        svc = ProjectService(repo)

        result = await svc.create_project(
            CreateProjectInput(
                owner_id=uuid.uuid4(),
                name="  padded  ",
                source_type=ProjectSourceType.LOCAL_WORKSPACE,
            )
        )
        assert result.name == "padded"

    @pytest.mark.asyncio
    async def test_create_project_empty_name_raises(self):
        from unittest.mock import AsyncMock
        from canary_api.application.projects.service import ProjectService
        from canary_api.application.projects.dtos import CreateProjectInput
        from canary_api.core.errors import ValidationError

        repo = AsyncMock()
        svc = ProjectService(repo)

        with pytest.raises(ValidationError):
            await svc.create_project(
                CreateProjectInput(
                    owner_id=uuid.uuid4(),
                    name="   ",
                    source_type=ProjectSourceType.ZIP_UPLOAD,
                )
            )
