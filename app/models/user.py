from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), default=UserRole.STUDENT, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    roll_number = Column(String(50), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    department = relationship("Department", back_populates="users")
    organized_events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
    registrations = relationship("EventRegistration", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship(
        "Attendance",
        back_populates="student",
        foreign_keys="Attendance.student_id",
        cascade="all, delete-orphan",
    )
    feedbacks = relationship("EventFeedback", back_populates="student", cascade="all, delete-orphan")
    certificates = relationship(
        "Certificate",
        back_populates="student",
        foreign_keys="Certificate.student_id",
        cascade="all, delete-orphan",
    )
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
