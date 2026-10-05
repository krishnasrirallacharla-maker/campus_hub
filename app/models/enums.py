import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FACULTY = "faculty"
    STUDENT = "student"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RegistrationStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class NotificationType(str, enum.Enum):
    EVENT_UPDATE = "event_update"
    REGISTRATION_CONFIRMED = "registration_confirmed"
    REGISTRATION_CANCELLED = "registration_cancelled"
    ATTENDANCE_MARKED = "attendance_marked"
    CERTIFICATE_ISSUED = "certificate_issued"
    GENERAL = "general"
