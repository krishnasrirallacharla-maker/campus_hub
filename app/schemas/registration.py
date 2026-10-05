from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import RegistrationStatus
from app.schemas.user import UserSummary


class RegistrationCreate(BaseModel):
    event_id: int


class RegistrationCancel(BaseModel):
    cancellation_reason: Optional[str] = Field(None, max_length=255)


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    student_id: int
    status: RegistrationStatus
    registered_at: datetime
    cancellation_reason: Optional[str] = None
    student: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationWithEventResponse(RegistrationResponse):
    event_title: Optional[str] = None
    event_start_time: Optional[datetime] = None
    event_venue: Optional[str] = None
    event_status: Optional[str] = None
