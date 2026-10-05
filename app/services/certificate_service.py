from datetime import datetime, timezone
import secrets
import string
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AlreadyExistsException, BadRequestException, ForbiddenException, NotFoundException
from app.models.enums import AttendanceStatus, NotificationType, UserRole
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.user import User
from app.models.notification import Notification
from app.schemas.certificate import (
    CertificateBulkIssueRequest,
    CertificateIssueRequest,
    CertificateVerificationResponse,
    CertificateWithEventResponse,
)


def generate_unique_certificate_code(event_id: int) -> str:
    """Generate a clean, professional unique certificate code."""
    year = datetime.now(timezone.utc).year
    random_part = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"CERT-{year}-EV{event_id}-{random_part}"


class CertificateService:
    @staticmethod
    def issue_certificate(
        db: Session,
        req: CertificateIssueRequest,
        current_user: User,
    ) -> Certificate:
        event = db.query(Event).filter(Event.id == req.event_id).first()
        if not event:
            raise NotFoundException("Event", req.event_id)

        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("Only the event organizer or an admin can issue certificates")

        student = db.query(User).filter(User.id == req.student_id).first()
        if not student:
            raise NotFoundException("Student", req.student_id)

        existing = (
            db.query(Certificate)
            .filter(
                Certificate.event_id == req.event_id,
                Certificate.student_id == req.student_id,
            )
            .first()
        )
        if existing:
            raise AlreadyExistsException("Certificate", "event and student", f"Event {req.event_id}, Student {req.student_id}")

        code = generate_unique_certificate_code(event.id)
        title = req.title or f"Certificate of Participation - {event.title}"
        description = req.description or f"Successfully attended and participated in {event.title} at {event.venue}."

        certificate = Certificate(
            certificate_code=code,
            event_id=event.id,
            student_id=student.id,
            title=title,
            description=description,
            issue_date=datetime.now(timezone.utc),
            issued_by_id=current_user.id,
            is_valid=True,
        )
        db.add(certificate)

        # Send notification to student
        notification = Notification(
            recipient_id=student.id,
            title="Certificate Issued!",
            message=f"Congratulations! Your certificate for '{event.title}' has been issued. Certificate Code: {code}.",
            notification_type=NotificationType.CERTIFICATE_ISSUED,
            related_event_id=event.id,
            is_read=False,
        )
        db.add(notification)

        db.commit()
        db.refresh(certificate)
        return certificate

    @staticmethod
    def bulk_issue_certificates(
        db: Session,
        req: CertificateBulkIssueRequest,
        current_user: User,
    ) -> List[Certificate]:
        event = db.query(Event).filter(Event.id == req.event_id).first()
        if not event:
            raise NotFoundException("Event", req.event_id)

        if current_user.role != UserRole.ADMIN and event.organizer_id != current_user.id:
            raise ForbiddenException("Only the event organizer or an admin can issue certificates")

        # Find attendees
        att_query = db.query(Attendance).filter(Attendance.event_id == req.event_id)
        if req.only_present_attendees:
            att_query = att_query.filter(
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
            )
        attendees = att_query.all()

        issued_certificates = []
        for att in attendees:
            existing = (
                db.query(Certificate)
                .filter(
                    Certificate.event_id == req.event_id,
                    Certificate.student_id == att.student_id,
                )
                .first()
            )
            if existing:
                continue

            code = generate_unique_certificate_code(event.id)
            title = req.custom_title or f"Certificate of Participation - {event.title}"
            desc = req.custom_description or f"Successfully attended and completed {event.title}."

            cert = Certificate(
                certificate_code=code,
                event_id=event.id,
                student_id=att.student_id,
                title=title,
                description=desc,
                issue_date=datetime.now(timezone.utc),
                issued_by_id=current_user.id,
                is_valid=True,
            )
            db.add(cert)

            notification = Notification(
                recipient_id=att.student_id,
                title="Certificate Issued!",
                message=f"Congratulations! Your certificate for '{event.title}' is now available. Code: {code}.",
                notification_type=NotificationType.CERTIFICATE_ISSUED,
                related_event_id=event.id,
                is_read=False,
            )
            db.add(notification)
            issued_certificates.append(cert)

        db.commit()
        return issued_certificates

    @staticmethod
    def verify_certificate(db: Session, certificate_code: str) -> CertificateVerificationResponse:
        code_clean = certificate_code.strip().upper()
        cert = (
            db.query(Certificate)
            .filter(Certificate.certificate_code == code_clean)
            .first()
        )
        if not cert:
            raise NotFoundException("Certificate", certificate_code)

        event = cert.event
        student = cert.student
        dept = event.department if event else None
        organizer = event.organizer if event else None

        return CertificateVerificationResponse(
            is_valid=cert.is_valid,
            certificate_code=cert.certificate_code,
            student_name=student.full_name if student else "N/A",
            student_roll=student.roll_number if student else None,
            event_title=event.title if event else "N/A",
            event_date=event.start_time if event else cert.issue_date,
            issue_date=cert.issue_date,
            department_name=dept.name if dept else "College-Wide",
            organizer_name=organizer.full_name if organizer else "N/A",
        )

    @staticmethod
    def get_student_certificates(db: Session, student_id: int) -> List[CertificateWithEventResponse]:
        records = (
            db.query(Certificate, Event)
            .join(Event, Certificate.event_id == Event.id)
            .filter(Certificate.student_id == student_id)
            .order_by(Certificate.issue_date.desc())
            .all()
        )

        results = []
        for cert, ev in records:
            dept_name = ev.department.name if ev.department else "College-Wide"
            results.append(
                CertificateWithEventResponse(
                    id=cert.id,
                    certificate_code=cert.certificate_code,
                    event_id=cert.event_id,
                    student_id=cert.student_id,
                    title=cert.title,
                    description=cert.description,
                    issue_date=cert.issue_date,
                    issued_by_id=cert.issued_by_id,
                    is_valid=cert.is_valid,
                    student=cert.student,
                    event_title=ev.title,
                    event_date=ev.start_time,
                    event_venue=ev.venue,
                    student_name=cert.student.full_name if cert.student else None,
                    student_roll=cert.student.roll_number if cert.student else None,
                    department_name=dept_name,
                )
            )
        return results

    @staticmethod
    def get_event_certificates(db: Session, event_id: int) -> List[Certificate]:
        return (
            db.query(Certificate)
            .filter(Certificate.event_id == event_id)
            .order_by(Certificate.issue_date.desc())
            .all()
        )

    @staticmethod
    def revoke_certificate(db: Session, certificate_id: int, current_user: User) -> Certificate:
        cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not cert:
            raise NotFoundException("Certificate", certificate_id)

        if current_user.role != UserRole.ADMIN and (not cert.event or cert.event.organizer_id != current_user.id):
            raise ForbiddenException("Only the organizer or admin can revoke a certificate")

        cert.is_valid = False
        db.commit()
        db.refresh(cert)
        return cert
