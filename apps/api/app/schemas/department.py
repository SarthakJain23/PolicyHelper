import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    code: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
