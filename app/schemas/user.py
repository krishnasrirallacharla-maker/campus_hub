from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole
from app.schemas.department import DepartmentResponse


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=150)
    role: UserRole = UserRole.STUDENT
    department_id: Optional[int] = None
    roll_number: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class StudentRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=150)
    department_id: Optional[int] = None
    roll_number: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = Field(None, max_length=20)
    roll_number: Optional[str] = None
    department_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    roll_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
