from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import EventStatus


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=False, index=True)  # Workshop, Seminar, Hackathon, Cultural, Sports, etc.
    venue = Column(String(200), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    registration_deadline = Column(DateTime(timezone=True), nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(SQLEnum(EventStatus, native_enum=False), default=EventStatus.DRAFT, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    banner_url = Column(String(500), nullable=True)
    is_certificate_provided = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    department = relationship("Department", back_populates="events")
    organizer = relationship("User", back_populates="organized_events")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    feedbacks = relationship("EventFeedback", back_populates="event", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="event", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="related_event", cascade="all, delete-orphan")
