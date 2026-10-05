# College Management Event System Backend

A robust, production-ready backend system for managing college events built with **Python FastAPI**, **PostgreSQL**, **SQLAlchemy ORM (2.0)**, **Pydantic (v2)**, and **Alembic Migrations**.

---

## 🌟 Key Features

1. **JWT Authentication & Role-Based Access Control (RBAC)**:
   - Three distinct roles: `Admin`, `Faculty`, `Student`.
   - Secure password hashing using `bcrypt`.
   - Token validation, auto-expiry, and role dependency guards.
2. **User & Department Management**:
   - Full CRUD for academic departments with student, faculty, and event metrics.
   - User creation, profile updates, password changes, and administrator password resets.
3. **Event Lifecycle Management**:
   - Create, update, filter, search, and delete events.
   - Event states: `Draft`, `Published`, `Ongoing`, `Completed`, `Cancelled`.
   - Automatic seat availability calculations and rating aggregation.
4. **Student Registrations**:
   - Validation against capacity limits and registration deadlines.
   - Self-service registration cancellation with audit reason.
   - Automatic in-app confirmation and cancellation notifications.
5. **Attendance Management**:
   - Single student and bulk attendance marking (`Present`, `Absent`, `Late`, `Excused`).
   - Student self-service / QR code check-in endpoint.
   - Comprehensive event attendance summary and student attendance history.
6. **In-App Notifications**:
   - Automated event triggers (registration, attendance, certificate issuance).
   - Organizer broadcast to all confirmed event attendees.
   - Admin system-wide announcements.
7. **Feedback & Ratings**:
   - 1–5 star ratings and written reviews restricted to registered/attended students.
   - Aggregated rating distribution and breakdown per event.
8. **Certificate Management**:
   - Unique verification codes (e.g. `CERT-2026-EV1-7X9B2K`).
   - Single and batch issuance for attendees.
   - **Public certificate verification API** for recruiters and verifiers.
9. **Analytics & Dashboards**:
   - **Admin Dashboard**: Summary KPIs, event status breakdown, overall attendance rate, top 5 popular events, department-wise stats, and monthly trends.
   - **Faculty Dashboard**: Organizer event counts, registered attendees, certificates generated, and average feedback ratings.

---

## 📁 Directory Structure

```text
c:\project\backend/
├── alembic/                          # Alembic database migration scripts
│   ├── versions/
│   │   └── 0001_initial_schema.py    # Initial full database migration
│   ├── env.py                        # Migration environment configuration
│   └── script.py.mako
├── alembic.ini                       # Alembic settings
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI application setup, CORS & routes
│   ├── database.py                   # SQLAlchemy engine, session & Base
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # Pydantic Settings & environment variables
│   │   ├── security.py               # Bcrypt password hashing & PyJWT tokens
│   │   ├── dependencies.py           # Authentication & RBAC role guards
│   │   └── exceptions.py             # Custom application exceptions
│   ├── models/                       # SQLAlchemy declarative models
│   │   ├── __init__.py
│   │   ├── enums.py                  # UserRole, EventStatus, AttendanceStatus...
│   │   ├── department.py             # Department model
│   │   ├── user.py                   # User model
│   │   ├── event.py                  # Event model
│   │   ├── registration.py           # EventRegistration model
│   │   ├── attendance.py             # Attendance model
│   │   ├── notification.py           # Notification model
│   │   ├── feedback.py               # EventFeedback model
│   │   └── certificate.py            # Certificate model
│   ├── schemas/                      # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── token.py
│   │   ├── user.py
│   │   ├── department.py
│   │   ├── event.py
│   │   ├── registration.py
│   │   ├── attendance.py
│   │   ├── notification.py
│   │   ├── feedback.py
│   │   ├── certificate.py
│   │   └── dashboard.py
│   ├── services/                     # Business logic service layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── department_service.py
│   │   ├── event_service.py
│   │   ├── registration_service.py
│   │   ├── attendance_service.py
│   │   ├── notification_service.py
│   │   ├── feedback_service.py
│   │   ├── certificate_service.py
│   │   └── dashboard_service.py
│   └── routers/                      # FastAPI endpoint controllers
│       ├── __init__.py
│       ├── auth.py                   # /api/v1/auth/*
│       ├── users.py                  # /api/v1/users/*
│       ├── departments.py            # /api/v1/departments/*
│       ├── events.py                 # /api/v1/events/*
│       ├── registrations.py          # /api/v1/registrations/*
│       ├── attendances.py            # /api/v1/attendances/*
│       ├── notifications.py          # /api/v1/notifications/*
│       ├── feedbacks.py              # /api/v1/feedbacks/*
│       ├── certificates.py           # /api/v1/certificates/*
│       └── dashboard.py              # /api/v1/dashboard/*
├── tests/                            # Automated test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures and mock DB
│   └── test_api.py                   # End-to-end API integration tests
├── .env.example                      # Environment variables template
├── .gitignore
├── requirements.txt                  # Python dependencies
├── seed_data.py                      # Database initialization script
└── README.md
```

---

## 🛠️ Quickstart & Setup

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.12)
- PostgreSQL Server 14+ (or cloud-hosted PostgreSQL e.g. Neon, Supabase, RDS)

### 2. Virtual Environment Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and adjust the configuration as needed:
```powershell
cp .env.example .env
```

Ensure your `DATABASE_URL` in `.env` is pointing to your PostgreSQL instance:
```env
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/college_events_db"
SECRET_KEY="your-secure-secret-key-at-least-32-characters"
```

### 4. Database Migrations
Run Alembic migrations to build the schema:
```powershell
alembic upgrade head
```

### 5. Seed Initial Data (Optional)
Run the seed script to populate sample departments, admin, faculty, students, events, registrations, attendances, feedbacks, and certificates:
```powershell
python seed_data.py
```

**Default Demo Credentials:**
| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@college.edu` | `AdminPassword123!` |
| **Faculty (CSE)** | `prof.sharma@college.edu` | `FacultyPass123!` |
| **Faculty (ECE)** | `dr.anita@college.edu` | `FacultyPass123!` |
| **Student** | `rahul.verma@student.college.edu` | `StudentPass123!` |

### 6. Run the FastAPI Server
```powershell
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc UI: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated Tests
The project includes a complete `pytest` test suite configured with an in-memory SQLite isolation layer:
```powershell
pytest -v
```

---

## 📑 API Endpoints Summary

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/login`: Authenticate and obtain JWT token.
- `POST /api/v1/auth/register`: Student self-registration.
- `GET /api/v1/auth/me`: Get current logged-in user profile.
- `PUT /api/v1/auth/me`: Update logged-in user profile.
- `POST /api/v1/auth/change-password`: Change own password.

### User Management (`/api/v1/users`) [Admin]
- `GET /api/v1/users`: List users (filtered by role, department, active status, search).
- `POST /api/v1/users`: Create a new user (Admin, Faculty, or Student).
- `GET /api/v1/users/{id}`: Get user details.
- `PUT /api/v1/users/{id}`: Update user attributes and status.
- `DELETE /api/v1/users/{id}`: Remove user.
- `POST /api/v1/users/{id}/reset-password`: Reset a user's password.

### Department Management (`/api/v1/departments`)
- `GET /api/v1/departments`: List all departments.
- `GET /api/v1/departments/with-stats`: List departments with student, faculty, and event counts [Faculty & Admin].
- `GET /api/v1/departments/{id}`: Get department details.
- `POST /api/v1/departments`: Create department [Admin].
- `PUT /api/v1/departments/{id}`: Update department [Admin].
- `DELETE /api/v1/departments/{id}`: Delete department [Admin].

### College Events (`/api/v1/events`)
- `GET /api/v1/events`: List events (filtered by status, department, type, upcoming only, search).
- `POST /api/v1/events`: Create event [Faculty & Admin].
- `GET /api/v1/events/{id}`: Get event details with seat counts and ratings.
- `PUT /api/v1/events/{id}`: Update event details [Organizer & Admin].
- `PATCH /api/v1/events/{id}/status`: Update event status [Organizer & Admin].
- `DELETE /api/v1/events/{id}`: Delete event [Organizer & Admin].

### Registrations (`/api/v1/registrations`)
- `POST /api/v1/registrations`: Register for an event [Student].
- `POST /api/v1/registrations/{event_id}/cancel`: Cancel registration [Student].
- `GET /api/v1/registrations/my-registrations`: List my registered events [Student].
- `GET /api/v1/registrations/event/{event_id}`: List all registrations for an event [Faculty & Admin].

### Attendance (`/api/v1/attendances`)
- `POST /api/v1/attendances/event/{event_id}/mark`: Mark single student attendance [Faculty & Admin].
- `POST /api/v1/attendances/bulk`: Bulk mark attendance for an event [Faculty & Admin].
- `POST /api/v1/attendances/check-in`: Student self check-in / QR validation [Student].
- `GET /api/v1/attendances/event/{event_id}/summary`: Complete event attendance report & rate [Faculty & Admin].
- `GET /api/v1/attendances/my-history`: Student attendance history [Student].

### Notifications (`/api/v1/notifications`)
- `GET /api/v1/notifications`: List user notifications (unread filter & pagination).
- `GET /api/v1/notifications/unread-count`: Get unread count badge.
- `POST /api/v1/notifications/{id}/read`: Mark notification as read.
- `POST /api/v1/notifications/read-all`: Mark all notifications as read.
- `POST /api/v1/notifications/event/{event_id}/broadcast`: Broadcast message to event attendees [Faculty & Admin].
- `POST /api/v1/notifications/system-broadcast`: System-wide announcement [Admin].

### Feedback & Ratings (`/api/v1/feedbacks`)
- `POST /api/v1/feedbacks`: Submit 1–5 star rating and comments for an event [Student].
- `GET /api/v1/feedbacks/event/{event_id}`: Get rating distribution and reviews for an event.
- `GET /api/v1/feedbacks/my-feedbacks`: List my submitted feedbacks [Student].

### Certificate Management (`/api/v1/certificates`)
- `POST /api/v1/certificates/issue`: Issue certificate to a student [Faculty & Admin].
- `POST /api/v1/certificates/bulk-issue`: Bulk issue certificates to present attendees [Faculty & Admin].
- `GET /api/v1/certificates/verify/{code}`: **Public certificate verification endpoint**.
- `GET /api/v1/certificates/my-certificates`: Get my issued certificates [Student].
- `GET /api/v1/certificates/event/{event_id}`: List all event certificates [Faculty & Admin].
- `POST /api/v1/certificates/{id}/revoke`: Revoke an issued certificate [Organizer & Admin].

### Analytics & Dashboards (`/api/v1/dashboard`)
- `GET /api/v1/dashboard/admin`: Comprehensive Admin analytics (KPIs, status distributions, popular events, department metrics, monthly trends) [Admin].
- `GET /api/v1/dashboard/faculty`: Faculty metrics (organized events, student turnouts, certificates, ratings) [Faculty & Admin].
