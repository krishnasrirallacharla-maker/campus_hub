from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_admin, get_current_faculty_or_admin
from app.models.user import User
from app.schemas.dashboard import AdminDashboardStats, FacultyDashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Statistics"])


@router.get(
    "/admin",
    response_model=AdminDashboardStats,
    summary="Get complete Admin Dashboard metrics and statistics (Admin only)",
    description="Returns aggregate counts for events, students, faculty, departments, registration rates, attendance rates, popular events, department breakdowns, and monthly trends.",
)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return DashboardService.get_admin_dashboard_stats(db)


@router.get(
    "/faculty",
    response_model=FacultyDashboardStats,
    summary="Get Faculty Dashboard overview (Faculty & Admin)",
    description="Returns organized events stats, registered students count, certificates count, average ratings, and recent events list.",
)
def get_faculty_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return DashboardService.get_faculty_dashboard_stats(db, current_user)
