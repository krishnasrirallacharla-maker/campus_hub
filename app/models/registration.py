from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import RegistrationStatus


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        SQLEnum(RegistrationStatus, native_enum=False),
        default=RegistrationStatus.CONFIRMED,
        nullable=False,
        index=True,
    )
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    cancellation_reason = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student_registration"),
    )

    # Relationships
    event = relationship("Event", back_populates="registrations")
    student = relationship("User", back_populates="registrations")
    attendance = relationship("Attendance", back_populates="registration", uselist=False)
