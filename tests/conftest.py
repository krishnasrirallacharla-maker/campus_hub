import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

# Test in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    user = User(
        email="test_admin@college.edu",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Administrator",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def faculty_user(db):
    user = User(
        email="test_faculty@college.edu",
        hashed_password=get_password_hash("FacultyPass123!"),
        full_name="Prof. Test Faculty",
        role=UserRole.FACULTY,
        phone="+91 9876543210",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def student_user(db):
    user = User(
        email="test_student@student.college.edu",
        hashed_password=get_password_hash("StudentPass123!"),
        full_name="Test Student",
        role=UserRole.STUDENT,
        roll_number="TEST2026-001",
        phone="+91 9123456780",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(subject=admin_user.id, role=admin_user.role.value, email=admin_user.email)


@pytest.fixture
def faculty_token(faculty_user):
    return create_access_token(subject=faculty_user.id, role=faculty_user.role.value, email=faculty_user.email)


@pytest.fixture
def student_token(student_user):
    return create_access_token(subject=student_user.id, role=student_user.role.value, email=student_user.email)
