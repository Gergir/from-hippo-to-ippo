from datetime import datetime, date

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.db_service import Base
from models.user import User
from models.measurement import Measurement

class Target(Base):
    __tablename__ = 'targets'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    target_weight: Mapped[float] = mapped_column()
    start_date: Mapped[date] = mapped_column(default=date.today())
    end_date: Mapped[date] = mapped_column(nullable=True)
    public: Mapped[bool] = mapped_column(default=True)
    reached: Mapped[bool] = mapped_column(default=False)
    end_date_exceeded: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(), default=None) # handled by DB
    updated_at: Mapped[datetime] = mapped_column(update_default=func.current_timestamp(), default=None)

    user: Mapped["User"] = relationship(back_populates="targets")
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="target")