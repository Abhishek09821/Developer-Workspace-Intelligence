"""ID generation helpers shared by all domain entities."""

from __future__ import annotations

import uuid


def new_id() -> uuid.UUID:
    """Generate a new random UUID4 for use as an entity primary key."""

    return uuid.uuid4()
