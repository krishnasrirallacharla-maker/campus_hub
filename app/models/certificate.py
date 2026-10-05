from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_code = Column(String(100), unique=True, nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    issue_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    issued_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student_certificate"),
    )

    # Relationships
    event = relationship("Event", back_populates="certificates")
    student = relationship("User", back_populates="certificates", foreign_keys=[student_id])
    issued_by = relationship("User", foreign_keys=[issued_by_id])
