"""GitHubConnection and GitHubRepository models."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class GitHubConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An OAuth connection linking a user's Canary account to GitHub."""

    __tablename__ = "github_connections"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    github_account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    # Access tokens must be encrypted at rest by the integrations layer
    # before being written here; never store plaintext tokens.
    encrypted_access_token: Mapped[str] = mapped_column(String(2048), nullable=False)
    scopes: Mapped[str | None] = mapped_column(String(512), nullable=True)

    repositories: Mapped[list["GitHubRepository"]] = relationship(
        "GitHubRepository", back_populates="connection", cascade="all, delete-orphan"
    )


class GitHubRepository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A GitHub repository available for import via a connection."""

    __tablename__ = "github_repositories"

    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("github_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), default="main", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    connection: Mapped["GitHubConnection"] = relationship(
        "GitHubConnection", back_populates="repositories"
    )
