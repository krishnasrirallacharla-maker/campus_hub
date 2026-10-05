from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import (
    get_current_faculty_or_admin,
    get_current_user,
    get_optional_current_user,
)
from app.models.enums import EventStatus
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventListResponse,
    EventResponse,
    EventStatusUpdate,
    EventUpdate,
)
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["College Events"])


@router.get(
    "",
    response_model=EventListResponse,
    summary="List college events with filters and pagination",
)
def list_events(
    status: Optional[EventStatus] = Query(None, description="Filter by event status"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    event_type: Optional[str] = Query(None, description="Filter by event category/type"),
    organizer_id: Optional[int] = Query(None, description="Filter by organizer ID"),
    upcoming_only: bool = Query(False, description="Show only future upcoming events"),
    search: Optional[str] = Query(None, description="Search event title, description, or venue"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    return EventService.list_events(
        db,
        status=status,
        department_id=department_id,
        event_type=event_type,
        organizer_id=organizer_id,
        upcoming_only=upcoming_only,
        search=search,
        page=page,
        size=size,
        current_user=current_user,
    )


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event (Faculty & Admin only)",
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    created_event = EventService.create_event(db, event_data, current_user)
    return EventService.format_event_response(db, created_event, current_user)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get single event details by ID",
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    event = EventService.get_by_id(db, event_id)
    return EventService.format_event_response(db, event, current_user)


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update event details (Organizer or Admin)",
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    updated = EventService.update_event(db, event_id, event_data, current_user)
    return EventService.format_event_response(db, updated, current_user)


@router.patch(
    "/{event_id}/status",
    response_model=EventResponse,
    summary="Update event status (Organizer or Admin)",
)
def update_event_status(
    event_id: int,
    status_data: EventStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    updated = EventService.update_event_status(db, event_id, status_data.status, current_user)
    return EventService.format_event_response(db, updated, current_user)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an event (Organizer or Admin)",
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    EventService.delete_event(db, event_id, current_user)
    return {"message": "Event deleted successfully"}
