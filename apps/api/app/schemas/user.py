import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.schemas.role import RoleResponse
from app.schemas.department import DepartmentResponse


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role_names: list[str] = Field(default_factory=lambda: ["EMPLOYEE"])
    department_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    role_names: list[str] | None = None
    department_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    must_change_password: bool
    last_login_at: datetime | None
    created_at: datetime
    roles: list[RoleResponse]
    department: DepartmentResponse | None

    class Config:
        from_attributes = True


class UserCreatedWithPasswordResponse(BaseModel):
    user: UserResponse
    temporary_password: str
    instructions: str = (
        "Share this temporary password securely with the user. "
        "They will be required to change their password upon first login."
    )
