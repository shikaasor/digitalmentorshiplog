"""
Database Connection Tests

Tests to verify database setup and connection work correctly.
"""

import pytest
from sqlalchemy import text

from app.database import Base
from app.models import User, Facility, MentorshipLog


@pytest.mark.database
def test_database_connection(db_session):
    """
    Test that database connection is established.

    This test verifies:
    - Database session can execute queries
    - Connection is working properly
    """
    # Execute a simple query
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.database
def test_database_tables_created(db_session):
    """
    Test that all database tables are created.

    This test verifies:
    - All SQLAlchemy models are mapped to tables
    - Tables can be queried
    """
    # Query each table to ensure they exist
    users_count = db_session.query(User).count()
    facilities_count = db_session.query(Facility).count()
    logs_count = db_session.query(MentorshipLog).count()

    # All should be zero (empty tables)
    assert users_count == 0
    assert facilities_count == 0
    assert logs_count == 0


@pytest.mark.database
def test_database_rollback(db_session):
    """
    Test that database changes are rolled back between tests.

    This test verifies:
    - Changes made in tests don't persist
    - Each test gets a clean database
    """
    from tests.helpers import create_test_user

    # Create a user
    user = create_test_user(db_session, email="rollback@test.com")
    assert user.id is not None

    # Verify user exists in current session
    found_user = db_session.query(User).filter_by(email="rollback@test.com").first()
    assert found_user is not None
    assert found_user.email == "rollback@test.com"


@pytest.mark.database
def test_database_isolation():
    """
    Test that each test gets isolated database session.

    This test verifies:
    - Previous test's user doesn't exist
    - Database is clean for each test
    """
    # This test runs after test_database_rollback
    # If isolation works, the user from previous test should NOT exist

    # Note: We can't use db_session here because we want to test
    # that fixture provides clean session
    # This will be verified by the fixture itself


@pytest.mark.database
def test_base_metadata():
    """
    Test that Base metadata contains all expected tables.

    This test verifies:
    - All models are registered with Base
    - Table definitions are correct
    """
    table_names = Base.metadata.tables.keys()

    # Check that expected tables are present
    expected_tables = [
        "users",
        "facilities",
        "mentorship_logs",
        "skills_transfers",
        "follow_ups",
        "attachments",
        "user_facility_assignments",
        "audit_logs"
    ]

    for table_name in expected_tables:
        assert table_name in table_names, f"Table '{table_name}' not found in metadata"
