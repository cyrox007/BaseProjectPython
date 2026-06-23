from typing import List, TYPE_CHECKING
from uuid import UUID as UUIDType, uuid4

from sqlalchemy import (
    UUID as PG_UUID,
    ForeignKey,
    String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Database
if TYPE_CHECKING:
    from models.permissions_model import Permission
    from models.users_model import User


class Role(Database.Base):
    __tablename__ = "roles"

    id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Уникальный ID роли"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True, 
        nullable=False,
        comment="Уникальное имя роли"
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="Описание роли"
    )

    # Отношения
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role(name={self.name})>"
    

class UserRoleAssociation(Database.Base):
    __tablename__ = 'user_roles'

    user_id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('users.id', ondelete='CASCADE'), 
        primary_key=True,
        index=True
    )
    role_id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('roles.id', ondelete='CASCADE'), 
        primary_key=True,
        index=True
    )

    # Опционально: для доступа к объектам через связь
    """ user: Mapped["User"] = relationship("User", back_populates="role_associations")
    role: Mapped["Role"] = relationship("Role", back_populates="user_associations") """