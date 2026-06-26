from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_db_session
from core.logger import setup_logger
from core.security import require_permission
from schemas.users.schemas import UserCreateRequest, UserList, UserItem, UserUpdateRequest
from services.users_service import (
    assign_role_to_user, 
    get_user_by_email, 
    get_user_role_association, 
    get_users_list, 
    get_user_by_uuid, 
    insert_user, 
    revoke_role_from_user, 
    update_user
)


logger = setup_logger(__name__)
routers = APIRouter(prefix='/api/v1/users', tags=['Admin.Users'])

@routers.get('/list',
             name="Получить список пользователей",
             response_model=UserList)
async def get_users(#current_user = Depends(require_permission('users:index')),
             db_session = Depends(get_db_session),
             offset: int = Query(0, ge=0, description="Пропустить N записей"),
             limit: int = Query(20, ge=1, le=100, description="Количество записей")):
    users = await get_users_list(
        db_session,
        offset=offset,
        limit=limit)
    return users

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
    
    association = await assign_role_to_user(db_session, new_user, data.role_id)
    if not association:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign permission to role"
        )
    
    logger.info(
        f"Пользователь создан: {new_user.email} (ID: {new_user.id}) | "
        f"Роль: {data.role_id} | "
        f"Создал: {current_user.get('email')}"
    )

    return new_user

@routers.put('/update/{user_id}', 
             name="Редактирование данных пользователя",
             response_model=UserItem,
             responses={
                404: {"description": "Пользователь не найден"},
                409: {"description": "Email уже занят"},
                400: {"description": "Ошибка обновления"}
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
        password=data.password
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    # 4. Обновляем роль (если передана и отличается от текущей)
    if data.role_id is not None:
        # Получаем текущую роль пользователя
        current_association = await get_user_role_association(db_session, user_id)
        current_role_id = current_association.role_id if current_association else None
        
        # Если роль изменилась
        if current_role_id != data.role_id:
            # Если была роль — удаляем старую
            if current_association:
                await revoke_role_from_user(db_session, user_id, current_role_id)
            
            # Назначаем новую роль
            association = await assign_role_to_user(db_session, updated_user, data.role_id)
            if not association:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to assign new role to user"
                )
            
            logger.info(
                f"Роль пользователя изменена: {user.email} | "
                f"Старая роль: {current_role_id} | "
                f"Новая роль: {data.role_id} | "
                f"Обновил: {current_user.get('email')}"
            )

    logger.info(
        f"Пользователь обновлён: {updated_user.email} (ID: {updated_user.id}) | "
        f"Обновил: {current_user.get('email')}"
    )
    return updated_user