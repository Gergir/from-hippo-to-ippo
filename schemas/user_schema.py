from typing import List
from pydantic import BaseModel
from schemas.target_schema import TargetResponse

class UserRequest(BaseModel):
    username: str
    email: str
    password: str
    height: float
    weight: float


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    targets: List[TargetResponse] = []


    class Config:
        orm_mode = True
