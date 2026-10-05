import pytest
from datetime import datetime, timedelta, timezone
from app.models.enums import AttendanceStatus, EventStatus, RegistrationStatus, UserRole
from app.models.department import Department
from app.models.event import Event
from app.models.registration import EventRegistration


def test_root_and_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_and_profile(client, admin_user, student_user):
    # Test Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test_admin@college.edu", "password": "AdminPass123!"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    token = data["access_token"]

    # Test /auth/me
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test_admin@college.edu"

    # Test Student Register
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new_student@college.edu",
            "password": "Password123!",
            "full_name": "New Student",
            "roll_number": "ST2026-999",
        },
    )
    assert reg_resp.status_code == 201
    assert reg_resp.json()["email"] == "new_student@college.edu"


def test_departments_crud(client, admin_token, faculty_token, student_token):
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_student = {"Authorization": f"Bearer {student_token}"}

    # Student cannot create department
    res = client.post(
        "/api/v1/departments",
        json={"name": "Civil Engineering", "code": "CIVIL"},
        headers=headers_student,
    )
    assert res.status_code == 403

    # Admin creates department
    res = client.post(
        "/api/v1/departments",
        json={
            "name": "Information Technology",
            "code": "IT",
            "description": "Dept of IT",
            "head_of_department": "Dr. Tech",
        },
        headers=headers_admin,
    )
    assert res.status_code == 201
    dept_id = res.json()["id"]

    # List departments
    list_res = client.get("/api/v1/departments")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Get department with stats (Faculty/Admin)
    stats_res = client.get(
        "/api/v1/departments/with-stats",
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    assert stats_res.status_code == 200


def test_events_and_registration_workflow(client, db, admin_token, faculty_token, student_token, student_user, faculty_user):
    headers_faculty = {"Authorization": f"Bearer {faculty_token}"}
    headers_student = {"Authorization": f"Bearer {student_token}"}

    # 1. Create Department
    dept = Department(name="Robotics and AI", code="RAI")
    db.add(dept)
    db.commit()
    db.refresh(dept)

    # 2. Faculty creates event
    now = datetime.now(timezone.utc)
    event_payload = {
        "title": "Autonomous Robotics Symposium",
        "description": "Annual robotics exhibition and challenge.",
        "event_type": "Symposium",
        "venue": "Auditorium 2",
        "start_time": (now + timedelta(days=5)).isoformat(),
        "end_time": (now + timedelta(days=6)).isoformat(),
        "registration_deadline": (now + timedelta(days=3)).isoformat(),
        "capacity": 2,  # small capacity for capacity test
        "department_id": dept.id,
        "status": "published",
        "is_certificate_provided": True,
    }

    create_ev_res = client.post("/api/v1/events", json=event_payload, headers=headers_faculty)
    assert create_ev_res.status_code == 201
    event_id = create_ev_res.json()["id"]

    # 3. Student registers for event
    reg_res = client.post(
        "/api/v1/registrations",
        json={"event_id": event_id},
        headers=headers_student,
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["status"] == "confirmed"

    # 4. Student views my-registrations
    my_regs = client.get("/api/v1/registrations/my-registrations", headers=headers_student)
    assert my_regs.status_code == 200
    assert len(my_regs.json()) == 1

    # 5. Check duplicate registration fails
    dup_reg = client.post(
        "/api/v1/registrations",
        json={"event_id": event_id},
        headers=headers_student,
    )
    assert dup_reg.status_code == 400

    # 6. Faculty marks attendance
    att_res = client.post(
        f"/api/v1/attendances/event/{event_id}/mark",
        json={"student_id": student_user.id, "status": "present", "notes": "Attended all sessions"},
        headers=headers_faculty,
    )
    assert att_res.status_code == 200
    assert att_res.json()["status"] == "present"

    # 7. Student submits feedback
    fb_res = client.post(
        "/api/v1/feedbacks",
        json={"event_id": event_id, "rating": 5, "comments": "Outstanding robotics demos!"},
        headers=headers_student,
    )
    assert fb_res.status_code == 201
    assert fb_res.json()["rating"] == 5

    # 8. Faculty issues certificate
    cert_res = client.post(
        "/api/v1/certificates/issue",
        json={"event_id": event_id, "student_id": student_user.id},
        headers=headers_faculty,
    )
    assert cert_res.status_code == 201
    cert_code = cert_res.json()["certificate_code"]

    # 9. Public verifies certificate
    verify_res = client.get(f"/api/v1/certificates/verify/{cert_code}")
    assert verify_res.status_code == 200
    assert verify_res.json()["is_valid"] is True
    assert verify_res.json()["student_name"] == "Test Student"

    # 10. Check Admin and Faculty Dashboards
    admin_dash = client.get("/api/v1/dashboard/admin", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_dash.status_code == 200
    assert admin_dash.json()["total_events"] >= 1
    assert admin_dash.json()["total_certificates_issued"] >= 1

    faculty_dash = client.get("/api/v1/dashboard/faculty", headers=headers_faculty)
    assert faculty_dash.status_code == 200
    assert faculty_dash.json()["total_organized_events"] >= 1
