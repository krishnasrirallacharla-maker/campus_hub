from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import (
    get_current_faculty_or_admin,
    get_current_user,
)
from app.models.user import User
from app.schemas.attendance import (
    AttendanceResponse,
    AttendanceWithEventResponse,
    BulkAttendanceRequest,
    CheckInRequest,
    EventAttendanceSummary,
    MarkAttendanceRequest,
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendances", tags=["Attendance Management"])


@router.post(
    "/event/{event_id}/mark",
    response_model=AttendanceResponse,
    summary="Mark single student attendance (Faculty & Admin)",
)
def mark_attendance(
    event_id: int,
    req: MarkAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return AttendanceService.mark_single_attendance(db, event_id, req, current_user)


@router.post(
    "/bulk",
    response_model=List[AttendanceResponse],
    summary="Bulk mark attendance for an event (Faculty & Admin)",
)
def bulk_mark_attendance(
    req: BulkAttendanceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return AttendanceService.bulk_mark_attendance(db, req, current_user)


@router.post(
    "/check-in",
    response_model=AttendanceResponse,
    summary="Student self check-in for an event",
)
def student_check_in(
    req: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AttendanceService.self_check_in(db, req, current_user)


@router.get(
    "/event/{event_id}/summary",
    response_model=EventAttendanceSummary,
    summary="Get complete attendance report and breakdown for an event (Faculty & Admin)",
)
def get_event_attendance_summary(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return AttendanceService.get_event_attendance_summary(db, event_id)


@router.get(
    "/my-history",
    response_model=List[AttendanceWithEventResponse],
    summary="Get attendance history for current logged-in student",
)
def get_my_attendance_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AttendanceService.get_student_attendances(db, current_user.id)
