from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db_session
from schemas.auth.login import LoginResponse, LoginRequest
from schemas.auth.registration import RegistrationRequest, RegistrationResponse
from services.users_service import get_user_by_email, insert_user
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
        return JSONResponse(
            status_code=403,
            content={
                'status': 'error',
                'detail': 'Incorrect username or password'
            }
        )
    
    access_token = create_access_token({
        'sub': 1,
        'username': form_data.email
    })
    
    return {'status': 'success', 'access_token': access_token, 'token_type': 'bearer'}

@routers.post('/registration', 
            name="Регистрация нового пользователя",
            description="Метод регистрации нового пользователя", 
            status_code=201,
            response_model=RegistrationResponse)
async def registratiom(data: RegistrationRequest, db_session: AsyncSession = Depends(get_db_session)):
    existing_user = await get_user_by_email(db_session, data.email)
    if existing_user:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Пользователь с таким email уже существует"}
        )
    
    if not await insert_user(db_session, data.firstname, data.lastname, data.password, data.email):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Ошибка при создании пользователя"}
        )
    
    return RegistrationResponse(
        status="ok",
        message="Пользователь успешно зарегистрирован"
    )