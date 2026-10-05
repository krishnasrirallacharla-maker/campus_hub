from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(
        SQLEnum(NotificationType, native_enum=False),
        default=NotificationType.GENERAL,
        nullable=False,
        index=True,
    )
    related_event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    recipient = relationship("User", back_populates="notifications")
    related_event = relationship("Event", back_populates="notifications")
