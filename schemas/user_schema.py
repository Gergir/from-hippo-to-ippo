from pydantic import BaseModel, Field, EmailStr
from schemas.target_schema import TargetResponse


class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    height: float = Field(ge=60, le=280)
    weight: float = Field(ge=30, le=500)

class UserUpdateRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=50)
    height: float | None = Field(None, ge=60, le=280)
    weight: float | None = Field(None, ge=30, le=500)

class UserResponse(BaseModel):
    id: int
    role_id: int
    username: str
    email: str
    targets: list[TargetResponse] = Field(default_factory=list)

    class ConfigDict:
        from_attributes = True


class UserResponseOnlyIdEmail(BaseModel):
    id: int
    email: str

    class ConfigDict:
        from_attributes = True
