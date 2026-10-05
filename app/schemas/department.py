from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Computer Science and Engineering")
    code: str = Field(..., min_length=2, max_length=20, example="CSE")
    description: Optional[str] = Field(None, example="Department of Computer Science and Engineering")
    head_of_department: Optional[str] = Field(None, max_length=100, example="Dr. Alan Turing")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = None
    head_of_department: Optional[str] = Field(None, max_length=100)


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentWithStats(DepartmentResponse):
    total_students: int = 0
    total_faculty: int = 0
    total_events: int = 0
