# Classes for keeping track of sequence numbers for target and measurement in relation with user and target.
# So e.g. The first target created by user is accessible by user/{user_id}/target/1, no matter of the actual target id.
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from services.db_service import Base

class UserTargetCounter(Base):
    __tablename__ = "user_target_counters"
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    current_count: Mapped[int] = mapped_column(default=0)

class TargetMeasurementCounter(Base):
    __tablename__ = "target_measurement_counters"
    target_id: Mapped[int] = mapped_column(ForeignKey('targets.id'), primary_key=True)
    current_count: Mapped[int] = mapped_column(default=0)