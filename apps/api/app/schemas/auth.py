import uuid
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
    full_name: str
    roles: list[str]
    department_id: uuid.UUID | None
    department_name: str | None
    must_change_password: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
