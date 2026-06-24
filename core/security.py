from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_client_info, get_db_session
from core.logger import setup_logger
from services.permission_service import has_permission

from services.users_service import get_user_by_uuid
from utils.jwt import verify_token

logger = setup_logger(__name__)
security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    # проверяем токен на валидность
    try:
        payload = verify_token(token.credentials)
        return payload
    except Exception as e:
        logger.warning(f"Ошибка верификации токена: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")



async def get_current_user_with_permission(
    permission_name: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    if not current_user:
        # Логируем попытку неавторизованного доступа
        client_info = await get_client_info(request)
        logger.warning(
            f"Доступ запрещён (неавторизован): {permission_name} | "
            f"IP: {client_info['ip']} | User-Agent: {client_info['user_agent']}"
        )
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = UUID(current_user['sub'])
    email = current_user.get('email', 'unknown')

    has_perm = await has_permission(session, user_id, permission_name)
    if not has_perm:
        user = await get_user_by_uuid(session, user_id)
        role_name = user.role.name if user and user.role else 'no_role'

        logger.warning(
            f"Доступ запрещён: {permission_name} | "
            f"User: {email} (ID: {user_id}) | "
            f"Role: {role_name} | "
            f"IP: {request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=403,
            detail=f"Permission '{permission_name}' required"
        )
    logger.debug(
        f"Доступ разрешён: {permission_name} | "
        f"User: {email} (ID: {user_id})"
    )
    return current_user

def require_permission(permission_name: str):
    async def dependency(
        request: Request,
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session)
    ):
        return await get_current_user_with_permission(
            permission_name, request, current_user, session)
    
    return dependency