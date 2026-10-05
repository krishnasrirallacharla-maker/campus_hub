from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import (
    get_current_faculty_or_admin,
    get_current_student,
    get_current_user,
)
from app.models.enums import RegistrationStatus
from app.models.user import User
from app.schemas.registration import (
    RegistrationCancel,
    RegistrationCreate,
    RegistrationResponse,
    RegistrationWithEventResponse,
)
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/registrations", tags=["Event Registrations"])


@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register for an event (Student)",
)
def register_for_event(
    req: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RegistrationService.register_for_event(db, req.event_id, current_user)


@router.post(
    "/{event_id}/cancel",
    response_model=RegistrationResponse,
    summary="Cancel registration for an event (Student)",
)
def cancel_registration(
    event_id: int,
    cancel_data: Optional[RegistrationCancel] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RegistrationService.cancel_registration(db, event_id, current_user, cancel_data)


@router.get(
    "/my-registrations",
    response_model=List[RegistrationWithEventResponse],
    summary="List all registrations of the current logged-in student",
)
def get_my_registrations(
    status: Optional[RegistrationStatus] = Query(None, description="Filter by registration status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RegistrationService.get_student_registrations(db, current_user.id, status=status)


@router.get(
    "/event/{event_id}",
    response_model=List[RegistrationResponse],
    summary="List all registered students for a specific event (Faculty & Admin)",
)
def get_event_registrations(
    event_id: int,
    status: Optional[RegistrationStatus] = Query(None, description="Filter by registration status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return RegistrationService.get_event_registrations(db, event_id, status=status)
