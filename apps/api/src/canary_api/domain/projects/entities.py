"""Project domain entity.

This is a plain-Python representation of a Project, independent of the
ORM/persistence layer. Application services operate on this type; the
persistence layer maps to/from SQLAlchemy models.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from canary_api.domain.common.ids import new_id
from canary_api.domain.projects.enums import ProjectSourceType, ProjectStatus


@dataclass
class Project:
    """A software project registered for analysis by Canary."""

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str | None
    source_type: ProjectSourceType
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        owner_id: uuid.UUID,
        name: str,
        source_type: ProjectSourceType,
        description: str | None = None,
    ) -> "Project":
        """Factory for a brand-new project in the ``CREATED`` state."""

        now = datetime.now(timezone.utc)
        return cls(
            id=new_id(),
            owner_id=owner_id,
            name=name,
            description=description,
            source_type=source_type,
            status=ProjectStatus.CREATED,
            created_at=now,
            updated_at=now,
        )

    def transition_to(self, status: ProjectStatus) -> None:
        """Move the project to a new lifecycle status.

        This is intentionally permissive at the domain layer for the
        foundation phase; stricter transition validation belongs to the
        application service once the scanning pipeline exists.
        """

        self.status = status
        self.updated_at = datetime.now(timezone.utc)
