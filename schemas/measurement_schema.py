from datetime import date
from pydantic import BaseModel, Field


class MeasurementRequest(BaseModel):
    weight: float = Field(ge=30, le=500)
    measurement_date: date = date.today()


class MeasurementResponse(BaseModel):
    id: int
    target_id: int
    weight: float
    measurement_date: date

    class ConfigDict:
        from_attributes = True
