import enum
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db_service import Base


class RoleType(enum.Enum):
    user = 'user'
    premium = 'premium'
    admin = 'admin'


class Role(Base):
    __tablename__ = 'roles'
    id:Mapped[int] = mapped_column(primary_key=True)
    role_type:Mapped[RoleType] = mapped_column(index=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(), default=None)  # handled by DB
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp(), default=None)

    users:Mapped[list["User"]] = relationship(back_populates='role')

