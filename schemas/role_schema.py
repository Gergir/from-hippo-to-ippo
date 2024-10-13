from pydantic import BaseModel
from models import RoleType
from schemas import UserResponse


class RoleRequest(BaseModel):
    role_type: RoleType

class RoleResponse(BaseModel):
    id: int
    role_type: RoleType
    users: list[UserResponse] = []

    class ConfigDict:
        from_attributes = True