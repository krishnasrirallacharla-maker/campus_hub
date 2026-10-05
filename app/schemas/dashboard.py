from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class DepartmentStats(BaseModel):
    department_id: Optional[int]
    department_name: str
    total_events: int
    total_students: int
    total_registrations: int


class PopularEvent(BaseModel):
    event_id: int
    title: str
    event_type: str
    capacity: int
    registration_count: int
    attendance_count: int
    fill_rate: float
    average_rating: Optional[float]


class MonthlyEventTrend(BaseModel):
    month: str
    event_count: int
    registration_count: int


class AdminDashboardStats(BaseModel):
    # Overall summary counts
    total_events: int
    total_students: int
    total_faculty: int
    total_departments: int
    total_registrations: int
    total_attendances_marked: int
    total_certificates_issued: int

    # Event breakdowns
    events_by_status: Dict[str, int]
    upcoming_events_count: int
    ongoing_events_count: int
    completed_events_count: int

    # Registration & Attendance KPIs
    overall_attendance_rate: float
    average_feedback_rating: float

    # Detailed statistics lists
    popular_events: List[PopularEvent]
    department_breakdown: List[DepartmentStats]
    monthly_trends: List[MonthlyEventTrend]


class FacultyDashboardStats(BaseModel):
    total_organized_events: int
    upcoming_events_count: int
    total_registered_students: int
    total_certificates_issued: int
    average_event_rating: float
    recent_events: List[Dict[str, Any]]
