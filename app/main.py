from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.database import Base, engine
from app.routers import (
    attendances_router,
    auth_router,
    certificates_router,
    dashboard_router,
    departments_router,
    events_router,
    feedbacks_router,
    notifications_router,
    registrations_router,
    users_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("college_events_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    logger.info("Starting up College Management Event System...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Database initialization warning (will be handled by Alembic): {e}")
    yield
    # Shutdown
    logger.info("Shutting down College Management Event System...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# College Management Event System API

A comprehensive backend system for managing college events, student registrations, attendance, certifications, feedbacks, and administrative dashboards.

## Features
- **JWT Authentication & RBAC**: Admin, Faculty, and Student roles
- **Department Management**: Academic departments and faculties
- **Event Lifecycle**: Creation, updates, draft/published/completed states, capacity and deadline enforcement
- **Student Registration**: Register, cancel, waitlist management
- **Attendance**: Single, bulk marking, self-check-in / QR validation
- **Notifications**: Automated event reminders, system & event broadcasts
- **Feedback & Ratings**: 1-5 star reviews with aggregated statistics
- **Certificate Management**: Verification codes, public verification endpoint, batch issuance
- **Dashboards**: Full analytics for Admins and Faculty
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if "*" not in settings.BACKEND_CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        msg = err.get("msg", "Invalid value")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred. Please try again later.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# Health check / Root endpoints
@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
    }


# Include API Routers under /api/v1
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(users_router, prefix=api_v1_prefix)
app.include_router(departments_router, prefix=api_v1_prefix)
app.include_router(events_router, prefix=api_v1_prefix)
app.include_router(registrations_router, prefix=api_v1_prefix)
app.include_router(attendances_router, prefix=api_v1_prefix)
app.include_router(notifications_router, prefix=api_v1_prefix)
app.include_router(feedbacks_router, prefix=api_v1_prefix)
app.include_router(certificates_router, prefix=api_v1_prefix)
app.include_router(dashboard_router, prefix=api_v1_prefix)
