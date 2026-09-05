"""HealthScore model."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from canary_api.persistence.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class HealthScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Computed overall + dimensional health score for a scan."""

    __tablename__ = "health_scores"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    dimension: Mapped[str] = mapped_column(String(64), nullable=False)  # security|deps|arch|...
    score: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
