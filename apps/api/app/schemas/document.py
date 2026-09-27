import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.department import DepartmentResponse
from app.schemas.role import UserRole


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    file_name: str
    file_type: str
    file_size: int
    category: str
    department_id: uuid.UUID | None
    department: DepartmentResponse | None
    allowed_role_names: list[str]
    status: str
    error_message: str | None
    uploaded_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadMetadata(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="GENERAL")
    department_id: uuid.UUID | None = None
    allowed_role_names: list[str] = Field(
        default_factory=lambda: [
            UserRole.EMPLOYEE.value,
            UserRole.MANAGER.value,
            UserRole.HR_ADMIN.value,
            UserRole.SUPER_ADMIN.value,
        ]
    )
