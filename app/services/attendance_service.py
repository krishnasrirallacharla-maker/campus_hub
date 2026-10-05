from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.enums import AttendanceStatus, NotificationType, RegistrationStatus, UserRole
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.user import User
from app.models.notification import Notification
from app.schemas.attendance import (
    AttendanceResponse,
    AttendanceWithEventResponse,
    BulkAttendanceRequest,
    CheckInRequest,
    EventAttendanceSummary,
    MarkAttendanceRequest,
)


class AttendanceService:
    @staticmethod
    def mark_single_attendance(
        db: Session,
        event_id: int,
        req: MarkAttendanceRequest,
        current_user: User,
    ) -> Attendance:
        """Mark or update attendance for a single student."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)

        # Check permissions: Admin or Organizer
        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("Only the event organizer or an admin can mark attendance")

        student = db.query(User).filter(User.id == req.student_id).first()
        if not student:
            raise NotFoundException("Student", req.student_id)

        # Find registration if exists
        registration = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.student_id == req.student_id,
            )
            .first()
        )

        attendance = (
            db.query(Attendance)
            .filter(Attendance.event_id == event_id, Attendance.student_id == req.student_id)
            .first()
        )

        if attendance:
            attendance.status = req.status
            attendance.marked_at = datetime.now(timezone.utc)
            attendance.marked_by_id = current_user.id
            attendance.notes = req.notes
            if registration:
                attendance.registration_id = registration.id
        else:
            attendance = Attendance(
                event_id=event_id,
                student_id=req.student_id,
                registration_id=registration.id if registration else None,
                status=req.status,
                marked_at=datetime.now(timezone.utc),
                marked_by_id=current_user.id,
                notes=req.notes,
            )
            db.add(attendance)

        # Send notification to student
        notification = Notification(
            recipient_id=student.id,
            title="Attendance Status Updated",
            message=f"Your attendance for '{event.title}' has been marked as {req.status.value.upper()}.",
            notification_type=NotificationType.ATTENDANCE_MARKED,
            related_event_id=event.id,
            is_read=False,
        )
        db.add(notification)

        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def bulk_mark_attendance(
        db: Session,
        req: BulkAttendanceRequest,
        current_user: User,
    ) -> List[Attendance]:
        """Bulk mark attendance for multiple students for an event."""
        event = db.query(Event).filter(Event.id == req.event_id).first()
        if not event:
            raise NotFoundException("Event", req.event_id)

        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("Only the event organizer or an admin can mark attendance")

        updated_attendances = []
        for item in req.attendances:
            registration = (
                db.query(EventRegistration)
                .filter(
                    EventRegistration.event_id == req.event_id,
                    EventRegistration.student_id == item.student_id,
                )
                .first()
            )

            attendance = (
                db.query(Attendance)
                .filter(
                    Attendance.event_id == req.event_id,
                    Attendance.student_id == item.student_id,
                )
                .first()
            )

            if attendance:
                attendance.status = item.status
                attendance.marked_at = datetime.now(timezone.utc)
                attendance.marked_by_id = current_user.id
                attendance.notes = item.notes
                if registration:
                    attendance.registration_id = registration.id
            else:
                attendance = Attendance(
                    event_id=req.event_id,
                    student_id=item.student_id,
                    registration_id=registration.id if registration else None,
                    status=item.status,
                    marked_at=datetime.now(timezone.utc),
                    marked_by_id=current_user.id,
                    notes=item.notes,
                )
                db.add(attendance)

            updated_attendances.append(attendance)

        db.commit()
        return updated_attendances

    @staticmethod
    def self_check_in(
        db: Session,
        req: CheckInRequest,
        student: User,
    ) -> Attendance:
        """Student check-in via event check-in code or self-service."""
        event = db.query(Event).filter(Event.id == req.event_id).first()
        if not event:
            raise NotFoundException("Event", req.event_id)

        # Check that student is registered
        registration = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == req.event_id,
                EventRegistration.student_id == student.id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .first()
        )
        if not registration:
            raise BadRequestException("You must be registered for this event to check in")

        attendance = (
            db.query(Attendance)
            .filter(Attendance.event_id == req.event_id, Attendance.student_id == student.id)
            .first()
        )

        if attendance and attendance.status == AttendanceStatus.PRESENT:
            raise BadRequestException("You have already checked in for this event")

        if attendance:
            attendance.status = AttendanceStatus.PRESENT
            attendance.marked_at = datetime.now(timezone.utc)
            attendance.check_in_code = req.check_in_code
        else:
            attendance = Attendance(
                event_id=req.event_id,
                student_id=student.id,
                registration_id=registration.id,
                status=AttendanceStatus.PRESENT,
                marked_at=datetime.now(timezone.utc),
                check_in_code=req.check_in_code,
            )
            db.add(attendance)

        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def get_event_attendance_summary(db: Session, event_id: int) -> EventAttendanceSummary:
        """Get complete attendance breakdown for an event."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)

        total_reg = (
            db.query(func.count(EventRegistration.id))
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

        attendances = (
            db.query(Attendance)
            .filter(Attendance.event_id == event_id)
            .order_by(Attendance.marked_at.desc())
            .all()
        )

        total_present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        total_absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        total_late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        total_excused = sum(1 for a in attendances if a.status == AttendanceStatus.EXCUSED)

        # Attended count = PRESENT + LATE
        attended_count = total_present + total_late
        att_rate = round((attended_count / total_reg * 100), 1) if total_reg > 0 else 0.0

        return EventAttendanceSummary(
            event_id=event_id,
            total_registered=total_reg,
            total_present=total_present,
            total_absent=total_absent,
            total_late=total_late,
            total_excused=total_excused,
            attendance_rate=att_rate,
            attendees=[AttendanceResponse.model_validate(a) for a in attendances],
        )

    @staticmethod
    def get_student_attendances(
        db: Session,
        student_id: int,
    ) -> List[AttendanceWithEventResponse]:
        """Get attendance history for a student."""
        records = (
            db.query(Attendance, Event)
            .join(Event, Attendance.event_id == Event.id)
            .filter(Attendance.student_id == student_id)
            .order_by(Attendance.marked_at.desc())
            .all()
        )

        results = []
        for att, ev in records:
            results.append(
                AttendanceWithEventResponse(
                    id=att.id,
                    event_id=att.event_id,
                    student_id=att.student_id,
                    registration_id=att.registration_id,
                    status=att.status,
                    marked_at=att.marked_at,
                    marked_by_id=att.marked_by_id,
                    notes=att.notes,
                    student=att.student,
                    event_title=ev.title,
                    event_start_time=ev.start_time,
                    event_venue=ev.venue,
                )
            )
        return results
