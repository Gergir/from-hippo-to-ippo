from datetime import date
from pydantic import BaseModel


class MeasurementRequest(BaseModel):
    weight: float
    measurement_date: date


class MeasurementResponse(BaseModel):
    id: int
    target_id: int
    weight: float
    measurement_date: date


    class ConfigDict:
        from_attributes = True
