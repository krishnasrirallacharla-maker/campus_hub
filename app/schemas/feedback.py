from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserSummary


class FeedbackCreate(BaseModel):
    event_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comments: Optional[str] = Field(None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: int
    event_id: int
    student_id: int
    rating: int
    comments: Optional[str] = None
    submitted_at: datetime
    student: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class EventFeedbackSummary(BaseModel):
    event_id: int
    event_title: str
    total_feedbacks: int
    average_rating: float
    rating_distribution: dict  # {"1": count, "2": count, "3": count, "4": count, "5": count}
    feedbacks: List[FeedbackResponse]
