from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.enums import NotificationType, RegistrationStatus, UserRole
from app.models.event import Event
from app.models.notification import Notification
from app.models.registration import EventRegistration
from app.models.user import User
from app.schemas.notification import (
    EventBroadcastNotification,
    NotificationCreate,
    SystemBroadcastNotification,
)


class NotificationService:
    @staticmethod
    def create_notification(db: Session, data: NotificationCreate) -> Notification:
        user = db.query(User).filter(User.id == data.recipient_id).first()
        if not user:
            raise NotFoundException("User", data.recipient_id)

        notification = Notification(
            recipient_id=data.recipient_id,
            title=data.title.strip(),
            message=data.message.strip(),
            notification_type=data.notification_type,
            related_event_id=data.related_event_id,
            is_read=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def broadcast_to_event_attendees(
        db: Session,
        event_id: int,
        data: EventBroadcastNotification,
        current_user: User,
    ) -> int:
        """Broadcast message to all confirmed students registered for an event."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundException("Event", event_id)

        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("Only the event organizer or an admin can broadcast notifications")

        registrations = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == RegistrationStatus.CONFIRMED,
            )
            .all()
        )

        notifications = []
        for reg in registrations:
            notifications.append(
                Notification(
                    recipient_id=reg.student_id,
                    title=f"[{event.title}] {data.title.strip()}",
                    message=data.message.strip(),
                    notification_type=data.notification_type,
                    related_event_id=event_id,
                    is_read=False,
                    created_at=datetime.now(timezone.utc),
                )
            )

        if notifications:
            db.add_all(notifications)
            db.commit()

        return len(notifications)

    @staticmethod
    def system_broadcast(
        db: Session,
        data: SystemBroadcastNotification,
        current_user: User,
    ) -> int:
        """Admin system-wide broadcast message."""
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Only admins can perform system broadcasts")

        query = db.query(User).filter(User.is_active == True)
        if data.target_role:
            query = query.filter(User.role == data.target_role)
        if data.department_id:
            query = query.filter(User.department_id == data.department_id)

        target_users = query.all()
        notifications = []
        for user in target_users:
            notifications.append(
                Notification(
                    recipient_id=user.id,
                    title=data.title.strip(),
                    message=data.message.strip(),
                    notification_type=NotificationType.GENERAL,
                    is_read=False,
                    created_at=datetime.now(timezone.utc),
                )
            )

        if notifications:
            db.add_all(notifications)
            db.commit()

        return len(notifications)

    @staticmethod
    def list_user_notifications(
        db: Session,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.recipient_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.recipient_id == user_id, Notification.is_read == False)
            .count()
        )

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.recipient_id == user_id)
            .first()
        )
        if not notif:
            raise NotFoundException("Notification", notification_id)

        notif.is_read = True
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        count = (
            db.query(Notification)
            .filter(Notification.recipient_id == user_id, Notification.is_read == False)
            .update({Notification.is_read: True})
        )
        db.commit()
        return count
