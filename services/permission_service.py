from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.roles_model import Role, UserRoleAssociation
from models.permissions_model import Permission, RolePermissionAssociation


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

    stmt = stmt.offset(offset).limit(limit)
    
    result = await session.execute(
        stmt
    )

    return result.scalars()