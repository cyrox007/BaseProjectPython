from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(
        ..., 
        description="Уникальное имя пользователя в системе",
        example="example@domain.com"
    )

    password: str = Field(
        description="Пароль пользователя в системе",
        example="Password123"
    )

class LoginResponse(BaseModel):
    status: str = Field(
        description="Флаг возвращаемого ответа",
        example='success | error'
    )
    access_token: str
    token_type: str