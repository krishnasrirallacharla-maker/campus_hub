from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserSummary


class CertificateIssueRequest(BaseModel):
    event_id: int
    student_id: int
    title: Optional[str] = None  # If None, defaults to "Certificate of Participation - {event.title}"
    description: Optional[str] = None


class CertificateBulkIssueRequest(BaseModel):
    event_id: int
    only_present_attendees: bool = True
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None


class CertificateResponse(BaseModel):
    id: int
    certificate_code: str
    event_id: int
    student_id: int
    title: str
    description: Optional[str] = None
    issue_date: datetime
    issued_by_id: Optional[int] = None
    is_valid: bool
    student: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class CertificateWithEventResponse(CertificateResponse):
    event_title: Optional[str] = None
    event_date: Optional[datetime] = None
    event_venue: Optional[str] = None
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    department_name: Optional[str] = None


class CertificateVerificationResponse(BaseModel):
    is_valid: bool
    certificate_code: str
    student_name: str
    student_roll: Optional[str] = None
    event_title: str
    event_date: datetime
    issue_date: datetime
    department_name: Optional[str] = None
    organizer_name: Optional[str] = None
