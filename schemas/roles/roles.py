from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RoleItem(BaseModel):
    id: UUID
    name: str
    description: str

    # ✅ Разрешаем создавать модель из ORM-объекта
    model_config = ConfigDict(from_attributes=True)

class RoleList(BaseModel):
    roles: List[RoleItem]

class RoleRequest(BaseModel):
    name: str = Field(
        ..., 
        description="Уникальное имя роли в системе",
        example="modedator"
    )

    description: Optional[str] = Field(
        ...,
        description="Пользовательское описание роли",
        example="Lorem ipsum..."
    )