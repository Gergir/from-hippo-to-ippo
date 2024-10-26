from datetime import date
from pydantic import BaseModel, Field
from schemas.measurement_schema import MeasurementResponse


class TargetRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    target_weight: float = Field(ge=30, le=300)
    start_date: date = date.today()
    end_date: date
    public: bool = True


class TargetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    target_weight: float
    start_date: date
    end_date: date
    public: bool
    reached: bool
    closed: bool
    measurements: list[MeasurementResponse] = []

    class ConfigDict:
        from_attributes = True
