from typing import List
from datetime import date
from pydantic import BaseModel
from schemas.measurement_schema import MeasurementResponse


class TargetRequest(BaseModel):
    title: str
    user_id: int
    target_weight: float
    start_date: date = date.today()
    end_date: date
    public: bool = True
    reached: bool = False


class TargetResponse(BaseModel):
    id: int
    title: str
    user_id: int
    target_weight: float
    start_date: date
    end_date: date
    public: bool
    reached: bool
    end_date_exceeded: bool
    measurements: List[MeasurementResponse] = []


    class Config:
        orm_mode = True
