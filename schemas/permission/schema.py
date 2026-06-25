from typing import List, Optional
from uuid import UUID

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PermissionRequest(BaseModel):
    name: str = Field(
        ..., 
        description="Уникальное имя разрешения в системе. Формат: {module}:{action}",
        examples=["users:create", "orders:read", "reports:generate"],
        min_length=3,
        max_length=100,
        pattern=r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)?:[a-z][a-z0-9_]*$"
    )

    description: Optional[str] = Field(
        "",
        description="Пользовательское описание разрешения",
        examples=["Создание новых пользователей", "Просмотр заказов"],
        max_length=255
    )

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Дополнительная валидация формата имени разрешения"""
        # Проверяем, что есть ровно одно двоеточие
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError(
                "Permission name must contain exactly one colon ':' separator. "
                "Example: 'users:create'"
            )
        
        resource_part, action_part = parts
        
        # Проверяем длину каждой части
        if len(resource_part) < 2:
            raise ValueError("Resource part must be at least 2 characters long")
        if len(action_part) < 2:
            raise ValueError("Action part must be at least 2 characters long")
        
        # Проверяем, что нет пробелов
        if " " in v:
            raise ValueError("Permission name cannot contain spaces")
        
        # Проверяем, что нет двойных подчёркиваний
        if "__" in v:
            raise ValueError("Permission name cannot contain double underscores '__'")
        
        return v.lower()  # Приводим к нижнему регистру
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Очистка описания"""
        if v is not None:
            v = v.strip()
            if v == "":
                return None
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "users:create",
                    "description": "Создание новых пользователей"
                },
                {
                    "name": "auth.roles:update",
                    "description": "Редактирование ролей"
                }
            ]
        }
    }


class PermissionItem(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    # ✅ Разрешаем создавать модель из ORM-объекта
    model_config = ConfigDict(from_attributes=True)

class PermissionList(BaseModel):
    permissions: List[PermissionItem]

    model_config = ConfigDict(from_attributes=True)

PERMISSION_ERRORS = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "value_error",
                            "loc": ["body", "name"],
                            "msg": "Permission name must contain exactly one colon ':' separator. Example: 'users:create'",
                            "input": "invalid-format"
                        }
                    ]
                }
            }
        }
    },
    status.HTTP_409_CONFLICT: {
        "description": "Разрешение уже существует",
        "content": {
            "application/json": {
                "example": {"detail": "Permission 'users:create' already exists"}
            }
        }
    }
}