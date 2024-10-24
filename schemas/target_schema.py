from datetime import date
from pydantic import BaseModel
from schemas.measurement_schema import MeasurementResponse


class TargetRequest(BaseModel):
    title: str
    target_weight: float
    start_date: date = date.today()
    end_date: date
    public: bool = True


class TargetResponse(BaseModel):
    id: int
    user_id: int
    title: str
    target_weight: float
    start_date: date
    end_date: date
    public: bool
    reached: bool
    closed: bool
    measurements: list[MeasurementResponse] = []


    class ConfigDict:
        from_attributes = True
