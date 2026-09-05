"""Scan and ScanChange models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from canary_api.domain.projects.enums import ScanStatus
from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Scan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single scan/analysis run against a project."""

    __tablename__ = "scans"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, name="scan_status"), nullable=False, default=ScanStatus.QUEUED, index=True
    )
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="scans")  # noqa: F821
    changes: Mapped[list["ScanChange"]] = relationship(
        "ScanChange", back_populates="scan", cascade="all, delete-orphan"
    )


class ScanChange(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A detected change (file added/modified/removed) within a scan."""

    __tablename__ = "scan_changes"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_path: Mapped[str] = mapped_column(String(4096), nullable=False)
    change_type: Mapped[str] = mapped_column(String(32), nullable=False)  # added|modified|removed

    scan: Mapped["Scan"] = relationship("Scan", back_populates="changes")
