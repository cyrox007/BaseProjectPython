from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_db_session
from core.logger import setup_logger
from core.security import require_permission
from schemas.permission.schema import PERMISSION_ERRORS, PermissionItem, PermissionList, PermissionRequest
from services.permission_service import get_permission, get_permission_by_code, get_permissions, insert_permission, remove_permission

logger = setup_logger(__name__)
routers = APIRouter(prefix='/api/v1/permissions', tags=['Admin.Permissions'])


@routers.get('/list', 
    name="Получить список разрешений", 
    response_model=PermissionList)
async def get_list(current_user = Depends(require_permission('permission:index')),
                db_session = Depends(get_db_session)):

    permissions = await get_permissions(db_session)

    return PermissionList(permissions=permissions)

@routers.get('/{permission_id}',
            name="Получить разрешение по ID",
            response_model=PermissionItem)
async def view_permission(permission_id: UUID,
                        current_user = Depends(require_permission('permission:show')),
                        db_session = Depends(get_db_session)):

    permission = await get_permission(db_session, permission_id)

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    

    return PermissionItem(
        id=permission.id,
        name=permission.name,
        description=permission.description
    )

@routers.post('/create',
            name="Создать разрешение",
            response_model=PermissionItem,
            responses=PERMISSION_ERRORS,
            status_code=status.HTTP_201_CREATED)
async def create_permission(data: PermissionRequest,
                            current_user = Depends(require_permission('permission:create')),
                            db_session = Depends(get_db_session)):

    existing = await get_permission_by_code(db_session, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Permission '{data.name}' already exists"
        )
    
    # Создание
    new_permission = await insert_permission(
        db_session,
        name=data.name.lower(),
        description=data.description
    )

    if not new_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create permission"
        )
    
    return PermissionItem(
        id=new_permission.id,
        name=new_permission.name,
        description=new_permission.description
    )

@routers.delete('/delete/{permission_id}',
                name="Удалить разрешение из системы", 
                status_code=status.HTTP_204_NO_CONTENT)
async def delete_permssion(permission_id: UUID,
                        current_user = Depends(require_permission('permission:delete')),
                        db_session = Depends(get_db_session)):
    
    permission = await get_permission(db_session, permission_id)

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    try:
        deleted = await remove_permission(db_session, permission)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete permission"
            )
        
        logger.info(
            f"Разрешение удалено | "
            f"User: {current_user.get('email')} | "
            f"Permission: {permission.name} (ID: {permission.id})"
        )
        
        return None  # 204 No Content
        
    except Exception as e:
        logger.error(f"Ошибка при удалении разрешения {permission.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    