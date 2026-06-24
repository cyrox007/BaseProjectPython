from typing import List
from uuid import UUID

from pydantic import BaseModel



class RoleItem(BaseModel):
    id: UUID
    name: str
    description: str

class RoleList(BaseModel):
    roles: List[RoleItem]