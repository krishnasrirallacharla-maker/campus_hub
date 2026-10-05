from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.enums import AttendanceStatus, EventStatus, RegistrationStatus, UserRole
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.feedback import EventFeedback
from app.models.department import Department
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse, EventUpdate


class EventService:
    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Event:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)
        return event

    @staticmethod
    def format_event_response(
        db: Session,
        event: Event,
        current_user: Optional[User] = None,
    ) -> EventResponse:
        # Calculate active registrations (CONFIRMED)
        reg_count = (
            db.query(func.count(EventRegistration.id))
            .filter(
                EventRegistration.event_id == event.id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )
        available_seats = max(0, event.capacity - reg_count)

        # Feedbacks
        feedback_stats = (
            db.query(
                func.count(EventFeedback.id).label("count"),
                func.avg(EventFeedback.rating).label("avg_rating"),
            )
            .filter(EventFeedback.event_id == event.id)
            .first()
        )
        total_feedbacks = feedback_stats.count if feedback_stats else 0
        avg_rating = round(float(feedback_stats.avg_rating), 1) if (feedback_stats and feedback_stats.avg_rating) else None

        # User-specific flags
        is_registered = False
        is_attended = False
        if current_user:
            user_reg = (
                db.query(EventRegistration)
                .filter(
                    EventRegistration.event_id == event.id,
                    EventRegistration.student_id == current_user.id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED,
                )
                .first()
            )
            is_registered = user_reg is not None

            user_att = (
                db.query(Attendance)
                .filter(
                    Attendance.event_id == event.id,
                    Attendance.student_id == current_user.id,
                    Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
                )
                .first()
            )
            is_attended = user_att is not None

        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            event_type=event.event_type,
            venue=event.venue,
            start_time=event.start_time,
            end_time=event.end_time,
            registration_deadline=event.registration_deadline,
            capacity=event.capacity,
            status=event.status,
            department_id=event.department_id,
            organizer_id=event.organizer_id,
            banner_url=event.banner_url,
            is_certificate_provided=event.is_certificate_provided,
            created_at=event.created_at,
            updated_at=event.updated_at,
            organizer=event.organizer,
            department=event.department,
            registered_count=reg_count,
            available_seats=available_seats,
            is_registered=is_registered,
            is_attended=is_attended,
            average_rating=avg_rating,
            total_feedbacks=total_feedbacks,
        )

    @staticmethod
    def list_events(
        db: Session,
        status: Optional[EventStatus] = None,
        department_id: Optional[int] = None,
        event_type: Optional[str] = None,
        organizer_id: Optional[int] = None,
        upcoming_only: bool = False,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        current_user: Optional[User] = None,
    ) -> Dict[str, Any]:
        query = db.query(Event)

        # Visibility rule: Students/Anonymous see only PUBLISHED, ONGOING, COMPLETED by default unless specified
        if current_user is None or current_user.role == UserRole.STUDENT:
            if status:
                query = query.filter(Event.status == status)
            else:
                query = query.filter(Event.status.in_([EventStatus.PUBLISHED, EventStatus.ONGOING, EventStatus.COMPLETED]))
        else:
            # Faculty/Admin can see drafts, cancelled, etc.
            if status:
                query = query.filter(Event.status == status)

        if department_id is not None:
            query = query.filter(Event.department_id == department_id)

        if event_type:
            query = query.filter(Event.event_type.ilike(f"%{event_type.strip()}%"))

        if organizer_id is not None:
            query = query.filter(Event.organizer_id == organizer_id)

        if upcoming_only:
            now_utc = datetime.now(timezone.utc)
            query = query.filter(Event.start_time >= now_utc)

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search_pattern),
                    Event.description.ilike(search_pattern),
                    Event.venue.ilike(search_pattern),
                    Event.event_type.ilike(search_pattern),
                )
            )

        total = query.count()
        offset = (page - 1) * size
        events = query.order_by(Event.start_time.asc()).offset(offset).limit(size).all()
        pages = (total + size - 1) // size if size > 0 else 1

        items = [EventService.format_event_response(db, ev, current_user) for ev in events]

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    @staticmethod
    def create_event(db: Session, event_data: EventCreate, current_user: User) -> Event:
        # Check permissions: Admin or Faculty
        if current_user.role not in [UserRole.ADMIN, UserRole.FACULTY]:
            raise ForbiddenException("Only Faculty and Admins can create events")

        # If faculty and no department specified, default to faculty department
        department_id = event_data.department_id
        if department_id is None and current_user.role == UserRole.FACULTY:
            department_id = current_user.department_id

        if department_id:
            dept = db.query(Department).filter(Department.id == department_id).first()
            if not dept:
                raise NotFoundException("Department", department_id)

        event = Event(
            title=event_data.title.strip(),
            description=event_data.description.strip(),
            event_type=event_data.event_type.strip(),
            venue=event_data.venue.strip(),
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            registration_deadline=event_data.registration_deadline,
            capacity=event_data.capacity,
            status=event_data.status or EventStatus.PUBLISHED,
            department_id=department_id,
            organizer_id=current_user.id,
            banner_url=event_data.banner_url.strip() if event_data.banner_url else None,
            is_certificate_provided=event_data.is_certificate_provided,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update_event(
        db: Session,
        event_id: int,
        event_data: EventUpdate,
        current_user: User,
    ) -> Event:
        event = EventService.get_by_id(db, event_id)

        # Permission check: Admin or event organizer
        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("You can only edit events you created or you must be an admin")

        if event_data.department_id is not None:
            if event_data.department_id:
                dept = db.query(Department).filter(Department.id == event_data.department_id).first()
                if not dept:
                    raise NotFoundException("Department", event_data.department_id)
            event.department_id = event_data.department_id

        if event_data.title is not None:
            event.title = event_data.title.strip()
        if event_data.description is not None:
            event.description = event_data.description.strip()
        if event_data.event_type is not None:
            event.event_type = event_data.event_type.strip()
        if event_data.venue is not None:
            event.venue = event_data.venue.strip()
        if event_data.start_time is not None:
            event.start_time = event_data.start_time
        if event_data.end_time is not None:
            event.end_time = event_data.end_time
        if event_data.registration_deadline is not None:
            event.registration_deadline = event_data.registration_deadline
        if event_data.capacity is not None:
            event.capacity = event_data.capacity
        if event_data.status is not None:
            event.status = event_data.status
        if event_data.banner_url is not None:
            event.banner_url = event_data.banner_url.strip() if event_data.banner_url else None
        if event_data.is_certificate_provided is not None:
            event.is_certificate_provided = event_data.is_certificate_provided

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update_event_status(
        db: Session,
        event_id: int,
        status: EventStatus,
        current_user: User,
    ) -> Event:
        event = EventService.get_by_id(db, event_id)
        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("You can only update status of events you organized or you must be an admin")
        event.status = status
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_event(db: Session, event_id: int, current_user: User) -> bool:
        event = EventService.get_by_id(db, event_id)
        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("You can only delete events you created or you must be an admin")
        db.delete(event)
        db.commit()
        return True
