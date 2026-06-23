from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class TestRequest(BaseModel):
    uuid: UUID = Field(
        ..., 
        description="Уникальный идентификатор",
        example=uuid4()
    )


class TestResponse(BaseModel):
    uuid: UUID = Field(
        description="Уникальный идентификатор",
        example=uuid4()
    )
    name: str = Field(
        description="Имя",
        example='John'
    )
    age: int = Field(
        description="возраст",
        example=18
    )