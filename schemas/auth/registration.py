from pydantic import BaseModel, Field, validator


class RegistrationRequest(BaseModel):
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
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Пароль пользователя",
        example="Password123"
    )
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class RegistrationResponse(BaseModel):
    status: str = Field(
        description="Флаг возвращаемого ответа",
        example='success | error'
    )
    message: str = Field(
        description="Сообщение об операции реагистрации"
    )