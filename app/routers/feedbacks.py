from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.feedback import EventFeedbackSummary, FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedbacks", tags=["Feedback and Ratings"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback and rating (1-5) for an event (Student)",
)
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FeedbackService.submit_feedback(db, data, current_user)


@router.get(
    "/event/{event_id}",
    response_model=EventFeedbackSummary,
    summary="Get feedback breakdown, average rating, and comments for an event",
)
def get_event_feedbacks(
    event_id: int,
    db: Session = Depends(get_db),
):
    return FeedbackService.get_event_feedback_summary(db, event_id)


@router.get(
    "/my-feedbacks",
    response_model=List[FeedbackResponse],
    summary="Get all feedbacks submitted by the logged-in student",
)
def get_my_feedbacks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FeedbackService.get_student_feedbacks(db, current_user.id)
