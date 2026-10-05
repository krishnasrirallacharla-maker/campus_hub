from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.enums import EventStatus, NotificationType, RegistrationStatus, UserRole
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.user import User
from app.models.notification import Notification
from app.schemas.registration import RegistrationCancel, RegistrationWithEventResponse


class RegistrationService:
    @staticmethod
    def register_for_event(db: Session, event_id: int, student: User) -> EventRegistration:
        """Register a student for an event with capacity and deadline validations."""
        if student.role != UserRole.STUDENT and student.role != UserRole.ADMIN:
            raise ForbiddenException("Only students can register for events")

        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)

        # 1. Check Event Status
        if event.status not in [EventStatus.PUBLISHED, EventStatus.ONGOING]:
            raise BadRequestException(f"Cannot register for an event in '{event.status.value}' status")

        # 2. Check Registration Deadline
        now_utc = datetime.now(timezone.utc)
        # Ensure timezone-aware comparison
        reg_deadline = event.registration_deadline
        if reg_deadline.tzinfo is None:
            reg_deadline = reg_deadline.replace(tzinfo=timezone.utc)

        if now_utc > reg_deadline:
            raise BadRequestException(
                f"Registration deadline passed on {reg_deadline.strftime('%Y-%m-%d %H:%M UTC')}"
            )

        # 3. Check for existing registration
        existing_reg = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.student_id == student.id,
            )
            .first()
        )

        if existing_reg and existing_reg.status == RegistrationStatus.CONFIRMED:
            raise BadRequestException("You are already registered for this event")

        # 4. Check Capacity
        current_confirmed = (
            db.query(func.count(EventRegistration.id))
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

        if current_confirmed >= event.capacity:
            raise BadRequestException("Event is full. Maximum capacity reached.")

        # 5. Create or Update registration
        if existing_reg:
            existing_reg.status = RegistrationStatus.CONFIRMED
            existing_reg.registered_at = datetime.now(timezone.utc)
            existing_reg.cancellation_reason = None
            registration = existing_reg
        else:
            registration = EventRegistration(
                event_id=event_id,
                student_id=student.id,
                status=RegistrationStatus.CONFIRMED,
                registered_at=datetime.now(timezone.utc),
            )
            db.add(registration)

        # 6. Send in-app notification to student
        notification = Notification(
            recipient_id=student.id,
            title="Registration Confirmed",
            message=f"You have successfully registered for '{event.title}' scheduled on {event.start_time.strftime('%Y-%m-%d %H:%M')}.",
            notification_type=NotificationType.REGISTRATION_CONFIRMED,
            related_event_id=event.id,
            is_read=False,
        )
        db.add(notification)

        db.commit()
        db.refresh(registration)
        return registration

    @staticmethod
    def cancel_registration(
        db: Session,
        event_id: int,
        student: User,
        cancel_data: Optional[RegistrationCancel] = None,
    ) -> EventRegistration:
        """Cancel registration for an event."""
        registration = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.student_id == student.id,
            )
            .first()
        )

        if not registration or registration.status != RegistrationStatus.CONFIRMED:
            raise BadRequestException("No active confirmed registration found for this event")

        event = db.query(Event).filter(Event.id == event_id).first()

        registration.status = RegistrationStatus.CANCELLED
        registration.cancellation_reason = (
            cancel_data.cancellation_reason if cancel_data else "Cancelled by student"
        )

        # Notify student
        if event:
            notification = Notification(
                recipient_id=student.id,
                title="Registration Cancelled",
                message=f"Your registration for '{event.title}' has been cancelled.",
                notification_type=NotificationType.REGISTRATION_CANCELLED,
                related_event_id=event.id,
                is_read=False,
            )
            db.add(notification)

        db.commit()
        db.refresh(registration)
        return registration

    @staticmethod
    def get_event_registrations(
        db: Session,
        event_id: int,
        status: Optional[RegistrationStatus] = None,
    ) -> List[EventRegistration]:
        """List all registrations for a specific event."""
        query = db.query(EventRegistration).filter(EventRegistration.event_id == event_id)
        if status:
            query = query.filter(EventRegistration.status == status)
        return query.order_by(EventRegistration.registered_at.asc()).all()

    @staticmethod
    def get_student_registrations(
        db: Session,
        student_id: int,
        status: Optional[RegistrationStatus] = None,
    ) -> List[RegistrationWithEventResponse]:
        """List registrations of a particular student."""
        query = (
            db.query(EventRegistration, Event)
            .join(Event, EventRegistration.event_id == Event.id)
            .filter(EventRegistration.student_id == student_id)
        )
        if status:
            query = query.filter(EventRegistration.status == status)

        records = query.order_by(Event.start_time.desc()).all()
        results = []
        for reg, ev in records:
            results.append(
                RegistrationWithEventResponse(
                    id=reg.id,
                    event_id=reg.event_id,
                    student_id=reg.student_id,
                    status=reg.status,
                    registered_at=reg.registered_at,
                    cancellation_reason=reg.cancellation_reason,
                    student=reg.student,
                    event_title=ev.title,
                    event_start_time=ev.start_time,
                    event_venue=ev.venue,
                    event_status=ev.status.value if hasattr(ev.status, "value") else str(ev.status),
                )
            )
        return results
