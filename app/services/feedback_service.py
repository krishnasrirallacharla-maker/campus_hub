from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.exceptions import AlreadyExistsException, BadRequestException, NotFoundException
from app.models.enums import AttendanceStatus, EventStatus, RegistrationStatus
from app.models.event import Event
from app.models.feedback import EventFeedback
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.feedback import EventFeedbackSummary, FeedbackCreate, FeedbackResponse


class FeedbackService:
    @staticmethod
    def submit_feedback(db: Session, data: FeedbackCreate, student: User) -> EventFeedback:
        event = db.query(Event).filter(Event.id == data.event_id).first()
        if not event:
            raise NotFoundException("Event", data.event_id)

        # Check if already submitted
        existing = (
            db.query(EventFeedback)
            .filter(
                EventFeedback.event_id == data.event_id,
                EventFeedback.student_id == student.id,
            )
            .first()
        )
        if existing:
            raise AlreadyExistsException("Feedback", "student_id", student.id)

        # Check that student was registered or attended
        reg = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == data.event_id,
                EventRegistration.student_id == student.id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .first()
        )
        if not reg:
            raise BadRequestException("You can only submit feedback for events you registered for")

        if data.rating < 1 or data.rating > 5:
            raise BadRequestException("Rating must be between 1 and 5")

        feedback = EventFeedback(
            event_id=data.event_id,
            student_id=student.id,
            rating=data.rating,
            comments=data.comments.strip() if data.comments else None,
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_event_feedback_summary(db: Session, event_id: int) -> EventFeedbackSummary:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)

        feedbacks = (
            db.query(EventFeedback)
            .filter(EventFeedback.event_id == event_id)
            .order_by(EventFeedback.submitted_at.desc())
            .all()
        )

        total_feedbacks = len(feedbacks)
        avg_rating = 0.0
        rating_dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

        if total_feedbacks > 0:
            total_score = sum(f.rating for f in feedbacks)
            avg_rating = round(total_score / total_feedbacks, 1)
            for f in feedbacks:
                key = str(f.rating)
                if key in rating_dist:
                    rating_dist[key] += 1

        return EventFeedbackSummary(
            event_id=event_id,
            event_title=event.title,
            total_feedbacks=total_feedbacks,
            average_rating=avg_rating,
            rating_distribution=rating_dist,
            feedbacks=[FeedbackResponse.model_validate(f) for f in feedbacks],
        )

    @staticmethod
    def get_student_feedbacks(db: Session, student_id: int) -> List[EventFeedback]:
        return (
            db.query(EventFeedback)
            .filter(EventFeedback.student_id == student_id)
            .order_by(EventFeedback.submitted_at.desc())
            .all()
        )
