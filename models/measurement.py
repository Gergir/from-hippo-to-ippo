from datetime import datetime, date
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.db_service import Base


class Measurement(Base):
    __tablename__ = 'measurements'
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey('targets.id'))
    weight: Mapped[float] = mapped_column()
    measurement_date: Mapped[date] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(), default=None)  # handled by DB
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp(), default=None)

    target: Mapped["Target"] = relationship(back_populates="measurements")
