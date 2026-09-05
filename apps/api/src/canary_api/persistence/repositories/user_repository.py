"""SQLAlchemy-backed user persistence used by the auth foundation."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from canary_api.persistence.models.user import User


class UserRepository:
    """Simple persistence access for ``User`` rows.

    Kept as a lightweight class (rather than a full domain aggregate) since
    this phase only needs registration/login, not rich user domain logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def add(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user
