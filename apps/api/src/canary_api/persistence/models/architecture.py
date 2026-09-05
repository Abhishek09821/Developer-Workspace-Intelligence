"""ArchitectureNode and ArchitectureEdge models: dependency/module graph."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ArchitectureNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A node in the architecture graph (module, package, service)."""

    __tablename__ = "architecture_nodes"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_type: Mapped[str] = mapped_column(String(64), nullable=False)  # module|package|service
    label: Mapped[str] = mapped_column(String(512), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class ArchitectureEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A directed edge (dependency relationship) between two graph nodes."""

    __tablename__ = "architecture_edges"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_nodes.id", ondelete="CASCADE"), nullable=False
    )
    edge_type: Mapped[str] = mapped_column(String(64), nullable=False)  # imports|calls|depends_on
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
