from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.roles_model import Role, UserRoleAssociation
from models.permissions_model import Permission, RolePermissionAssociation

logger = setup_logger(__name__)


async def has_permission(session: AsyncSession, user_id: UUID, permission_name: str) -> bool:
    stmt = (
        select(Permission)
        .join(RolePermissionAssociation, Permission.id == RolePermissionAssociation.permission_id)
        .join(UserRoleAssociation, RolePermissionAssociation.role_id == UserRoleAssociation.role_id)
        .where(
            UserRoleAssociation.user_id == user_id,
            Permission.name == permission_name
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def get_permissions(session: AsyncSession, offset: int = 0, limit: int = 10) -> List[Permission]:
    stmt = select(Permission)

    # фильтр списка разрешений

    stmt = stmt.offset(offset).limit(limit)
    
    result = await session.execute(
        stmt
    )

    return result.scalars()

async def get_permission(session: AsyncSession, permission_id: UUID) -> Optional[Permission]:
    return await session.get(Permission, permission_id)

async def get_permission_by_code(session: AsyncSession, permission_code: str) -> Optional[Permission]:
    stmt = select(Permission).where(Permission.name == permission_code)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def insert_permission(session: AsyncSession, name: str, description: str = '') -> Optional[Permission]:
    new_permission = Permission(
        name=name,
        description=description
    )

    session.add(new_permission)

    try:
        await session.flush()
        return new_permission
    except Exception as e:
        await session.rollback()
        logger.error(f"{e}")
        return None

async def remove_permission(session: AsyncSession, permission: Permission) -> bool:
    await session.delete(permission)

    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"{e}")
        return False