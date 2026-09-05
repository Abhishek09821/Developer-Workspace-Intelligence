"""File and CodeEntity models: the codebase index."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# Dimensionality for code-entity embeddings used in semantic search once the
# AI Codebase Assistant module is implemented. Kept centralized so it can be
# changed in one place if the embedding model changes.
EMBEDDING_DIMENSIONS = 1536


class File(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single file discovered within a project during a scan."""

    __tablename__ = "files"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    path: Mapped[str] = mapped_column(String(4096), nullable=False)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    code_entities: Mapped[list["CodeEntity"]] = relationship(
        "CodeEntity", back_populates="file", cascade="all, delete-orphan"
    )


class CodeEntity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A parsed code construct (function, class, module) within a file."""

    __tablename__ = "code_entities"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # function|class|module|...
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )

    file: Mapped["File"] = relationship("File", back_populates="code_entities")
