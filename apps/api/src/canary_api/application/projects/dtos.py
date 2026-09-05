"""Data transfer objects for the Project application service.

Kept separate from both the domain entity and the API's Pydantic schemas so
each layer can evolve independently.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from canary_api.domain.projects.enums import ProjectSourceType


@dataclass(frozen=True)
class CreateProjectInput:
    """Input required to create a new project."""

    owner_id: uuid.UUID
    name: str
    source_type: ProjectSourceType
    description: str | None = None
