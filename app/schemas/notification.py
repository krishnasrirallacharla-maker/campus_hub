from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import NotificationType


class NotificationCreate(BaseModel):
    recipient_id: int
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2)
    notification_type: NotificationType = NotificationType.GENERAL
    related_event_id: Optional[int] = None


class EventBroadcastNotification(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2)
    notification_type: NotificationType = NotificationType.EVENT_UPDATE


class SystemBroadcastNotification(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2)
    target_role: Optional[str] = None  # None for everyone, or "student", "faculty"
    department_id: Optional[int] = None


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    title: str
    message: str
    notification_type: NotificationType
    related_event_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    unread_count: int
