from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from core.dependencies import get_db_session
from core.security import require_permission
from schemas.users.schemas import UserCreateRequest, UserList, UserItem, UserUpdateRequest
from services.users_service import get_user_by_email, get_users_list, get_user_by_uuid, insert_user, update_user


routers = APIRouter(prefix='/api/v1/users', tags=['Admin.Users'])

@routers.get('/list',
             name="Получить список пользователей",
             response_model=UserList)
async def get_users(current_user = Depends(require_permission('users:index')),
             db_session = Depends(get_db_session)):
    users = await get_users_list(db_session)
    return UserList(users=users)

@routers.get('/{user_id}',
             name="Получить пользователя по ID",
            response_model=UserItem)
async def show_user(user_id: UUID,
             current_user = Depends(require_permission('users:show')),
             db_session = Depends(get_db_session)):

    user = await get_user_by_uuid(db_session, user_id)

    return UserItem(
        id=user.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        role=user.role
    )

@routers.post('/create', 
             name="Создание пользователя",
             response_model=UserItem,
             responses={
                409: {"description": "Пользователь с таким email уже существует"},
                400: {"description": "Ошибка валидации"}
             })
async def create_user_endpoint(data: UserCreateRequest,
                    current_user = Depends(require_permission('users:create')),
                    db_session = Depends(get_db_session)):
    
    # Проверка на существующий email
    existing = await get_user_by_email(db_session, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    new_user = await insert_user(
        db_session, 
        data.firstname, 
        data.lastname, 
        data.password, 
        data.email
    )

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
    
    # дальше надо назначить роль юзера

    return new_user

@routers.put('/update/{user_id}', 
             name="Редактирование данных пользователя",
             response_model=UserItem,
             responses={
                404: {"description": "Пользователь не найден"},
                409: {"description": "Email уже занят"}
             })
async def update_user_endpoint(user_id: UUID,
                    data: UserUpdateRequest,
                    current_user = Depends(require_permission('users:update')),
                    db_session = Depends(get_db_session)):
    # 1. Проверяем, существует ли пользователь
    user = await get_user_by_uuid(db_session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 2. Проверяем email (если передан и отличается)
    if data.email and data.email != user.email:
        existing = await get_user_by_email(db_session, data.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already taken by another user"
            )
    
    # 3. Обновляем только переданные поля
    updated_user = await update_user(
        db_session,
        user_id=user_id,
        email=data.email,
        firstname=data.firstname,
        lastname=data.lastname,
        password=data.password,
        role_id=data.role_id
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    # тут проверяем передан ли новый параметр role_id и отличается ли от от текущего затем переназначаем
    
    #logger.info(f"Пользователь обновлён: {updated_user.email} (ID: {updated_user.id})")
    return updated_user