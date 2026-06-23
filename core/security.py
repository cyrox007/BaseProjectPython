from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from services.permission_service import has_permission

from utils.jwt import verify_token

security = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    # проверяем токен на валидность
    print(token.credentials)
    payload = verify_token(token.credentials)
    print(payload)
    return payload

async def get_current_user_with_permission(
    permission_name: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Проверка через метод модели
    if await has_permission(session, UUID(current_user['sub']), permission_name) is False:
        raise HTTPException(
            status_code=403,
            detail=f"Permission '{permission_name}' required"
        )
    
    return current_user

def require_permission(permission_name: str):
    async def dependency(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session)
    ):
        return await get_current_user_with_permission(permission_name, current_user, session)
    return dependency