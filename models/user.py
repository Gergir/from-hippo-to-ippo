from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db_service import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    height: Mapped[float] = mapped_column()
    weight: Mapped[float] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(), default=None)  # handled by DB
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp(), default=None)

    targets: Mapped[list["Target"]] = relationship(back_populates="user")
