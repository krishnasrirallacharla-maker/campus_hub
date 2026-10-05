"""Database Seeder Script for College Management Event System."""
import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.enums import AttendanceStatus, EventStatus, NotificationType, RegistrationStatus, UserRole
from app.models.department import Department
from app.models.user import User
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.feedback import EventFeedback
from app.models.certificate import Certificate
from app.models.notification import Notification
from app.services.certificate_service import generate_unique_certificate_code


def seed_database():
    print("Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        admin_user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if admin_user:
            print(f"Database already contains admin user ({settings.FIRST_SUPERUSER_EMAIL}). Skipping seed.")
            return

        print("Seeding initial data...")
        now = datetime.now(timezone.utc)

        # 1. Seed Departments
        dept_cs = Department(
            name="Computer Science and Engineering",
            code="CSE",
            description="Department of Computer Science and Engineering",
            head_of_department="Dr. Alan Turing",
        )
        dept_ec = Department(
            name="Electronics and Communication",
            code="ECE",
            description="Department of Electronics and Communication Engineering",
            head_of_department="Dr. Claude Shannon",
        )
        dept_me = Department(
            name="Mechanical Engineering",
            code="MECH",
            description="Department of Mechanical Engineering",
            head_of_department="Dr. James Watt",
        )
        dept_mba = Department(
            name="Management Studies",
            code="MBA",
            description="Department of Business Administration and Management",
            head_of_department="Dr. Peter Drucker",
        )

        db.add_all([dept_cs, dept_ec, dept_me, dept_mba])
        db.flush()

        # 2. Seed Users
        # Admin
        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name=settings.FIRST_SUPERUSER_NAME,
            role=UserRole.ADMIN,
            is_active=True,
        )

        # Faculty members
        faculty_cs = User(
            email="prof.sharma@college.edu",
            hashed_password=get_password_hash("FacultyPass123!"),
            full_name="Prof. Rajesh Sharma",
            role=UserRole.FACULTY,
            department_id=dept_cs.id,
            phone="+91 9876543210",
            is_active=True,
        )
        faculty_ec = User(
            email="dr.anita@college.edu",
            hashed_password=get_password_hash("FacultyPass123!"),
            full_name="Dr. Anita Desai",
            role=UserRole.FACULTY,
            department_id=dept_ec.id,
            phone="+91 9876543211",
            is_active=True,
        )

        # Students
        student1 = User(
            email="rahul.verma@student.college.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Rahul Verma",
            role=UserRole.STUDENT,
            department_id=dept_cs.id,
            roll_number="CSE2024-001",
            phone="+91 9123456780",
            is_active=True,
        )
        student2 = User(
            email="priya.patel@student.college.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Priya Patel",
            role=UserRole.STUDENT,
            department_id=dept_cs.id,
            roll_number="CSE2024-002",
            phone="+91 9123456781",
            is_active=True,
        )
        student3 = User(
            email="amit.singh@student.college.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Amit Singh",
            role=UserRole.STUDENT,
            department_id=dept_ec.id,
            roll_number="ECE2024-015",
            phone="+91 9123456782",
            is_active=True,
        )
        student4 = User(
            email="sneha.reddy@student.college.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="Sneha Reddy",
            role=UserRole.STUDENT,
            department_id=dept_me.id,
            roll_number="ME2024-042",
            phone="+91 9123456783",
            is_active=True,
        )

        db.add_all([admin, faculty_cs, faculty_ec, student1, student2, student3, student4])
        db.flush()

        # 3. Seed Events
        event1 = Event(
            title="National Level Hackathon - CodeSprint 2026",
            description="A 36-hour continuous software hackathon featuring tracks in AI/ML, Web3, and IoT.",
            event_type="Hackathon",
            venue="Tech Park, Seminar Hall 1 & Labs",
            start_time=now + timedelta(days=10, hours=9),
            end_time=now + timedelta(days=11, hours=21),
            registration_deadline=now + timedelta(days=8),
            capacity=120,
            status=EventStatus.PUBLISHED,
            department_id=dept_cs.id,
            organizer_id=faculty_cs.id,
            is_certificate_provided=True,
        )

        event2 = Event(
            title="Hands-on Workshop: Deep Learning with PyTorch",
            description="Intensive workshop covering neural networks, CNNs, Transformers, and deployment techniques.",
            event_type="Workshop",
            venue="Computer Lab 4, Block B",
            start_time=now - timedelta(days=5),
            end_time=now - timedelta(days=5, hours=-6),
            registration_deadline=now - timedelta(days=7),
            capacity=50,
            status=EventStatus.COMPLETED,
            department_id=dept_cs.id,
            organizer_id=faculty_cs.id,
            is_certificate_provided=True,
        )

        event3 = Event(
            title="Guest Lecture: VLSI Design and Embedded AI",
            description="Distinguished lecture by industry leaders from Qualcomm on next-generation edge silicon.",
            event_type="Guest Lecture",
            venue="Main Auditorium",
            start_time=now + timedelta(days=15, hours=14),
            end_time=now + timedelta(days=15, hours=17),
            registration_deadline=now + timedelta(days=14),
            capacity=200,
            status=EventStatus.PUBLISHED,
            department_id=dept_ec.id,
            organizer_id=faculty_ec.id,
            is_certificate_provided=True,
        )

        event4 = Event(
            title="Annual Inter-College Cultural Fest - तरंग 2026",
            description="Grand annual cultural festival with music, dance, theater, and fine arts competitions.",
            event_type="Cultural",
            venue="College Amphitheatre & Grounds",
            start_time=now + timedelta(days=30),
            end_time=now + timedelta(days=32),
            registration_deadline=now + timedelta(days=25),
            capacity=500,
            status=EventStatus.PUBLISHED,
            department_id=None,  # College-wide
            organizer_id=admin.id,
            is_certificate_provided=True,
        )

        db.add_all([event1, event2, event3, event4])
        db.flush()

        # 4. Seed Registrations
        # Event 1 (Upcoming Hackathon) Registrations
        reg1_e1 = EventRegistration(event_id=event1.id, student_id=student1.id, status=RegistrationStatus.CONFIRMED)
        reg2_e1 = EventRegistration(event_id=event1.id, student_id=student2.id, status=RegistrationStatus.CONFIRMED)
        reg3_e1 = EventRegistration(event_id=event1.id, student_id=student3.id, status=RegistrationStatus.CONFIRMED)

        # Event 2 (Completed PyTorch Workshop) Registrations
        reg1_e2 = EventRegistration(event_id=event2.id, student_id=student1.id, status=RegistrationStatus.CONFIRMED)
        reg2_e2 = EventRegistration(event_id=event2.id, student_id=student2.id, status=RegistrationStatus.CONFIRMED)
        reg4_e2 = EventRegistration(event_id=event2.id, student_id=student4.id, status=RegistrationStatus.CONFIRMED)

        db.add_all([reg1_e1, reg2_e1, reg3_e1, reg1_e2, reg2_e2, reg4_e2])
        db.flush()

        # 5. Seed Attendance for Completed Event (Event 2)
        att1_e2 = Attendance(
            event_id=event2.id,
            student_id=student1.id,
            registration_id=reg1_e2.id,
            status=AttendanceStatus.PRESENT,
            marked_at=event2.start_time + timedelta(minutes=15),
            marked_by_id=faculty_cs.id,
            notes="Active participation in lab practicals",
        )
        att2_e2 = Attendance(
            event_id=event2.id,
            student_id=student2.id,
            registration_id=reg2_e2.id,
            status=AttendanceStatus.PRESENT,
            marked_at=event2.start_time + timedelta(minutes=10),
            marked_by_id=faculty_cs.id,
            notes="Completed all coding exercises",
        )
        att4_e2 = Attendance(
            event_id=event2.id,
            student_id=student4.id,
            registration_id=reg4_e2.id,
            status=AttendanceStatus.ABSENT,
            marked_at=event2.start_time + timedelta(minutes=45),
            marked_by_id=faculty_cs.id,
            notes="Did not attend",
        )

        db.add_all([att1_e2, att2_e2, att4_e2])
        db.flush()

        # 6. Seed Feedbacks for Event 2
        fb1 = EventFeedback(
            event_id=event2.id,
            student_id=student1.id,
            rating=5,
            comments="Excellent workshop! The hands-on labs were extremely practical and well-structured.",
            submitted_at=event2.end_time + timedelta(hours=2),
        )
        fb2 = EventFeedback(
            event_id=event2.id,
            student_id=student2.id,
            rating=4,
            comments="Very informative session. Would love an advanced part 2 on Transformer architectures.",
            submitted_at=event2.end_time + timedelta(hours=4),
        )

        db.add_all([fb1, fb2])
        db.flush()

        # 7. Seed Certificates for Event 2 attendees
        cert1 = Certificate(
            certificate_code=generate_unique_certificate_code(event2.id),
            event_id=event2.id,
            student_id=student1.id,
            title="Certificate of Completion - Deep Learning with PyTorch",
            description="Successfully completed the 6-hour intensive PyTorch workshop with practical hands-on assessments.",
            issue_date=event2.end_time + timedelta(days=1),
            issued_by_id=faculty_cs.id,
            is_valid=True,
        )
        cert2 = Certificate(
            certificate_code=generate_unique_certificate_code(event2.id),
            event_id=event2.id,
            student_id=student2.id,
            title="Certificate of Completion - Deep Learning with PyTorch",
            description="Successfully completed the 6-hour intensive PyTorch workshop with practical hands-on assessments.",
            issue_date=event2.end_time + timedelta(days=1),
            issued_by_id=faculty_cs.id,
            is_valid=True,
        )

        db.add_all([cert1, cert2])
        db.flush()

        # 8. Seed Notifications
        n1 = Notification(
            recipient_id=student1.id,
            title="Registration Confirmed",
            message=f"You have successfully registered for '{event1.title}'.",
            notification_type=NotificationType.REGISTRATION_CONFIRMED,
            related_event_id=event1.id,
            is_read=True,
        )
        n2 = Notification(
            recipient_id=student1.id,
            title="Certificate Issued!",
            message=f"Your certificate for '{event2.title}' is ready for download. Code: {cert1.certificate_code}.",
            notification_type=NotificationType.CERTIFICATE_ISSUED,
            related_event_id=event2.id,
            is_read=False,
        )
        n3 = Notification(
            recipient_id=student2.id,
            title="Registration Confirmed",
            message=f"You have successfully registered for '{event1.title}'.",
            notification_type=NotificationType.REGISTRATION_CONFIRMED,
            related_event_id=event1.id,
            is_read=False,
        )

        db.add_all([n1, n2, n3])
        db.commit()

        print("Successfully seeded initial data:")
        print(f"  - Admin: {admin.email} (Password: {settings.FIRST_SUPERUSER_PASSWORD})")
        print(f"  - Faculty: {faculty_cs.email} (Password: FacultyPass123!)")
        print(f"  - Student: {student1.email} (Password: StudentPass123!)")
        print("  - 4 Departments, 4 Events, 6 Registrations, 3 Attendance records, 2 Certificates, 2 Feedbacks.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
