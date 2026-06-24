from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from core.security import get_current_user, require_permission
from schemas.roles.roles import RoleList
from services.role_service import get_role_list

routers = APIRouter(prefix='/api/v1', tags=['Admin.Roles'])


@routers.get('/list',
            name='Получить список ролей',
            response_model=RoleList)
async def get_roles(
    current_user = Depends(require_permission('roles:index')),
    db_session: AsyncSession = Depends(get_db_session)):

    roles = await get_role_list(db_session)
    return RoleList(roles)