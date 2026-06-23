from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users_model import User


async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.id == uuid)
    )
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()
