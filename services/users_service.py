from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.users_model import User
from utils.hashed_password import hash_password

logger = setup_logger(__name__)

async def get_users_list(session: AsyncSession, offset=0, limit=10) -> List[User]:
    stmt = select(User)

    # фильтрация по свойствам тут

    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)
    return result.scalars()

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
        email: str,
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
    
async def update_user(
    session: AsyncSession,
    user_id: UUID,
    email: Optional[str] = None,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
    password: Optional[str] = None,
    role_id: Optional[UUID] = None
) -> Optional[User]:
    """
    Частичное обновление данных пользователя.
    Обновляются только переданные поля.
    """
    try:
        # Получаем пользователя
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Обновляем только переданные поля
        if email is not None:
            user.email = email
        
        if firstname is not None:
            user.firstname = firstname
        
        if lastname is not None:
            user.lastname = lastname
        
        if password is not None:
            user.hashed_password = hash_password(password)
        
        await session.flush()
        return user
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        return None