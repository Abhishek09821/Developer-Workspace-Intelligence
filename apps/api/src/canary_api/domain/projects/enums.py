"""Enumerations for the project lifecycle and source types."""

from __future__ import annotations

import enum


class ProjectStatus(str, enum.Enum):
    """Lifecycle states a project moves through end to end."""

    CREATED = "created"
    IMPORTING = "importing"
    READY = "ready"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectSourceType(str, enum.Enum):
    """Where a project's code originates from."""

    LOCAL_WORKSPACE = "local_workspace"
    ZIP_UPLOAD = "zip_upload"
    GITHUB_REPOSITORY = "github_repository"


class ScanStatus(str, enum.Enum):
    """Lifecycle states of an individual scan run."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
