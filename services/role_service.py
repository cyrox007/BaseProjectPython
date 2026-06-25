from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import setup_logger
from models.permissions_model import RolePermissionAssociation
from models.roles_model import Role

logger = setup_logger(__name__)

async def get_role_list(session: AsyncSession, limit: int = 10, offset: int = 0) -> List[Role]:
    stmt = select(Role)

    # делаем фильтры тут

    stmt = stmt.offset(offset).limit(limit)

    result = await session.execute(stmt)

    return result.scalars()

async def get_role(session: AsyncSession, role_id: UUID) -> Optional[Role]:
    return await session.get(Role, role_id)

async def get_role_by_code(session: AsyncSession, code: str) -> Optional[Role]:
    result = await session.execute(
        select(Role).where(Role.name == code.upper())
    )
    return result.scalar_one_or_none()

async def insert_role(session: AsyncSession, name: str, description: str = ''):
    new_role = Role(
        name=name.upper(),
        description=description
    )

    session.add(new_role)

    try:
        await session.flush()
        logger.info(f"Роль создана: {new_role.id}")
        return new_role
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при создании роли: {e}')
        return None
    
async def update_role(session: AsyncSession, target_role: Role, 
                      new_name: str, new_description: str = ''):
    
    target_role.name = new_name
    target_role.description = new_description

    session.add(target_role)

    try:
        await session.flush()
        logger.info(f"Роль обновлена: {target_role.id}")
        return target_role
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при изменения роли: {e}')
        return None
    
async def remove_role(session: AsyncSession, role: Role):
    session.delete(role)

    try:
        await session.flush()
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f'Ошибка при удалении роли: {e}')
        return False
    

async def assign_perm_to_role(session: AsyncSession, role_id: UUID, permission_id: UUID) -> bool:
    # Проверяем, не существует ли уже
    existing = await get_role_permission_association(session, role_id, permission_id)
    if existing:
        logger.warning(f"Разрешение {permission_id} уже назначено роли {role_id}")
        return None
        
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
    
async def get_role_permission_association(session: AsyncSession, role_id: UUID, permission_id: UUID) -> Optional[RolePermissionAssociation]:
    stmt = select(RolePermissionAssociation).where(
        RolePermissionAssociation.role_id == role_id,
        RolePermissionAssociation.permission_id == permission_id
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()

async def revoke_perm_from_role(
    session: AsyncSession,
    role_id: UUID,
    permission_id: UUID
) -> bool:
    """Отзыв разрешения у роли"""
    try:
        association = await get_role_permission_association(session, role_id, permission_id)
        if not association:
            return False
        
        await session.delete(association)
        await session.flush()
        
        logger.info(f"Разрешение {permission_id} отозвано у роли {role_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отзыве разрешения: {e}")
        return False
