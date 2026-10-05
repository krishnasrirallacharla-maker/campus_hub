from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import AttendanceStatus
from app.schemas.user import UserSummary


class MarkAttendanceRequest(BaseModel):
    student_id: int
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None


class BulkAttendanceItem(BaseModel):
    student_id: int
    status: AttendanceStatus = AttendanceStatus.PRESENT
    notes: Optional[str] = None


class BulkAttendanceRequest(BaseModel):
    event_id: int
    attendances: List[BulkAttendanceItem]


class CheckInRequest(BaseModel):
    event_id: int
    check_in_code: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    event_id: int
    student_id: int
    registration_id: Optional[int] = None
    status: AttendanceStatus
    marked_at: datetime
    marked_by_id: Optional[int] = None
    notes: Optional[str] = None
    student: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceWithEventResponse(AttendanceResponse):
    event_title: Optional[str] = None
    event_start_time: Optional[datetime] = None
    event_venue: Optional[str] = None


class EventAttendanceSummary(BaseModel):
    event_id: int
    total_registered: int
    total_present: int
    total_absent: int
    total_late: int
    total_excused: int
    attendance_rate: float
    attendees: List[AttendanceResponse]
