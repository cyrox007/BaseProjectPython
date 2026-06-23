from typing import List, TYPE_CHECKING
from uuid import UUID as UUIDType, uuid4

from sqlalchemy import UUID as PG_UUID, Boolean, DateTime, Float, String, Text, Index, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Database

if TYPE_CHECKING:
    from models.roles_model import Role


class User(Database.Base):
    __tablename__ = 'users'

    id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4, 
        comment="Уникальный ID пользователя"
    )
    # Authentication fields - both unique
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True, 
        comment="Email для входа"
    )
    firstname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя пользоваеля"
    )
    lastname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Фамилия пользователя"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        comment="Хэш пароля (bcrypt)"
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",  # Название ассоциативной таблицы
        back_populates="users",  # Должно совпадать с именем в модели Role
        lazy="selectin"
    )
