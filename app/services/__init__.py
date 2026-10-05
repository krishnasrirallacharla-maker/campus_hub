from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.department_service import DepartmentService
from app.services.event_service import EventService
from app.services.registration_service import RegistrationService
from app.services.attendance_service import AttendanceService
from app.services.notification_service import NotificationService
from app.services.feedback_service import FeedbackService
from app.services.certificate_service import CertificateService
from app.services.dashboard_service import DashboardService

__all__ = [
    "AuthService",
    "UserService",
    "DepartmentService",
    "EventService",
    "RegistrationService",
    "AttendanceService",
    "NotificationService",
    "FeedbackService",
    "CertificateService",
    "DashboardService",
]
