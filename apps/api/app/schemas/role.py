import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    HR_ADMIN = "HR_ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    permissions: dict

    model_config = ConfigDict(from_attributes=True)

