from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logger import setup_logger
from core.redis import cache, invalidate_cache
from models.roles_model import UserRoleAssociation
from models.users_model import User
from schemas.users.schemas import UserItem, UserList
from utils.hashed_password import hash_password

logger = setup_logger(__name__)

@cache(key_prefix="users:list", ttl=60, key_args=["offset", "limit"], use_pickle=True)
async def get_users_list(session: AsyncSession, offset=0, limit=10) -> UserList:
    stmt = select(User).options(selectinload(User.role))

    # фильтрация по свойствам тут

    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)
    users = result.scalars().all()
    return UserList(users=users)

async def get_user_by_uuid(session: AsyncSession, uuid: UUID) -> UserItem:
    result = await session.execute(
        select(User).where(User.id == uuid)
    )
    user = result.scalar_one_or_none()
    return UserItem(id=user, email=user.email,
                    firstname=user.firstname, lastname=user.lastname, 
                    role=user.role)

@cache(key_prefix='user:email', ttl=300, key_args=['email'])
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
        await invalidate_cache("users:*")
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
    password: Optional[str] = None
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

        await invalidate_cache("user:*")
        await invalidate_cache("users:*")
        return user
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        return None
    
async def get_user_role_association(session: AsyncSession, user_id: UUID, role_id: UUID) -> Optional[UserRoleAssociation]:
    stmt = select(UserRoleAssociation).where(
        UserRoleAssociation.role_id == role_id,
        UserRoleAssociation.user_id == user_id
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()

async def assign_role_to_user(session: AsyncSession, user_id: UUID, role_id: UUID) -> Optional[UserRoleAssociation]:
        
    association = UserRoleAssociation(
        role_id=role_id,
        user_id=user_id
    )

    session.add(association)
    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        return False
    
async def revoke_role_from_user(
    session: AsyncSession,
    user_id: UUID,
    role_id: UUID
) -> bool:
    """Отзыв роли у пользователя"""
    try:
        stmt = select(UserRoleAssociation).where(
            UserRoleAssociation.user_id == user_id,
            UserRoleAssociation.role_id == role_id
        )
        result = await session.execute(stmt)
        association = result.scalar_one_or_none()
        
        if not association:
            logger.warning(f"Роль {role_id} не найдена у пользователя {user_id}")
            return False
        
        await session.delete(association)
        await session.flush()
        
        logger.info(f"Роль {role_id} отозвана у пользователя {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при отзыве роли: {e}")
        return False