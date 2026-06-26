from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.roles_model import Role, UserRoleAssociation
from models.permissions_model import Permission, RolePermissionAssociation
from schemas.permission.schema import PermissionItem, PermissionList

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


async def get_permissions(session: AsyncSession, 
                          offset: int = 0, limit: int = 10) -> Optional[PermissionList]:
    stmt = select(Permission)

    # фильтр списка разрешений

    stmt = stmt.offset(offset).limit(limit)
    
    result = await session.execute(
        stmt
    )

    permissions = result.scalars().all()
    return PermissionList(permissions=permissions)

async def get_permission(session: AsyncSession, permission_id: UUID) -> Optional[PermissionItem]:
    permission = await session.get(Permission, permission_id)
    return PermissionItem(
        id=permission.id,
        name=permission.name,
        description=permission.description
    ) if permission else None

async def get_permission_by_code(session: AsyncSession, 
                                 permission_code: str) -> Optional[PermissionItem]:
    stmt = select(Permission).where(Permission.name == permission_code)

    result = await session.execute(stmt)
    permission = result.scalar_one_or_none()
    return PermissionItem(
        id=permission.id,
        name=permission.name,
        description=permission.description
    ) if permission else None

async def insert_permission(session: AsyncSession, 
                            name: str, description: str = '') -> Optional[PermissionItem]:
    new_permission = Permission(
        name=name,
        description=description
    )

    session.add(new_permission)

    try:
        await session.flush()
        return  PermissionItem(
            id=new_permission.id,
            name=new_permission.name,
            description=new_permission.description
        ) if new_permission else None
    except Exception as e:
        await session.rollback()
        logger.error(f"{e}")
        return None

async def remove_permission(session: AsyncSession, permission_id: UUID) -> bool:
    permission = await session.get(Permission, permission_id)
    await session.delete(permission)

    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"{e}")
        return False