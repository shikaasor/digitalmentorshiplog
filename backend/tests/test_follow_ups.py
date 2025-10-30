"""
Comprehensive tests for Follow-ups API

Tests for managing action items (follow-ups) from mentorship logs.
Follow-ups track action items from Section 5 of the ACE2 PDF form.
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


def create_test_facility(db_session, name="Test Facility", code="FAC001"):
    """Helper to create a test facility"""
    facility = Facility(
        name=name,
        code=code,
        state="Kano",
        lga="Kano Municipal"
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


def create_test_log(db_session, mentor, facility, visit_date=None):
    """Helper to create a test mentorship log"""
    if visit_date is None:
        visit_date = date.today()

    log = MentorshipLog(
        facility_id=facility.id,
        mentor_id=mentor.id,
        visit_date=visit_date,
        status=LogStatus.draft
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


def create_test_follow_up(db_session, mentorship_log, **kwargs):
    """Helper to create a test follow-up"""
    follow_up_data = {
        "mentorship_log_id": mentorship_log.id,
        "action_item": "Test action item",
        "priority": "High",
        "status": FollowUpStatus.pending
    }
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
class TestListFollowUps:
    """Tests for listing follow-ups"""

    def test_authenticated_user_can_list_follow_ups(self, client, db_session):
        """Any authenticated user can list follow-ups"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        create_test_follow_up(db_session, log, action_item="Follow up 1")
        create_test_follow_up(db_session, log, action_item="Follow up 2")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/follow-ups", headers=headers)
        data = assert_success(response)

        assert isinstance(data, list)
        assert len(data) >= 2

    def test_filter_by_status(self, client, db_session):
        """Filter follow-ups by status"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        create_test_follow_up(db_session, log, action_item="Pending item", status=FollowUpStatus.pending)
        create_test_follow_up(db_session, log, action_item="In progress item", status=FollowUpStatus.in_progress)
        create_test_follow_up(db_session, log, action_item="Completed item", status=FollowUpStatus.completed)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        # Filter by pending
        response = client.get("/api/follow-ups?status=pending", headers=headers)
        data = assert_success(response)
        assert all(item["status"] == "pending" for item in data)

    def test_filter_by_mentorship_log(self, client, db_session):
        """Filter follow-ups by mentorship log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log1 = create_test_log(db_session, mentor, facility)
        log2 = create_test_log(db_session, mentor, facility, visit_date=date.today() + timedelta(days=1))

        create_test_follow_up(db_session, log1, action_item="Log 1 item")
        create_test_follow_up(db_session, log2, action_item="Log 2 item")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/follow-ups?mentorship_log_id={log1.id}", headers=headers)
        data = assert_success(response)

        assert all(item["mentorship_log_id"] == str(log1.id) for item in data)
        assert len(data) >= 1

    def test_filter_by_assigned_user(self, client, db_session):
        """Filter follow-ups by assigned user"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assignee = create_test_user(db_session, email="assignee@test.com", role=UserRole.mentor, name="Assignee")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        create_test_follow_up(db_session, log, action_item="Assigned item", assigned_to=assignee.id)
        create_test_follow_up(db_session, log, action_item="Unassigned item")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/follow-ups?assigned_to={assignee.id}", headers=headers)
        data = assert_success(response)

        assert all(item["assigned_to"] == str(assignee.id) for item in data)

    def test_filter_by_priority(self, client, db_session):
        """Filter follow-ups by priority"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        create_test_follow_up(db_session, log, action_item="High priority", priority="High")
        create_test_follow_up(db_session, log, action_item="Medium priority", priority="Medium")
        create_test_follow_up(db_session, log, action_item="Low priority", priority="Low")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/follow-ups?priority=High", headers=headers)
        data = assert_success(response)

        assert all(item["priority"] == "High" for item in data)

    def test_pagination_works(self, client, db_session):
        """Pagination works correctly"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        # Create multiple follow-ups
        for i in range(15):
            create_test_follow_up(db_session, log, action_item=f"Action item {i}")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        # Get first page
        response = client.get("/api/follow-ups?skip=0&limit=10", headers=headers)
        data = assert_success(response)
        assert len(data) == 10

        # Get second page
        response = client.get("/api/follow-ups?skip=10&limit=10", headers=headers)
        data = assert_success(response)
        assert len(data) >= 5

    def test_unauthenticated_cannot_list(self, client, db_session):
        """Unauthenticated users cannot list follow-ups"""
        response = client.get("/api/follow-ups")
        assert_error(response, 403)


@pytest.mark.integration
class TestGetFollowUp:
    """Tests for getting a single follow-up"""

    def test_can_get_follow_up(self, client, db_session):
        """Authenticated user can get a follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Test action")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/follow-ups/{follow_up.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(follow_up.id)
        assert data["action_item"] == "Test action"
        assert data["status"] == "pending"

    def test_get_nonexistent_follow_up_returns_404(self, client, db_session):
        """Getting a nonexistent follow-up returns 404"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        fake_id = uuid4()
        response = client.get(f"/api/follow-ups/{fake_id}", headers=headers)
        assert_error(response, 404)

    def test_unauthenticated_cannot_get(self, client, db_session):
        """Unauthenticated users cannot get a follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        response = client.get(f"/api/follow-ups/{follow_up.id}")
        assert_error(response, 403)


@pytest.mark.integration
class TestCreateFollowUp:
    """Tests for creating follow-ups"""

    def test_mentor_can_create_follow_up_for_own_log(self, client, db_session):
        """Mentor can create follow-up for their own log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(log.id),
            "action_item": "New action item",
            "responsible_person": "John Doe",
            "target_date": str(date.today() + timedelta(days=7)),
            "priority": "High",
            "resources_needed": "Training materials"
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        data = assert_success(response, 201)

        assert data["action_item"] == "New action item"
        assert data["status"] == "pending"
        assert data["priority"] == "High"

    def test_admin_can_create_follow_up(self, client, db_session):
        """Admin can create follow-up for any log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(log.id),
            "action_item": "Admin action item"
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        data = assert_success(response, 201)

        assert data["action_item"] == "Admin action item"

    def test_supervisor_can_create_follow_up(self, client, db_session):
        """Supervisor can create follow-up for any log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(log.id),
            "action_item": "Supervisor action item"
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        data = assert_success(response, 201)

        assert data["action_item"] == "Supervisor action item"

    def test_mentor_cannot_create_follow_up_for_other_log(self, client, db_session):
        """Mentor cannot create follow-up for another mentor's log"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor2, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(log.id),
            "action_item": "Unauthorized action"
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        assert_error(response, 403)

    def test_create_with_assigned_user(self, client, db_session):
        """Can create follow-up with assigned user"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assignee = create_test_user(db_session, email="assignee@test.com", role=UserRole.mentor, name="Assignee")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(log.id),
            "action_item": "Assigned action",
            "assigned_to": str(assignee.id)
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        data = assert_success(response, 201)

        assert data["assigned_to"] == str(assignee.id)

    def test_create_with_invalid_log_id_returns_404(self, client, db_session):
        """Creating follow-up with invalid log ID returns 404"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        follow_up_data = {
            "mentorship_log_id": str(uuid4()),
            "action_item": "Invalid log action"
        }

        response = client.post("/api/follow-ups", json=follow_up_data, headers=headers)
        assert_error(response, 404)

    def test_unauthenticated_cannot_create(self, client, db_session):
        """Unauthenticated users cannot create follow-ups"""
        follow_up_data = {
            "mentorship_log_id": str(uuid4()),
            "action_item": "Test action"
        }

        response = client.post("/api/follow-ups", json=follow_up_data)
        assert_error(response, 403)


@pytest.mark.integration
class TestUpdateFollowUp:
    """Tests for updating follow-ups"""

    def test_mentor_can_update_own_log_follow_up(self, client, db_session):
        """Mentor can update follow-up for their own log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Original action")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {
            "action_item": "Updated action",
            "priority": "Medium"
        }

        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["action_item"] == "Updated action"
        assert data["priority"] == "Medium"

    def test_admin_can_update_any_follow_up(self, client, db_session):
        """Admin can update any follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Original action")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {"action_item": "Admin updated"}

        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["action_item"] == "Admin updated"

    def test_supervisor_can_update_any_follow_up(self, client, db_session):
        """Supervisor can update any follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Original action")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        update_data = {"action_item": "Supervisor updated"}

        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["action_item"] == "Supervisor updated"

    def test_assigned_user_can_update_status(self, client, db_session):
        """Assigned user can update status of their assigned follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assignee = create_test_user(db_session, email="assignee@test.com", role=UserRole.mentor, name="Assignee")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Assigned task", assigned_to=assignee.id)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(assignee.id)})
        headers = get_auth_headers(token)

        update_data = {"status": "in_progress"}

        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["status"] == "in_progress"

    def test_mentor_cannot_update_other_log_follow_up(self, client, db_session):
        """Mentor cannot update follow-up for another mentor's log"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor2, facility)
        follow_up = create_test_follow_up(db_session, log, action_item="Original action")

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        update_data = {"action_item": "Unauthorized update"}

        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data, headers=headers)
        assert_error(response, 403)

    def test_update_nonexistent_follow_up_returns_404(self, client, db_session):
        """Updating nonexistent follow-up returns 404"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        fake_id = uuid4()
        update_data = {"action_item": "Updated"}

        response = client.put(f"/api/follow-ups/{fake_id}", json=update_data, headers=headers)
        assert_error(response, 404)

    def test_unauthenticated_cannot_update(self, client, db_session):
        """Unauthenticated users cannot update follow-ups"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        update_data = {"action_item": "Updated"}
        response = client.put(f"/api/follow-ups/{follow_up.id}", json=update_data)
        assert_error(response, 403)


@pytest.mark.integration
class TestMarkFollowUpInProgress:
    """Tests for marking follow-up as in progress"""

    def test_mentor_can_mark_own_log_follow_up_in_progress(self, client, db_session):
        """Mentor can mark their own log's follow-up as in progress"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, status=FollowUpStatus.pending)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/in-progress", headers=headers)
        data = assert_success(response)

        assert data["status"] == "in_progress"

    def test_assigned_user_can_mark_in_progress(self, client, db_session):
        """Assigned user can mark their assigned follow-up as in progress"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assignee = create_test_user(db_session, email="assignee@test.com", role=UserRole.mentor, name="Assignee")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, assigned_to=assignee.id)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(assignee.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/in-progress", headers=headers)
        data = assert_success(response)

        assert data["status"] == "in_progress"

    def test_unauthorized_user_cannot_mark_in_progress(self, client, db_session):
        """Unauthorized user cannot mark follow-up as in progress"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor2, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/in-progress", headers=headers)
        assert_error(response, 403)


@pytest.mark.integration
class TestMarkFollowUpCompleted:
    """Tests for marking follow-up as completed"""

    def test_mentor_can_mark_own_log_follow_up_completed(self, client, db_session):
        """Mentor can mark their own log's follow-up as completed"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, status=FollowUpStatus.in_progress)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/complete", headers=headers)
        data = assert_success(response)

        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_assigned_user_can_mark_completed(self, client, db_session):
        """Assigned user can mark their assigned follow-up as completed"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assignee = create_test_user(db_session, email="assignee@test.com", role=UserRole.mentor, name="Assignee")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log, assigned_to=assignee.id, status=FollowUpStatus.in_progress)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(assignee.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/complete", headers=headers)
        data = assert_success(response)

        assert data["status"] == "completed"

    def test_unauthorized_user_cannot_mark_completed(self, client, db_session):
        """Unauthorized user cannot mark follow-up as completed"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor2, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/follow-ups/{follow_up.id}/complete", headers=headers)
        assert_error(response, 403)


@pytest.mark.integration
class TestDeleteFollowUp:
    """Tests for deleting follow-ups"""

    def test_mentor_can_delete_own_log_follow_up(self, client, db_session):
        """Mentor can delete follow-up from their own log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/follow-ups/{follow_up.id}", headers=headers)
        assert response.status_code == 204

    def test_admin_can_delete_any_follow_up(self, client, db_session):
        """Admin can delete any follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/follow-ups/{follow_up.id}", headers=headers)
        assert response.status_code == 204

    def test_supervisor_can_delete_any_follow_up(self, client, db_session):
        """Supervisor can delete any follow-up"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/follow-ups/{follow_up.id}", headers=headers)
        assert response.status_code == 204

    def test_mentor_cannot_delete_other_log_follow_up(self, client, db_session):
        """Mentor cannot delete follow-up from another mentor's log"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor, name="Mentor 2")
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor2, facility)
        follow_up = create_test_follow_up(db_session, log)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/follow-ups/{follow_up.id}", headers=headers)
        assert_error(response, 403)

    def test_delete_nonexistent_follow_up_returns_404(self, client, db_session):
        """Deleting nonexistent follow-up returns 404"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        fake_id = uuid4()
        response = client.delete(f"/api/follow-ups/{fake_id}", headers=headers)
        assert_error(response, 404)

    def test_unauthenticated_cannot_delete(self, client, db_session):
        """Unauthenticated users cannot delete follow-ups"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_log(db_session, mentor, facility)
        follow_up = create_test_follow_up(db_session, log)

        response = client.delete(f"/api/follow-ups/{follow_up.id}")
        assert_error(response, 403)
