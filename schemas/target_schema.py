from typing import List
from datetime import date
from pydantic import BaseModel
from schemas.measurement_schema import MeasurementResponse

# from schemas.measurement_schema import

class TargetRequest(BaseModel):
    title: str
    user_id: int
    target_weight: float
    start_date: date
    end_date: date
    public: bool
    reached: bool
    end_date_exceeded: bool


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
    measurement: List[MeasurementResponse]


    class Config:
        orm_mode = True
