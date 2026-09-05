"""SQLAlchemy ORM models.

Import all model modules here so Alembic's autogenerate and
``Base.metadata.create_all`` (tests) see the complete schema.
"""

from canary_api.persistence.models.activity import ActivityEvent
from canary_api.persistence.models.ai import Conversation, Message
from canary_api.persistence.models.architecture import ArchitectureEdge, ArchitectureNode
from canary_api.persistence.models.code import CodeEntity, File
from canary_api.persistence.models.dependency import Dependency
from canary_api.persistence.models.github import GitHubConnection, GitHubRepository
from canary_api.persistence.models.health import HealthScore
from canary_api.persistence.models.project import Project, ProjectSource
from canary_api.persistence.models.recommendation import Recommendation
from canary_api.persistence.models.scan import Scan, ScanChange
from canary_api.persistence.models.security import SecurityFinding
from canary_api.persistence.models.user import User
from canary_api.persistence.models.workspace import Workspace

__all__ = [
    "ActivityEvent",
    "ArchitectureEdge",
    "ArchitectureNode",
    "CodeEntity",
    "Conversation",
    "Dependency",
    "File",
    "GitHubConnection",
    "GitHubRepository",
    "HealthScore",
    "Message",
    "Project",
    "ProjectSource",
    "Recommendation",
    "Scan",
    "ScanChange",
    "SecurityFinding",
    "User",
    "Workspace",
]
