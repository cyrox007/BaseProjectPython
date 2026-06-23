from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from schemas.auth.login import LoginResponse, LoginRequest
from schemas.auth.registration import RegistrationRequest, RegistrationResponse
from services.users_service import get_user_by_email
from utils.hashed_password import verify_password
from utils.jwt import create_access_token

routers = APIRouter(prefix='/api/v1/auth')


@routers.post('/login',
            name="Аутентификация",
            description="Метод аутентификации пользователя. Проверяет логин и пароль в БД и возвращает токен доступа в систему необходимый для выполнения авторизационных запросов к системе", 
            response_model=LoginResponse)
async def login(form_data: LoginRequest, db_session: AsyncSession = Depends(get_db_session)):
    user = await get_user_by_email(
        session=db_session,
        email=form_data.email
    )
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        return {
            'status': 'error',
            'detail': 'Incorrect username or password'
        }, 403
    
    access_token = create_access_token({
        'sub': 1,
        'username': form_data.email
    })
    
    return {'status': 'success', 'access_token': access_token, 'token_type': 'bearer'}

@routers.post('/registration', response_model=RegistrationResponse)
async def registratiom(data: RegistrationRequest):
    return RegistrationResponse('ok', '')