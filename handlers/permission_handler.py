from fastapi import APIRouter, Depends

from core.dependencies import get_db_session
from core.security import require_permission
from services.permission_service import get_permissions


routers = APIRouter(prefix='/api/v1/permissions', tags=['Admin.Permission'])


@routers.get('/list', 
            name="Получить список разрешений")
async def get_list(
    current_user = Depends(require_permission('permission:index')),
    db_session = Depends(get_db_session)):

    permissions = await get_permissions(db_session)