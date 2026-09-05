"""Dependency model: third-party packages detected in a project."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Dependency(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A third-party dependency declared or resolved within a project."""

    __tablename__ = "dependencies"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ecosystem: Mapped[str] = mapped_column(String(64), nullable=False)  # npm|pypi|cargo|...
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_direct: Mapped[bool] = mapped_column(default=True, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
