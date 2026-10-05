from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import (
    get_current_faculty_or_admin,
    get_current_user,
)
from app.models.user import User
from app.schemas.certificate import (
    CertificateBulkIssueRequest,
    CertificateIssueRequest,
    CertificateResponse,
    CertificateVerificationResponse,
    CertificateWithEventResponse,
)
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates Management"])


@router.post(
    "/issue",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a certificate to a student (Faculty & Admin)",
)
def issue_certificate(
    req: CertificateIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return CertificateService.issue_certificate(db, req, current_user)


@router.post(
    "/bulk-issue",
    response_model=List[CertificateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk issue certificates to all present attendees of an event (Faculty & Admin)",
)
def bulk_issue_certificates(
    req: CertificateBulkIssueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return CertificateService.bulk_issue_certificates(db, req, current_user)


@router.get(
    "/verify/{certificate_code}",
    response_model=CertificateVerificationResponse,
    summary="Public verification endpoint for event certificates",
    description="Verify the validity and details of any issued certificate using its unique code.",
)
def verify_certificate(
    certificate_code: str,
    db: Session = Depends(get_db),
):
    return CertificateService.verify_certificate(db, certificate_code)


@router.get(
    "/my-certificates",
    response_model=List[CertificateWithEventResponse],
    summary="Get all certificates issued to current logged-in student",
)
def get_my_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CertificateService.get_student_certificates(db, current_user.id)


@router.get(
    "/event/{event_id}",
    response_model=List[CertificateResponse],
    summary="List all certificates issued for an event (Faculty & Admin)",
)
def get_event_certificates(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return CertificateService.get_event_certificates(db, event_id)


@router.post(
    "/{certificate_id}/revoke",
    response_model=CertificateResponse,
    summary="Revoke/Invalidate an issued certificate (Organizer & Admin)",
)
def revoke_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return CertificateService.revoke_certificate(db, certificate_id, current_user)
