from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import (
    get_current_admin,
    get_current_faculty_or_admin,
    get_current_user,
)
from app.models.user import User
from app.schemas.notification import (
    EventBroadcastNotification,
    NotificationCreate,
    NotificationResponse,
    SystemBroadcastNotification,
    UnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=List[NotificationResponse],
    summary="Get notifications for current user",
)
def get_my_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.list_user_notifications(
        db, current_user.id, unread_only=unread_only, skip=skip, limit=limit
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get count of unread notifications for current user",
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = NotificationService.get_unread_count(db, current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a specific notification as read",
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.mark_as_read(db, notification_id, current_user.id)


@router.post(
    "/read-all",
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read for current user",
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = NotificationService.mark_all_as_read(db, current_user.id)
    return {"message": f"{count} notifications marked as read"}


@router.post(
    "/event/{event_id}/broadcast",
    status_code=status.HTTP_200_OK,
    summary="Broadcast notification to all registered attendees of an event (Faculty & Admin)",
)
def broadcast_to_event(
    event_id: int,
    data: EventBroadcastNotification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    count = NotificationService.broadcast_to_event_attendees(db, event_id, data, current_user)
    return {"message": f"Broadcast sent to {count} registered attendees"}


@router.post(
    "/system-broadcast",
    status_code=status.HTTP_200_OK,
    summary="Send system-wide broadcast notification (Admin only)",
)
def system_broadcast(
    data: SystemBroadcastNotification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    count = NotificationService.system_broadcast(db, data, current_user)
    return {"message": f"System broadcast sent to {count} users"}
