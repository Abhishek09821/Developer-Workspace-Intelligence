"""Workspace model.

Represents a local filesystem workspace registered for import. Stores only
the validated root path and metadata - never file contents.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped, mapped_column

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A local workspace directory registered by a user for scanning."""

    __tablename__ = "workspaces"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    root_path: Mapped[str] = mapped_column(String(4096), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
