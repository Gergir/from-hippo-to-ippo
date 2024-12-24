from pydantic import BaseModel, Field
from models import RoleType
from schemas import UserResponseOnlyIdEmail


class RoleRequest(BaseModel):
    role_type: RoleType


class RoleResponse(BaseModel):
    id: int
    role_type: RoleType
    users: list[UserResponseOnlyIdEmail] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True
