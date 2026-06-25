from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_db_session
from core.logger import setup_logger
from core.security import require_permission
from schemas.users.association_schema import AssignRoleData, AssignRoleResponse, UserRoleAssocRequest
from services.role_service import get_role
from services.users_service import assign_role_to_user, get_user_by_uuid, get_user_role_association

logger = setup_logger(__name__)
routers = APIRouter(
    prefix='/api/v1/users/roles',
    tags=['Admin.Users', 'Admin.Roles']
)

@routers.post('/assign',
              name="Назначение роли пользователю",
              response_model=AssignRoleResponse)
async def assign_user_to_role_endpoint(data: UserRoleAssocRequest,
									   current_user = Depends(require_permission('permission:assign')),
                                        db_session = Depends(get_db_session)):
    role = await get_role(db_session, data.role_id)
    if not role:
        """ logger.warning(
            f"Попытка назначить разрешение несуществующей роли | "
            f"User: {current_user.get('email')} | "
            f"Role ID: {data.role_id}"
        ) """
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    user = await get_user_by_uuid(db_session, data.user_id)
    if not user:
        """ logger.warning(
            f"Попытка назначить разрешение несуществующей роли | "
            f"User: {current_user.get('email')} | "
            f"Role ID: {data.role_id}"
        ) """
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Проверяем, не назначено ли уже разрешение
    existing = await get_user_role_association(db_session, data.user_id, data.role_id)
    if existing:
        """ logger.warning(
            f"Попытка повторно назначить разрешение | "
            f"User: {current_user.get('email')} | "
            f"Role: {role.name} | Permission: {permission.name}"
        ) """
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="role already assigned to this user"
        )
    
    # Назначаем разрешение
    try:
        association = await assign_role_to_user(db_session, data.user_id, data.role_id)
        
        if not association:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign permission to role"
            )
        
        """ logger.info(
            f"Разрешение назначено роли | "
            f"User: {current_user.get('email')} | "
            f"Role: {role.name} | Permission: {permission.name}"
        ) """
        
        return AssignRoleResponse(
            status="success",
            message=f"Role '{role.name}' assigned to user '{user.email}'",
            data=AssignRoleData(
                role_id=role.id,
                role_name=role.name,
                user_id=user.id,
                email=user.email,
                assigned_at=datetime.now().isoformat()  # можно добавить при создании
            )
        )
        
    except Exception as e:
        logger.error(f"Ошибка при назначении разрешения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
