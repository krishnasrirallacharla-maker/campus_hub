from typing import Optional
from pydantic import BaseModel
from app.models.enums import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
    email: str
    full_name: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    new_password: str
