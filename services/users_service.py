from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.users_model import User
from utils.hashed_password import hash_password

logger = setup_logger(__name__)

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

async def insert_user(
        session: AsyncSession, 
        firstname: str,
        lastname: str,
        password: str,
        email: str
) -> Optional[User]:

    new_user = User(
        email=email,
        firstname=firstname,
        lastname=lastname,
        hashed_password=hash_password(password)
    )

    session.add(new_user)

    try:
        await session.flush()
        logger.info(f"Пользователь создан: {new_user.id}")
        return new_user
    except Exception as e:
        logger.error(f'Ошибка при создании пользователя: {e}')
        return None