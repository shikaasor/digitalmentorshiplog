"""
Test Helper Functions

Utility functions to make writing tests easier and reduce code duplication.
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
import uuid

from app.models import User, Facility, MentorshipLog, UserRole, LogStatus
from app.utils.security import hash_password


def create_test_user(
    db_session,
    email: str = "user@test.com",
    name: str = "Test User",
    role: UserRole = UserRole.mentor,
    password: str = "password123",
    **kwargs
) -> User:
    """
    Create a test user with default or custom values.

    Args:
        db_session: Database session
        email: User email
        name: User name
        role: User role
        password: User password (will be hashed)
        **kwargs: Additional user fields

    Returns:
        User: Created user object
    """
    user = User(
        email=email,
        name=name,
        role=role,
        password_hash=hash_password(password),
        is_active=kwargs.get("is_active", True),
        designation=kwargs.get("designation"),
        region_state=kwargs.get("region_state"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_facility(
    db_session,
    name: str = "Test Facility",
    code: str = None,
    **kwargs
) -> Facility:
    """
    Create a test facility with default or custom values.

    Args:
        db_session: Database session
        name: Facility name
        code: Facility code (auto-generated if not provided)
        **kwargs: Additional facility fields

    Returns:
        Facility: Created facility object
    """
    if code is None:
        code = f"TEST-{str(uuid.uuid4())[:8]}"

    facility = Facility(
        name=name,
        code=code,
        location=kwargs.get("location", "Test Location"),
        state=kwargs.get("state", "Kano"),
        lga=kwargs.get("lga", "Test LGA"),
        facility_type=kwargs.get("facility_type", "Primary Care"),
        contact_person=kwargs.get("contact_person"),
        contact_email=kwargs.get("contact_email"),
        contact_phone=kwargs.get("contact_phone"),
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


def create_test_mentorship_log(
    db_session,
    mentor: User = None,
    facility: Facility = None,
    visit_date: Optional[date] = None,
    status: LogStatus = LogStatus.draft,
    **kwargs
) -> MentorshipLog:
    """
    Create a test mentorship log with default or custom values.
    Updated to match ACE2 PDF form structure.

    Args:
        db_session: Database session
        mentor: Mentor user (created if not provided)
        facility: Facility (created if not provided)
        visit_date: Visit date (defaults to tomorrow)
        status: Log status
        **kwargs: Additional log fields (matching new PDF structure)

    Returns:
        MentorshipLog: Created log object
    """
    # Create mentor and facility if not provided
    if mentor is None:
        mentor = create_test_user(db_session, email=f"mentor-{uuid.uuid4()}@test.com")
    if facility is None:
        facility = create_test_facility(db_session)

    if visit_date is None:
        visit_date = date.today() + timedelta(days=1)

    log = MentorshipLog(
        mentor_id=mentor.id,
        facility_id=facility.id,
        visit_date=visit_date,
        status=status,
        # Header fields
        interaction_type=kwargs.get("interaction_type", "On-site"),
        duration_hours=kwargs.get("duration_hours", 2),
        duration_minutes=kwargs.get("duration_minutes", 30),
        mentees_present=kwargs.get("mentees_present", []),
        # Section 1: Activities Conducted
        activities_conducted=kwargs.get("activities_conducted", ["Direct clinical service"]),
        activities_other_specify=kwargs.get("activities_other_specify"),
        # Section 2: Thematic Areas Covered
        thematic_areas=kwargs.get("thematic_areas", ["General HIV care and treatment"]),
        thematic_areas_other_specify=kwargs.get("thematic_areas_other_specify"),
        # Section 3: Observations
        strengths_observed=kwargs.get("strengths_observed"),
        gaps_identified=kwargs.get("gaps_identified"),
        root_causes=kwargs.get("root_causes"),
        # Section 6: Challenges & Solutions
        challenges_encountered=kwargs.get("challenges_encountered"),
        solutions_proposed=kwargs.get("solutions_proposed"),
        support_needed=kwargs.get("support_needed"),
        # Section 7: Success Stories
        success_stories=kwargs.get("success_stories"),
        # Section 8: Attachments
        attachment_types=kwargs.get("attachment_types", []),
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


def assert_dict_contains(actual: Dict[str, Any], expected: Dict[str, Any]) -> None:
    """
    Assert that actual dictionary contains all key-value pairs from expected.

    Useful for checking API responses without checking every field.

    Args:
        actual: The actual dictionary
        expected: Dictionary with expected key-value pairs

    Raises:
        AssertionError: If any expected key-value pair is missing or different
    """
    for key, expected_value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dictionary"
        assert actual[key] == expected_value, (
            f"Value mismatch for key '{key}': "
            f"expected {expected_value}, got {actual[key]}"
        )


def assert_validation_error(response, field: str) -> None:
    """
    Assert that response contains a validation error for the specified field.

    Args:
        response: FastAPI test response
        field: Field name that should have validation error

    Raises:
        AssertionError: If validation error not found for field
    """
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    errors = response.json().get("detail", [])

    # Check if any error is for the specified field
    field_errors = [
        error for error in errors
        if field in str(error.get("loc", []))
    ]

    assert field_errors, f"No validation error found for field '{field}'"


def assert_unauthorized(response) -> None:
    """
    Assert that response indicates unauthorized access (401).

    Args:
        response: FastAPI test response
    """
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def assert_forbidden(response) -> None:
    """
    Assert that response indicates forbidden access (403).

    Args:
        response: FastAPI test response
    """
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


def assert_not_found(response) -> None:
    """
    Assert that response indicates resource not found (404).

    Args:
        response: FastAPI test response
    """
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def assert_success(response, status_code: int = 200) -> Dict[str, Any]:
    """
    Assert that response is successful and return JSON data.

    Args:
        response: FastAPI test response
        status_code: Expected status code (default 200)

    Returns:
        Dict: Response JSON data

    Raises:
        AssertionError: If status code doesn't match
    """
    assert response.status_code == status_code, (
        f"Expected {status_code}, got {response.status_code}. "
        f"Response: {response.text}"
    )
    return response.json()


def get_auth_headers(token: str) -> Dict[str, str]:
    """
    Create authentication headers with Bearer token.

    Args:
        token: JWT token

    Returns:
        Dict: Headers dictionary with Authorization
    """
    return {"Authorization": f"Bearer {token}"}


def create_multiple_users(db_session, count: int = 5) -> list[User]:
    """
    Create multiple test users.

    Args:
        db_session: Database session
        count: Number of users to create

    Returns:
        list[User]: List of created users
    """
    users = []
    for i in range(count):
        user = create_test_user(
            db_session,
            email=f"user{i}@test.com",
            name=f"Test User {i}",
        )
        users.append(user)
    return users


def create_multiple_facilities(db_session, count: int = 5) -> list[Facility]:
    """
    Create multiple test facilities.

    Args:
        db_session: Database session
        count: Number of facilities to create

    Returns:
        list[Facility]: List of created facilities
    """
    facilities = []
    for i in range(count):
        facility = create_test_facility(
            db_session,
            name=f"Test Facility {i}",
            code=f"TEST-{i:03d}",
        )
        facilities.append(facility)
    return facilities


def strip_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove timestamp fields from dictionary for easier comparison.

    Args:
        data: Dictionary that may contain timestamp fields

    Returns:
        Dict: Dictionary without timestamp fields
    """
    timestamp_fields = [
        "created_at", "updated_at", "submitted_at",
        "approved_at", "completed_at"
    ]

    return {
        key: value
        for key, value in data.items()
        if key not in timestamp_fields
    }


def mock_jwt_token(user_id: str) -> str:
    """
    Create a mock JWT token for testing.

    Args:
        user_id: User ID to encode in token

    Returns:
        str: JWT token
    """
    from app.utils.security import create_access_token
    return create_access_token(data={"sub": user_id})
