import uuid
from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    permissions: dict

    class Config:
        from_attributes = True
