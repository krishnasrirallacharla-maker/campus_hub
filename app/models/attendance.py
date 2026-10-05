from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import AttendanceStatus


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = Column(Integer, ForeignKey("event_registrations.id", ondelete="SET NULL"), nullable=True)
    status = Column(
        SQLEnum(AttendanceStatus, native_enum=False),
        default=AttendanceStatus.PRESENT,
        nullable=False,
        index=True,
    )
    marked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    marked_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    check_in_code = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student_attendance"),
    )

    # Relationships
    event = relationship("Event", back_populates="attendances")
    student = relationship("User", back_populates="attendances", foreign_keys=[student_id])
    registration = relationship("EventRegistration", back_populates="attendance")
    marked_by = relationship("User", foreign_keys=[marked_by_id])
