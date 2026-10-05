from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class EventFeedback(Base):
    __tablename__ = "event_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comments = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student_feedback"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Relationships
    event = relationship("Event", back_populates="feedbacks")
    student = relationship("User", back_populates="feedbacks")
