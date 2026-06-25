from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, validator

from schemas.roles.schema import RoleItem

class UserBase(BaseModel):
    firstname: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Имя пользователя",
        example="Иван"
    )
    lastname: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Фамилия пользователя",
        example="Иванов"
    )
    email: str = Field(
        ..., 
        min_length=5,
        max_length=50,
        description="Email пользователя",
        example="example@domain.com"
    )

class UserCreateRequest(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Пароль пользователя",
        example="Password123"
    )

    role_id: UUID = Field(
        ...,
        description="ID роли пользователя"
    )
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
    
class UserUpdateRequest(BaseModel):
    """Схема для обновления пользователя (все поля опциональны)"""
    email: Optional[str] = Field(
        None,
        description="Новый email пользователя",
        examples=["newemail@example.com"]
    )
    firstname: Optional[str] = Field(
        None,
        description="Новое имя пользователя",
        examples=["Пётр"],
        min_length=1,
        max_length=100
    )
    lastname: Optional[str] = Field(
        None,
        description="Новая фамилия пользователя",
        examples=["Петров"],
        min_length=1,
        max_length=100
    )
    password: Optional[str] = Field(
        None,
        description="Новый пароль пользователя",
        examples=["NewSecurePass123!"],
        min_length=6,
        max_length=72
    )
    role_id: Optional[UUID] = Field(
        None,
        description="Новая роль пользователя"
    )
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserItem(BaseModel):
    id: UUID

    # Authentication fields - both unique
    email: str
    firstname: str
    lastname: str

    role: Optional[RoleItem] = None

    # ✅ Разрешаем создавать модель из ORM-объекта
    model_config = ConfigDict(from_attributes=True)

class UserList(BaseModel):
    users: List[UserItem]