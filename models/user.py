from datetime import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db_service import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))
    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column()
    height: Mapped[float] = mapped_column()
    weight: Mapped[float] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(), default=None)  # handled by DB
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp(), default=None)

    targets: Mapped[list["Target"]] = relationship(back_populates="user")
    role:Mapped["Role"] = relationship(back_populates='users')

