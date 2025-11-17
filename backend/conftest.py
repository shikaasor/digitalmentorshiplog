"""
Pytest Configuration and Shared Fixtures

This file contains fixtures that are available to all tests.
Fixtures provide reusable test data and setup/teardown logic.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, Facility, MentorshipLog, UserRole
from app.utils.security import hash_password, create_access_token


# Test Database Configuration
# Using SQLite in-memory database for fast tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test database engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Use static pool for in-memory database
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a clean database session for each test.

    This fixture:
    - Creates all database tables
    - Provides a database session for the test
    - Rolls back changes after the test
    - Drops all tables after the test

    Scope: function (runs for each test)
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create a new session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        # Rollback any changes and close session
        session.rollback()
        session.close()

        # Drop all tables to ensure clean state
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a FastAPI test client with test database.

    This fixture:
    - Overrides the get_db dependency to use test database
    - Provides a TestClient for making API requests

    Usage:
        def test_something(client):
            response = client.get("/api/endpoint")
            assert response.status_code == 200
    """
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Provide sample user data for tests.

    Returns:
        dict: User data dictionary
    """
    return {
        "email": "test.mentor@example.com",
        "name": "Test Mentor",
        "designation": "Senior Mentor",
        "region_state": "Test State",
        "role": UserRole.mentor,
        "password": "password123"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """
    Create a test user in the database.

    Returns:
        User: Created user object
    """
    user = User(
        email=test_user_data["email"],
        name=test_user_data["name"],
        designation=test_user_data["designation"],
        region_state=test_user_data["region_state"],
        role=test_user_data["role"],
        password_hash=hash_password(test_user_data["password"]),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_supervisor_data():
    """
    Provide sample supervisor data for tests.
    """
    return {
        "email": "test.supervisor@example.com",
        "name": "Test Supervisor",
        "designation": "Program Supervisor",
        "region_state": "Test State",
        "role": UserRole.supervisor,
        "password": "supervisorPassword123"
    }


@pytest.fixture
def test_supervisor(db_session, test_supervisor_data):
    """
    Create a test supervisor in the database.
    """
    supervisor = User(
        email=test_supervisor_data["email"],
        name=test_supervisor_data["name"],
        designation=test_supervisor_data["designation"],
        region_state=test_supervisor_data["region_state"],
        role=test_supervisor_data["role"],
        password_hash=hash_password(test_supervisor_data["password"]),
        is_active=True
    )
    db_session.add(supervisor)
    db_session.commit()
    db_session.refresh(supervisor)
    return supervisor


@pytest.fixture
def test_admin_data():
    """
    Provide sample admin data for tests.
    """
    return {
        "email": "test.admin@example.com",
        "name": "Test Admin",
        "designation": "System Administrator",
        "region_state": "Test State",
        "role": UserRole.admin,
        "password": "adminPassword123"
    }


@pytest.fixture
def test_admin(db_session, test_admin_data):
    """
    Create a test admin in the database.
    """
    admin = User(
        email=test_admin_data["email"],
        name=test_admin_data["name"],
        designation=test_admin_data["designation"],
        region_state=test_admin_data["region_state"],
        role=test_admin_data["role"],
        password_hash=hash_password(test_admin_data["password"]),
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_facility_data():
    """
    Provide sample facility data for tests.
    """
    return {
        "name": "Test Health Clinic",
        "code": "TEST-001",
        "location": "Test Location",
        "state": "Test State",
        "lga": "Test LGA",
        "facility_type": "Primary Care",
        "contact_person": "Dr. Test Person",
        "contact_email": "contact@testclinic.com",
        "contact_phone": "+234-800-0000"
    }


@pytest.fixture
def test_facility(db_session, test_facility_data):
    """
    Create a test facility in the database.
    """
    facility = Facility(**test_facility_data)
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


@pytest.fixture
def auth_token(test_user):
    """
    Generate a JWT authentication token for test user.

    Usage:
        def test_protected_endpoint(client, auth_token):
            response = client.get(
                "/api/endpoint",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
    """
    token = create_access_token(data={"sub": str(test_user.id)})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """
    Generate authentication headers for test requests.

    Returns:
        dict: Headers with Bearer token
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def supervisor_token(test_supervisor):
    """
    Generate a JWT authentication token for test supervisor.
    """
    token = create_access_token(data={"sub": str(test_supervisor.id)})
    return token


@pytest.fixture
def supervisor_headers(supervisor_token):
    """
    Generate authentication headers for supervisor requests.
    """
    return {"Authorization": f"Bearer {supervisor_token}"}


@pytest.fixture
def admin_token(test_admin):
    """
    Generate a JWT authentication token for test admin.
    """
    token = create_access_token(data={"sub": str(test_admin.id)})
    return token


@pytest.fixture
def admin_headers(admin_token):
    """
    Generate authentication headers for admin requests.
    """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_mentorship_log_data(test_facility):
    """
    Provide sample mentorship log data for tests (ACE2 PDF form structure).
    """
    return {
        "facility_id": str(test_facility.id),
        "visit_date": "2025-11-20",
        # Header fields
        "interaction_type": "On-site",
        "duration_hours": 3,
        "duration_minutes": 30,
        "mentees_present": ["Dr. John Doe", "Nurse Jane Smith"],
        # Section 1: Activities Conducted
        "activities_conducted": ["Direct clinical service", "Mentoring/Coaching"],
        # Section 2: Thematic Areas Covered
        "thematic_areas": ["General HIV care and treatment", "TB/HIV services"],
        # Section 3: Observations
        "strengths_observed": "Good patient record management",
        "gaps_identified": "Need for additional training on ART adherence",
        "root_causes": "Limited staff capacity",
        # Section 6: Challenges & Solutions
        "challenges_encountered": "Staff shortage during visit",
        "solutions_proposed": "Recommended additional training",
        "support_needed": "Training materials for ART adherence"
    }


# Pytest hooks for better test output
def pytest_configure(config):
    """
    Configure pytest with custom settings.
    """
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    """
    for item in items:
        # Add 'unit' marker to tests without other markers
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unit)
