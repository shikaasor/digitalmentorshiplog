"""
Comprehensive tests for Reports API

Tests for basic operational reports providing visibility into mentorship operations.
Focus on summary statistics, activity tracking, and follow-up monitoring.
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.models import User, UserRole, Facility, MentorshipLog, FollowUp, FollowUpStatus, LogStatus


def create_test_user(db_session, email="test@example.com", role=UserRole.mentor, name="Test User"):
    """Helper to create a test user"""
    from app.utils.security import hash_password
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        name=name,
        role=role,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_facility(db_session, name="Test Facility", code="FAC001", state="Kano", lga="Kano Municipal"):
    """Helper to create a test facility"""
    facility = Facility(
        name=name,
        code=code,
        state=state,
        lga=lga
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


def create_test_log(db_session, mentor, facility, visit_date=None, status=LogStatus.draft):
    """Helper to create a test mentorship log"""
    if visit_date is None:
        visit_date = date.today()

    log = MentorshipLog(
        facility_id=facility.id,
        mentor_id=mentor.id,
        visit_date=visit_date,
        status=status
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


def create_test_follow_up(db_session, mentorship_log, status=FollowUpStatus.pending, target_date=None, **kwargs):
    """Helper to create a test follow-up"""
    follow_up_data = {
        "mentorship_log_id": mentorship_log.id,
        "action_item": "Test action item",
        "status": status
    }
    if target_date:
        follow_up_data["target_date"] = target_date
    follow_up_data.update(kwargs)

    follow_up = FollowUp(**follow_up_data)
    db_session.add(follow_up)
    db_session.commit()
    db_session.refresh(follow_up)
    return follow_up


def get_auth_headers(token):
    """Helper to get authorization headers"""
    return {"Authorization": f"Bearer {token}"}


def assert_success(response, expected_status=200):
    """Assert response is successful and return JSON data"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    return response.json()


def assert_error(response, expected_status):
    """Assert response is an error with expected status"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    return response.json()


@pytest.mark.integration
class TestSummaryReport:
    """Tests for overall summary statistics"""

    def test_admin_can_get_summary(self, client, db_session):
        """Admin can get summary report"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        # Create sample data
        create_test_log(db_session, mentor, facility, status=LogStatus.draft)
        create_test_log(db_session, mentor, facility, status=LogStatus.submitted)
        create_test_log(db_session, mentor, facility, status=LogStatus.approved)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/summary", headers=headers)
        data = assert_success(response)

        assert "total_logs" in data
        assert "logs_by_status" in data
        assert "total_facilities" in data
        assert "total_mentors" in data
        assert data["total_logs"] >= 3

    def test_supervisor_can_get_summary(self, client, db_session):
        """Supervisor can get summary report"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/summary", headers=headers)
        data = assert_success(response)

        assert "total_logs" in data
        assert "logs_by_status" in data

    def test_mentor_cannot_get_summary(self, client, db_session):
        """Mentor cannot get summary report"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/summary", headers=headers)
        assert_error(response, 403)

    def test_summary_includes_follow_ups(self, client, db_session):
        """Summary includes follow-up statistics"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        # Create follow-ups
        create_test_follow_up(db_session, log, status=FollowUpStatus.pending)
        create_test_follow_up(db_session, log, status=FollowUpStatus.in_progress)
        create_test_follow_up(db_session, log, status=FollowUpStatus.completed)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/summary", headers=headers)
        data = assert_success(response)

        assert "total_follow_ups" in data
        assert "follow_ups_by_status" in data
        assert data["total_follow_ups"] >= 3


@pytest.mark.integration
class TestMentorshipLogsReport:
    """Tests for mentorship logs report"""

    def test_admin_can_get_logs_report(self, client, db_session):
        """Admin can get mentorship logs report"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        create_test_log(db_session, mentor, facility, visit_date=date.today() - timedelta(days=5))
        create_test_log(db_session, mentor, facility, visit_date=date.today())

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/mentorship-logs", headers=headers)
        data = assert_success(response)

        assert "total_count" in data
        assert "logs_by_mentor" in data
        assert "logs_by_facility" in data
        assert "logs_by_state" in data

    def test_filter_logs_by_date_range(self, client, db_session):
        """Can filter logs report by date range"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        # Create logs across different dates
        create_test_log(db_session, mentor, facility, visit_date=date(2025, 10, 1))
        create_test_log(db_session, mentor, facility, visit_date=date(2025, 10, 15))
        create_test_log(db_session, mentor, facility, visit_date=date(2025, 10, 30))

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        # Filter for October 1-20
        response = client.get(
            "/api/reports/mentorship-logs?start_date=2025-10-01&end_date=2025-10-20",
            headers=headers
        )
        data = assert_success(response)

        # Should only include logs from Oct 1-20
        assert data["total_count"] == 2

    def test_filter_logs_by_mentor(self, client, db_session):
        """Can filter logs report by mentor"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor, name="Mentor 1")
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)

        create_test_log(db_session, mentor1, facility)
        create_test_log(db_session, mentor1, facility)
        create_test_log(db_session, mentor2, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/reports/mentorship-logs?mentor_id={mentor1.id}", headers=headers)
        data = assert_success(response)

        assert data["total_count"] == 2

    def test_filter_logs_by_facility(self, client, db_session):
        """Can filter logs report by facility"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility1 = create_test_facility(db_session, code="FAC001", name="Facility 1")
        facility2 = create_test_facility(db_session, code="FAC002", name="Facility 2")

        create_test_log(db_session, mentor, facility1)
        create_test_log(db_session, mentor, facility1)
        create_test_log(db_session, mentor, facility2)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/reports/mentorship-logs?facility_id={facility1.id}", headers=headers)
        data = assert_success(response)

        assert data["total_count"] == 2

    def test_filter_logs_by_status(self, client, db_session):
        """Can filter logs report by status"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        create_test_log(db_session, mentor, facility, status=LogStatus.draft)
        create_test_log(db_session, mentor, facility, status=LogStatus.approved)
        create_test_log(db_session, mentor, facility, status=LogStatus.approved)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/mentorship-logs?status=approved", headers=headers)
        data = assert_success(response)

        assert data["total_count"] == 2

    def test_mentor_cannot_access_logs_report(self, client, db_session):
        """Mentor cannot access logs report"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/mentorship-logs", headers=headers)
        assert_error(response, 403)


@pytest.mark.integration
class TestFollowUpsReport:
    """Tests for follow-ups report"""

    def test_admin_can_get_follow_ups_report(self, client, db_session):
        """Admin can get follow-ups report"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        create_test_follow_up(db_session, log, status=FollowUpStatus.pending)
        create_test_follow_up(db_session, log, status=FollowUpStatus.completed)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/follow-ups", headers=headers)
        data = assert_success(response)

        assert "total_count" in data
        assert "by_status" in data
        assert "pending_count" in data
        assert "overdue_count" in data

    def test_report_shows_overdue_follow_ups(self, client, db_session):
        """Report identifies overdue follow-ups"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        # Create overdue follow-up
        create_test_follow_up(
            db_session, log,
            status=FollowUpStatus.pending,
            target_date=date.today() - timedelta(days=5)
        )
        # Create upcoming follow-up
        create_test_follow_up(
            db_session, log,
            status=FollowUpStatus.pending,
            target_date=date.today() + timedelta(days=5)
        )

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/follow-ups", headers=headers)
        data = assert_success(response)

        assert data["overdue_count"] >= 1

    def test_filter_follow_ups_by_status(self, client, db_session):
        """Can filter follow-ups report by status"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        create_test_follow_up(db_session, log, status=FollowUpStatus.pending)
        create_test_follow_up(db_session, log, status=FollowUpStatus.pending)
        create_test_follow_up(db_session, log, status=FollowUpStatus.completed)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/follow-ups?status=pending", headers=headers)
        data = assert_success(response)

        assert data["total_count"] == 2

    def test_filter_follow_ups_by_priority(self, client, db_session):
        """Can filter follow-ups report by priority"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        create_test_follow_up(db_session, log, priority="High")
        create_test_follow_up(db_session, log, priority="High")
        create_test_follow_up(db_session, log, priority="Low")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/follow-ups?priority=High", headers=headers)
        data = assert_success(response)

        assert data["total_count"] == 2

    def test_supervisor_can_access_follow_ups_report(self, client, db_session):
        """Supervisor can access follow-ups report"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/follow-ups", headers=headers)
        data = assert_success(response)

        assert "total_count" in data


@pytest.mark.integration
class TestFacilityCoverageReport:
    """Tests for facility coverage report"""

    def test_admin_can_get_facility_coverage(self, client, db_session):
        """Admin can get facility coverage report"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility1 = create_test_facility(db_session, code="FAC001", name="Facility 1")
        facility2 = create_test_facility(db_session, code="FAC002", name="Facility 2")

        create_test_log(db_session, mentor, facility1, visit_date=date.today() - timedelta(days=10))
        create_test_log(db_session, mentor, facility1, visit_date=date.today())

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/facility-coverage", headers=headers)
        data = assert_success(response)

        assert "total_facilities" in data
        assert "visited_facilities" in data
        assert "unvisited_facilities" in data
        assert "facilities" in data
        assert isinstance(data["facilities"], list)

    def test_coverage_shows_last_visit_date(self, client, db_session):
        """Coverage report shows last visit date for each facility"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        last_visit = date.today() - timedelta(days=3)
        create_test_log(db_session, mentor, facility, visit_date=date.today() - timedelta(days=10))
        create_test_log(db_session, mentor, facility, visit_date=last_visit)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/facility-coverage", headers=headers)
        data = assert_success(response)

        # Find our facility in the results
        facility_data = next((f for f in data["facilities"] if f["facility_id"] == str(facility.id)), None)
        assert facility_data is not None
        assert facility_data["last_visit_date"] == str(last_visit)
        assert facility_data["visit_count"] == 2

    def test_coverage_identifies_unvisited_facilities(self, client, db_session):
        """Coverage report identifies facilities with no visits"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility1 = create_test_facility(db_session, code="FAC001", name="Visited Facility")
        facility2 = create_test_facility(db_session, code="FAC002", name="Unvisited Facility")

        create_test_log(db_session, mentor, facility1)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/facility-coverage", headers=headers)
        data = assert_success(response)

        assert data["visited_facilities"] >= 1
        assert data["unvisited_facilities"] >= 1

    def test_filter_coverage_by_state(self, client, db_session):
        """Can filter facility coverage by state"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility1 = create_test_facility(db_session, code="FAC001", state="Kano")
        facility2 = create_test_facility(db_session, code="FAC002", state="Jigawa")

        create_test_log(db_session, mentor, facility1)
        create_test_log(db_session, mentor, facility2)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/facility-coverage?state=Kano", headers=headers)
        data = assert_success(response)

        # Should only include Kano facilities
        assert all(f["state"] == "Kano" for f in data["facilities"] if f["visit_count"] > 0)

    def test_supervisor_can_access_facility_coverage(self, client, db_session):
        """Supervisor can access facility coverage report"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/reports/facility-coverage", headers=headers)
        data = assert_success(response)

        assert "total_facilities" in data
