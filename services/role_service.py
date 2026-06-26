from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.permissions_model import RolePermissionAssociation
from models.roles_model import Role
from schemas.roles.schema import RoleItem, RoleList

logger = setup_logger(__name__)

async def get_role_list(session: AsyncSession, 
                        limit: int = 10, offset: int = 0) -> RoleList:
    stmt = select(Role)

    # делаем фильтры тут

    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)

    roles = result.scalars().all()
    return RoleList(roles=roles)

async def get_role(session: AsyncSession, role_id: UUID) -> Optional[RoleItem]:
    role = await session.get(Role, role_id)
    return RoleItem(id=role.id, name=role.name, 
                    description=role.description) if role else None

async def get_role_by_code(session: AsyncSession, code: str) -> Optional[RoleItem]:
    result = await session.execute(
        select(Role).where(Role.name == code.upper())
    )
    role = result.scalar_one_or_none()
    return RoleItem(id=role.id, name=role.name, 
                    description=role.description) if role else None

async def insert_role(session: AsyncSession, name: str, 
                      description: str = '') -> Optional[RoleItem]:
    new_role = Role(
        name=name.upper(),
        description=description
    )

    session.add(new_role)

    try:
        await session.flush()
        logger.info(f"Роль создана: {new_role.id}")
        return RoleItem(id=new_role.id, name=new_role.name, 
                    description=new_role.description) if new_role else None
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при создании роли: {e}')
        return None
    
async def update_role(session: AsyncSession, target_role: Role, 
                      new_name: str, new_description: str = '') -> Optional[RoleItem]:
    
    target_role.name = new_name
    target_role.description = new_description

    session.add(target_role)

    try:
        await session.flush()
        logger.info(f"Роль обновлена: {target_role.id}")
        return RoleItem(id=target_role.id, name=target_role.name, 
                    description=target_role.description) if target_role else None
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при изменения роли: {e}')
        return None
    
async def remove_role(session: AsyncSession, role_id: UUID) -> bool:
    role = await session.get(Role, role_id)
    session.delete(role)

    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при удалении роли: {e}')
        return False
    

async def assign_perm_to_role(session: AsyncSession, 
                              role_id: UUID, permission_id: UUID) -> bool: 
    association = RolePermissionAssociation(
        role_id=role_id,
        permission_id=permission_id
    )

    session.add(association)
    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        return False
    
async def get_role_permission_association(session: AsyncSession, 
                                          role_id: UUID, 
                                          permission_id: UUID) -> Optional[RolePermissionAssociation]:
    stmt = select(RolePermissionAssociation).where(
        RolePermissionAssociation.role_id == role_id,
        RolePermissionAssociation.permission_id == permission_id
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()

async def revoke_perm_from_role(
    session: AsyncSession,
    association: RolePermissionAssociation
) -> bool:
    """Отзыв разрешения у роли"""
    try:
        await session.delete(association)
        await session.flush()
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при отзыве разрешения: {e}")
        return False
