from pydantic import BaseModel
from models import RoleType
from schemas import UserResponseOnlyIdEmail


class RoleRequest(BaseModel):
    role_type: RoleType


class RoleResponse(BaseModel):
    id: int
    role_type: RoleType
    users: list[UserResponseOnlyIdEmail] = []

    class ConfigDict:
        from_attributes = True
