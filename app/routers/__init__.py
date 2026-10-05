from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.departments import router as departments_router
from app.routers.events import router as events_router
from app.routers.registrations import router as registrations_router
from app.routers.attendances import router as attendances_router
from app.routers.notifications import router as notifications_router
from app.routers.feedbacks import router as feedbacks_router
from app.routers.certificates import router as certificates_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "users_router",
    "departments_router",
    "events_router",
    "registrations_router",
    "attendances_router",
    "notifications_router",
    "feedbacks_router",
    "certificates_router",
    "dashboard_router",
]
