import re
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

RESERVED_ROLE_NAMES = {
    "SUPERADMIN", "ADMIN", "ROOT", "SYSTEM", "OWNER",
    "ADMINISTRATOR", "MODERATOR", "GUEST", "USER"
}

class RoleItem(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, v):
        """Преобразует строку в UUID, если необходимо"""
        if isinstance(v, str):
            return UUID(v)
        return v
    
    # ✅ Разрешаем создавать модель из ORM-объекта
    model_config = ConfigDict(
        from_attributes=True,
        strict=True  # ✅ Строгий режим
    )

class RoleList(BaseModel):
    roles: List[RoleItem]

class RoleRequest(BaseModel):
    name: str = Field(
        ..., 
        description="Уникальное имя роли в системе. Только буквы, цифры и подчёркивания",
        examples=["moderator", "content_manager", "analyst"],
        min_length=2,
        max_length=50
    )

    description: Optional[str] = Field(
        "",
        description="Пользовательское описание роли",
        examples=["Модератор контента", "Управление контентом", "Аналитик данных"],
        max_length=255
    )

    @field_validator("name")
    @classmethod
    def validate_role_name(cls, v: str) -> str:
        """Валидация имени роли"""
        v = v.strip()
        
        if not v:
            raise ValueError("Role name cannot be empty")
        
        # Только буквы, цифры и подчёркивания
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Role name can only contain letters, numbers, and underscores. "
                "Example: 'moderator', 'content_manager'"
            )
        
        # Защита от зарезервированных имён
        if v.upper() in RESERVED_ROLE_NAMES:
            raise ValueError(
                f"Role name '{v}' is reserved and cannot be used. "
                f"Reserved names: {', '.join(sorted(RESERVED_ROLE_NAMES))}"
            )
        
        # Приводим к верхнему регистру
        return v.upper()
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Очистка описания"""
        if v is not None:
            v = v.strip()
            if len(v) > 255:
                raise ValueError("Description must not exceed 255 characters")
            if v == "":
                return None
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "MODERATOR",
                    "description": "Модератор контента"
                },
                {
                    "name": "CONTENT_MANAGER",
                    "description": "Управление контентом"
                },
                {
                    "name": "ANALYST",
                    "description": "Аналитик данных"
                }
            ]
        }
    }
    
    def to_orm(self) -> dict:
        """Преобразование в словарь для создания ORM-объекта"""
        return {
            "name": self.name.upper(),
            "description": self.description
        }

