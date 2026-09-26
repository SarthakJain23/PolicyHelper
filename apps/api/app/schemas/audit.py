import uuid
from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    user_email: str | None = None
    user_name: str | None = None
    action: str
    ip_address: str | None = None
    details: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
