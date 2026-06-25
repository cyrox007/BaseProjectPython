from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserRoleAssocRequest(BaseModel):
    """Запрос на назначение/отзыв роли пользователю"""
    user_id: UUID = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        examples=["f6e5d4c3-b2a1-0987-zyxw-vu9876543210"]
    )

    role_id: UUID = Field(
        ...,
        description="Уникальный идентификатор роли",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    )

class AssignRoleData(BaseModel):
    role_id: UUID = Field(..., description="ID роли")
    role_name: str = Field(..., description="Имя роли")
    user_id: UUID = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    assigned_at: Optional[str] = Field(None, description="Дата назначения")

class AssignRoleResponse(BaseModel):
    status: str = Field(
        ..., 
        description="Статус операции",
        examples=["success", "error"]
    )
    message: str = Field(
        ..., 
        description="Сообщение о результате",
        examples=[""]
    )
    data: Optional[AssignRoleData] = Field(
        None,
        description="Данные о назначенной роли"
    )