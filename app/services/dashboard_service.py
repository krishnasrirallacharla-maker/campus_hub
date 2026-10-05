from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.enums import AttendanceStatus, EventStatus, RegistrationStatus, UserRole
from app.models.event import Event
from app.models.registration import EventRegistration
from app.models.attendance import Attendance
from app.models.feedback import EventFeedback
from app.models.certificate import Certificate
from app.models.department import Department
from app.models.user import User
from app.schemas.dashboard import (
    AdminDashboardStats,
    DepartmentStats,
    FacultyDashboardStats,
    MonthlyEventTrend,
    PopularEvent,
)


def ensure_utc(dt: datetime) -> datetime:
    if dt is None:
        return dt
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class DashboardService:
    @staticmethod
    def get_admin_dashboard_stats(db: Session) -> AdminDashboardStats:
        now_utc = datetime.now(timezone.utc)

        # Totals
        total_events = db.query(func.count(Event.id)).scalar() or 0
        total_students = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar() or 0
        total_faculty = db.query(func.count(User.id)).filter(User.role == UserRole.FACULTY).scalar() or 0
        total_departments = db.query(func.count(Department.id)).scalar() or 0
        total_registrations = (
            db.query(func.count(EventRegistration.id))
            .filter(EventRegistration.status == RegistrationStatus.CONFIRMED)
            .scalar()
            or 0
        )
        total_attendances_marked = db.query(func.count(Attendance.id)).scalar() or 0
        total_certificates_issued = (
            db.query(func.count(Certificate.id)).filter(Certificate.is_valid == True).scalar() or 0
        )

        # Status counts
        status_counts_raw = (
            db.query(Event.status, func.count(Event.id)).group_by(Event.status).all()
        )
        events_by_status = {s.value: 0 for s in EventStatus}
        for st, count in status_counts_raw:
            key = st.value if hasattr(st, "value") else str(st)
            events_by_status[key] = count

        upcoming_count = (
            db.query(func.count(Event.id))
            .filter(Event.start_time > now_utc, Event.status != EventStatus.CANCELLED)
            .scalar()
            or 0
        )
        ongoing_count = events_by_status.get(EventStatus.ONGOING.value, 0)
        completed_count = events_by_status.get(EventStatus.COMPLETED.value, 0)

        # Overall attendance rate (attended / total confirmed registrations)
        attended_count = (
            db.query(func.count(Attendance.id))
            .filter(Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]))
            .scalar()
            or 0
        )
        attendance_rate = (
            round((attended_count / total_registrations * 100), 1) if total_registrations > 0 else 0.0
        )

        # Average feedback rating
        avg_rating_raw = db.query(func.avg(EventFeedback.rating)).scalar()
        average_feedback_rating = round(float(avg_rating_raw), 1) if avg_rating_raw else 0.0

        # Popular events (top 5 by registration count)
        top_events_query = (
            db.query(
                Event,
                func.count(EventRegistration.id).label("reg_count"),
            )
            .outerjoin(
                EventRegistration,
                (Event.id == EventRegistration.event_id)
                & (EventRegistration.status == RegistrationStatus.CONFIRMED),
            )
            .group_by(Event.id)
            .order_by(func.count(EventRegistration.id).desc())
            .limit(5)
            .all()
        )

        popular_events: List[PopularEvent] = []
        for ev, r_count in top_events_query:
            att_count = (
                db.query(func.count(Attendance.id))
                .filter(
                    Attendance.event_id == ev.id,
                    Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE]),
                )
                .scalar()
                or 0
            )
            fill_rate = round((r_count / ev.capacity * 100), 1) if ev.capacity > 0 else 0.0

            ev_avg_rating = (
                db.query(func.avg(EventFeedback.rating))
                .filter(EventFeedback.event_id == ev.id)
                .scalar()
            )

            popular_events.append(
                PopularEvent(
                    event_id=ev.id,
                    title=ev.title,
                    event_type=ev.event_type,
                    capacity=ev.capacity,
                    registration_count=r_count,
                    attendance_count=att_count,
                    fill_rate=fill_rate,
                    average_rating=round(float(ev_avg_rating), 1) if ev_avg_rating else None,
                )
            )

        # Department breakdown
        dept_breakdown: List[DepartmentStats] = []
        depts = db.query(Department).all()
        for d in depts:
            d_events = db.query(func.count(Event.id)).filter(Event.department_id == d.id).scalar() or 0
            d_students = (
                db.query(func.count(User.id))
                .filter(User.department_id == d.id, User.role == UserRole.STUDENT)
                .scalar()
                or 0
            )
            d_regs = (
                db.query(func.count(EventRegistration.id))
                .join(Event, EventRegistration.event_id == Event.id)
                .filter(
                    Event.department_id == d.id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED,
                )
                .scalar()
                or 0
            )
            dept_breakdown.append(
                DepartmentStats(
                    department_id=d.id,
                    department_name=d.name,
                    total_events=d_events,
                    total_students=d_students,
                    total_registrations=d_regs,
                )
            )

        # Monthly trends (last 6 months or current year events)
        # Standard aggregation
        all_events = db.query(Event).order_by(Event.start_time.asc()).all()
        monthly_map: Dict[str, Dict[str, int]] = {}
        for ev in all_events:
            month_key = ev.start_time.strftime("%b %Y")
            if month_key not in monthly_map:
                monthly_map[month_key] = {"events": 0, "registrations": 0}
            monthly_map[month_key]["events"] += 1
            regs_for_ev = (
                db.query(func.count(EventRegistration.id))
                .filter(
                    EventRegistration.event_id == ev.id,
                    EventRegistration.status == RegistrationStatus.CONFIRMED,
                )
                .scalar()
                or 0
            )
            monthly_map[month_key]["registrations"] += regs_for_ev

        monthly_trends = [
            MonthlyEventTrend(
                month=m,
                event_count=data["events"],
                registration_count=data["registrations"],
            )
            for m, data in monthly_map.items()
        ]

        return AdminDashboardStats(
            total_events=total_events,
            total_students=total_students,
            total_faculty=total_faculty,
            total_departments=total_departments,
            total_registrations=total_registrations,
            total_attendances_marked=total_attendances_marked,
            total_certificates_issued=total_certificates_issued,
            events_by_status=events_by_status,
            upcoming_events_count=upcoming_count,
            ongoing_events_count=ongoing_count,
            completed_events_count=completed_count,
            overall_attendance_rate=attendance_rate,
            average_feedback_rating=average_feedback_rating,
            popular_events=popular_events,
            department_breakdown=dept_breakdown,
            monthly_trends=monthly_trends,
        )

    @staticmethod
    def get_faculty_dashboard_stats(db: Session, faculty_user: User) -> FacultyDashboardStats:
        now_utc = datetime.now(timezone.utc)
        my_events = db.query(Event).filter(Event.organizer_id == faculty_user.id).all()
        event_ids = [e.id for e in my_events]

        total_organized = len(my_events)
        upcoming = sum(1 for e in my_events if ensure_utc(e.start_time) > now_utc and e.status != EventStatus.CANCELLED)

        total_regs = 0
        total_certs = 0
        avg_rating = 0.0

        if event_ids:
            total_regs = (
                db.query(func.count(EventRegistration.id))
                .filter(
                    EventRegistration.event_id.in_(event_ids),
                    EventRegistration.status == RegistrationStatus.CONFIRMED,
                )
                .scalar()
                or 0
            )
            total_certs = (
                db.query(func.count(Certificate.id))
                .filter(Certificate.event_id.in_(event_ids), Certificate.is_valid == True)
                .scalar()
                or 0
            )
            avg_r = (
                db.query(func.avg(EventFeedback.rating))
                .filter(EventFeedback.event_id.in_(event_ids))
                .scalar()
            )
            avg_rating = round(float(avg_r), 1) if avg_r else 0.0

        recent_events = [
            {
                "id": e.id,
                "title": e.title,
                "event_type": e.event_type,
                "start_time": e.start_time.isoformat(),
                "status": e.status.value,
                "capacity": e.capacity,
            }
            for e in sorted(my_events, key=lambda x: x.start_time, reverse=True)[:5]
        ]

        return FacultyDashboardStats(
            total_organized_events=total_organized,
            upcoming_events_count=upcoming,
            total_registered_students=total_regs,
            total_certificates_issued=total_certs,
            average_event_rating=avg_rating,
            recent_events=recent_events,
        )
