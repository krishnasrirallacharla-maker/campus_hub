from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.enums import EventStatus
from app.schemas.department import DepartmentResponse
from app.schemas.user import UserSummary


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, example="Annual AI Hackathon 2026")
    description: str = Field(..., min_length=10, example="A 48-hour competitive coding hackathon.")
    event_type: str = Field(..., min_length=2, max_length=50, example="Hackathon")
    venue: str = Field(..., min_length=2, max_length=200, example="Main Auditorium, Block C")
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    capacity: int = Field(..., gt=0, example=100)
    department_id: Optional[int] = None
    banner_url: Optional[str] = Field(None, max_length=500)
    is_certificate_provided: bool = True


class EventCreate(EventBase):
    status: Optional[EventStatus] = EventStatus.PUBLISHED

    @model_validator(mode="after")
    def validate_dates(self) -> "EventCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.registration_deadline > self.start_time:
            raise ValueError("registration_deadline must be on or before start_time")
        return self


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    event_type: Optional[str] = Field(None, min_length=2, max_length=50)
    venue: Optional[str] = Field(None, min_length=2, max_length=200)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    capacity: Optional[int] = Field(None, gt=0)
    status: Optional[EventStatus] = None
    department_id: Optional[int] = None
    banner_url: Optional[str] = Field(None, max_length=500)
    is_certificate_provided: Optional[bool] = None

    @model_validator(mode="after")
    def validate_dates_if_present(self) -> "EventUpdate":
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.registration_deadline and self.start_time and self.registration_deadline > self.start_time:
            raise ValueError("registration_deadline must be on or before start_time")
        return self


class EventStatusUpdate(BaseModel):
    status: EventStatus


class EventResponse(EventBase):
    id: int
    status: EventStatus
    organizer_id: int
    created_at: datetime
    updated_at: datetime
    organizer: Optional[UserSummary] = None
    department: Optional[DepartmentResponse] = None
    registered_count: int = 0
    available_seats: int = 0
    is_registered: Optional[bool] = None  # for current student caller
    is_attended: Optional[bool] = None  # for current student caller
    average_rating: Optional[float] = None
    total_feedbacks: int = 0

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
    page: int
    size: int
    pages: int
