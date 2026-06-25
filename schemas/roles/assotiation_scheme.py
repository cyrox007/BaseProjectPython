from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RolePermAssocRequest(BaseModel):
    """Запрос на назначение/отзыв разрешения для роли"""
    
    role_id: UUID = Field(
        ...,
        description="Уникальный идентификатор роли",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]
    )
    
    permission_id: UUID = Field(
        ...,
        description="Уникальный идентификатор разрешения",
        examples=["f6e5d4c3-b2a1-0987-zyxw-vu9876543210"]
    )
    
    @field_validator("role_id")
    @classmethod
    def validate_role_id(cls, v: UUID) -> UUID:
        """Проверка, что UUID не нулевой"""
        if v == UUID(int=0):
            raise ValueError("role_id cannot be empty (zero UUID)")
        return v
    
    @field_validator("permission_id")
    @classmethod
    def validate_permission_id(cls, v: UUID) -> UUID:
        """Проверка, что UUID не нулевой"""
        if v == UUID(int=0):
            raise ValueError("permission_id cannot be empty (zero UUID)")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "permission_id": "f6e5d4c3-b2a1-0987-zyxw-vu9876543210"
                }
            ]
        }
    }

class AssignPermissionData(BaseModel):
    """Данные о назначенном разрешении"""
    role_id: UUID = Field(..., description="ID роли")
    role_name: str = Field(..., description="Имя роли")
    permission_id: UUID = Field(..., description="ID разрешения")
    permission_name: str = Field(..., description="Имя разрешения")
    assigned_at: Optional[str] = Field(None, description="Дата назначения")


class AssignPermissionResponse(BaseModel):
    """Ответ на назначение разрешения роли"""
    status: str = Field(
        ..., 
        description="Статус операции",
        examples=["success", "error"]
    )
    message: str = Field(
        ..., 
        description="Сообщение о результате",
        examples=["Permission 'users:create' assigned to role 'MODERATOR'"]
    )
    data: Optional[AssignPermissionData] = Field(
        None,
        description="Данные о назначенном разрешении"
    )

class RevokePermissionResponse(BaseModel):
    """Ответ на отзыв разрешения у роли"""
    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение о результате")
    role_id: UUID = Field(..., description="ID роли")
    permission_id: UUID = Field(..., description="ID разрешения")