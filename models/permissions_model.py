from uuid import UUID as UUIDType, uuid4

from sqlalchemy import (
    UUID as PG_UUID, 
    ForeignKey, 
    String, 
    Table, 
    Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Database


class Permission(Database.Base):
    __tablename__ = "permissions"

    id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Уникальный ID разрешения"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Уникальное имя разрешения (например, 'create_item')"
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="Описание разрешения"
    )

    def __repr__(self):
        return f"<Permission(name={self.name})>"
    

class RolePermissionAssociation(Database.Base):
    __tablename__ = 'role_permissions'

    role_id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('roles.id', ondelete='CASCADE'),
        primary_key=True,
        index=True
    )

    permission_id: Mapped[UUIDType] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey('permissions.id', ondelete='CASCADE'),
        primary_key=True,
        index=True
    )