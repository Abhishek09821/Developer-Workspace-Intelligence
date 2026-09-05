"""Project and ProjectSource models.

``Project`` is the core aggregate root developers create and analyze.
``ProjectSource`` records where the code came from (local workspace path,
uploaded zip reference, or GitHub repository) without storing full
repository contents in the database.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from canary_api.domain.projects.enums import ProjectSourceType, ProjectStatus
from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A software project registered for analysis."""

    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[ProjectSourceType] = mapped_column(
        Enum(ProjectSourceType, name="project_source_type"), nullable=False
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.CREATED,
        index=True,
    )
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="projects")  # noqa: F821
    sources: Mapped[list["ProjectSource"]] = relationship(
        "ProjectSource", back_populates="project", cascade="all, delete-orphan"
    )
    scans: Mapped[list["Scan"]] = relationship(  # noqa: F821
        "Scan", back_populates="project", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_project_owner_name"),)


class ProjectSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Origin metadata for a project's code (workspace path, zip, or GitHub)."""

    __tablename__ = "project_sources"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[ProjectSourceType] = mapped_column(
        Enum(ProjectSourceType, name="project_source_type_ref"), nullable=False
    )
    # Arbitrary but validated metadata per source type, e.g. workspace root
    # path, zip storage key, or GitHub owner/repo/ref. Never stores file
    # contents.
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="sources")
