from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from core.logger import setup_logger
from core.security import require_permission
from schemas.error_responses import ERROR_RESPONSES
from schemas.roles.schema import RoleItem, RoleList, RoleRequest
from services.role_service import (
    get_role, get_role_by_code, 
    get_role_list, insert_role, remove_role, 
    update_role)


logger = setup_logger(__name__)
routers = APIRouter(prefix='/api/v1/roles', tags=['Admin.Roles'])


@routers.get('/list',
            name='Получить список ролей',
            response_model=RoleList)
async def get_roles(
    current_user = Depends(require_permission('roles:index')),
    db_session: AsyncSession = Depends(get_db_session)):

    roles = await get_role_list(db_session)
    return roles

@routers.get('/{role_id}',
            name="Получить роль по ID",
            response_model=RoleItem, 
            responses={
                404: {"description": "Роль не найдена"},
            })

async def show_role(
    role_id: UUID,
    current_user = Depends(require_permission('roles:show')),
    db_session: AsyncSession = Depends(get_db_session)):

    role = await get_role(db_session, role_id)

    if not role:
        raise HTTPException(
            status_code=404,
            detail='role not found'
        )

    return role

@routers.post('/create',
            name="Метод создания роли в системе",
            status_code=201,
            response_model=RoleItem,
            responses={
                409: {"description": "Роль уже существует"},
                400: {"description": "Ошибка валидации"}
            })
async def create_role(data: RoleRequest,
    current_user = Depends(require_permission('roles:create')),                  
    db_session: AsyncSession = Depends(get_db_session)):

    existing_role = await get_role_by_code(db_session, data.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такая роль уже существует"
        )

    role = await insert_role(db_session, data.name, data.description)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании роли")
    
    return role

@routers.put('/update/{role_id}',
            name='Редактирование роли', 
            response_model=RoleItem,
            responses={
                409: {"description": "Роль уже существует"},
                400: {"description": "Ошибка валидации"}
            })
async def edit_role(role_id: UUID,
    data: RoleRequest,
    current_user = Depends(require_permission('roles:update')),    
    db_session: AsyncSession = Depends(get_db_session)):

    current_role = await get_role(db_session, role_id)

    if not current_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такая роль уже существует"
        )

    if current_role.name.upper() == 'SUPERADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете именить предустановленную роль"
        )

    if data.name and data.name.upper() != current_role.name.upper():
        # Проверяем, не занято ли новое имя
        existing_role = await get_role_by_code(db_session, data.name)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role with name '{data.name}' already exists"
            )
        
    updated_role = await update_role(db_session, current_role, data.name, data.description)
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании роли"
        )
    
    return updated_role

@routers.delete('/delete/{role_id}',
                name='Удаление роли', 
                status_code=status.HTTP_204_NO_CONTENT, 
                responses={
                    400: {"description": "Ошибка валидации"}
                })
async def delete_role(role_id: UUID,
    current_user = Depends(require_permission('roles:update')),
    db_session: AsyncSession = Depends(get_db_session)):

    current_role = await get_role(db_session, role_id)
    
    if not current_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if current_role.name.upper() == "SUPERADMIN":
        logger.warning(f"Попытка удаления SUPERADMIN роли | User: {current_user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete SUPERADMIN role"
        )
    
    await remove_role(db_session, current_role.id)
    return