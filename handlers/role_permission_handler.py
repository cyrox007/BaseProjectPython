from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException

from core.dependencies import get_db_session
from core.logger import setup_logger
from core.security import require_permission
from schemas.roles.assotiation_scheme import AssignPermissionData, AssignPermissionResponse, RevokePermissionResponse, RolePermAssocRequest
from services.permission_service import get_permission
from services.role_service import assign_perm_to_role, get_role, get_role_permission_association, revoke_perm_from_role

logger = setup_logger(__name__)
routers = APIRouter(
    prefix='/api/v1/roles/permissions', 
    tags=['Admin.Roles', 'Admin.Permissions']
)


@routers.post('/assign',
              name="Назначить разрешение роли",
              description="Привязывает существующее разрешение к указанной роли",
              status_code=status.HTTP_201_CREATED,
			  response_model=AssignPermissionResponse,
              responses={
                404: {"description": "Роль или разрешение не найдены"},
                409: {"description": "Разрешение уже назначено роли"}
            })
async def assign_permission_to_role_endpoint(data: RolePermAssocRequest,
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
	
	# 2. Проверяем, существует ли разрешение
	permission = await get_permission(db_session, data.permission_id)
	if not permission:
		""" logger.warning(
            f"Попытка назначить несуществующее разрешение | "
            f"User: {current_user.get('email')} | "
            f"Permission ID: {data.permission_id}"
        ) """
		raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
	# 3. Проверяем, не назначено ли уже разрешение
	existing = await get_role_permission_association(db_session, data.role_id, data.permission_id)
	if existing:
		""" logger.warning(
            f"Попытка повторно назначить разрешение | "
            f"User: {current_user.get('email')} | "
            f"Role: {role.name} | Permission: {permission.name}"
        ) """
		raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already assigned to this role"
        )
	# 4. Назначаем разрешение
	try:
		association = await assign_perm_to_role(db_session, data.role_id, data.permission_id)
        
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
        
		return AssignPermissionResponse(
            status="success",
            message=f"Permission '{permission.name}' assigned to role '{role.name}'",
            data=AssignPermissionData(
                role_id=role.id,
                role_name=role.name,
                permission_id=permission.id,
                permission_name=permission.name,
                assigned_at=datetime.now().isoformat()  # можно добавить при создании
            )
        )
        
	except Exception as e:
		logger.error(f"Ошибка при назначении разрешения: {e}")
		raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@routers.delete(
    '/revoke',
    name="Отозвать разрешение у роли",
    description="Удаляет связь между разрешением и ролью",
    status_code=status.HTTP_200_OK,
    response_model=RevokePermissionResponse
)
async def revoke_permission_from_role_endpoint(
    data: RolePermAssocRequest,
    current_user: dict = Depends(require_permission('permissions:revoke')),
    db_session = Depends(get_db_session)
) -> RevokePermissionResponse:
    # Проверяем существование
    association = await get_role_permission_association(
        db_session, data.role_id, data.permission_id
    )
    
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission is not assigned to this role"
        )
    
    # Отзываем
    success = await revoke_perm_from_role(db_session, association)
    logger.info(f"Разрешение {data.permission_id} отозвано у роли {data.role_id}")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke permission from role"
        )
    
    return RevokePermissionResponse(
        status="success",
        message="Permission revoked from role",
        role_id=data.role_id,
        permission_id=data.permission_id
    )