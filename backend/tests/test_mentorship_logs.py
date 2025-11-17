"""
Mentorship Log Endpoint Tests

Tests for mentorship log CRUD operations and workflow.
"""

import pytest
from datetime import date, timedelta

from app.models import UserRole, LogStatus
from tests.helpers import (
    create_test_user, create_test_facility, create_test_mentorship_log,
    get_auth_headers, assert_success, assert_unauthorized, assert_forbidden,
    assert_not_found
)


@pytest.mark.integration
class TestCreateMentorshipLog:
    """Tests for creating mentorship logs"""

    def test_create_log_success(self, client, db_session):
        """Test creating a mentorship log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        log_data = {
            "facility_id": str(facility.id),
            "visit_date": str(date.today()),
            "interaction_type": "On-site",
            "duration_hours": 3,
            "duration_minutes": 30,
            "activities_conducted": ["Direct clinical service", "Case review/discussion"],
            "thematic_areas": ["General HIV care and treatment"],
            "strengths_observed": "Good patient documentation",
            "gaps_identified": "Need more ART training",
        }

        response = client.post("/api/mentorship-logs", json=log_data, headers=headers)
        data = assert_success(response, 201)

        assert data["facility_id"] == str(facility.id)
        assert data["mentor_id"] == str(mentor.id)
        assert data["status"] == "draft"
        assert data["interaction_type"] == "On-site"
        assert data["duration_hours"] == 3
        assert "Direct clinical service" in data["activities_conducted"]

    def test_create_log_with_nested_data(self, client, db_session):
        """Test creating a log with skills transfers and follow-ups"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        log_data = {
            "facility_id": str(facility.id),
            "visit_date": str(date.today()),
            "interaction_type": "On-site",
            "skills_transfers": [
                {
                    "skill_knowledge_transferred": "ART initiation",
                    "recipient_name": "Dr. Ahmed",
                    "recipient_cadre": "Doctor",
                    "method": "Side-by-side mentorship",
                    "competency_level": "Intermediate"
                }
            ],
            "follow_ups": [
                {
                    "action_item": "Schedule follow-up training",
                    "responsible_person": "Dr. Ahmed",
                    "target_date": str(date.today() + timedelta(days=30)),
                    "priority": "High"
                }
            ]
        }

        response = client.post("/api/mentorship-logs", json=log_data, headers=headers)
        data = assert_success(response, 201)

        assert len(data["skills_transfers"]) == 1
        assert data["skills_transfers"][0]["skill_knowledge_transferred"] == "ART initiation"
        assert len(data["follow_ups"]) == 1
        assert data["follow_ups"][0]["action_item"] == "Schedule follow-up training"

    def test_create_log_without_auth(self, client, db_session):
        """Test creating a log without authentication"""
        facility = create_test_facility(db_session)

        log_data = {
            "facility_id": str(facility.id),
            "visit_date": str(date.today()),
        }

        response = client.post("/api/mentorship-logs", json=log_data)
        assert_forbidden(response)


@pytest.mark.integration
class TestListMentorshipLogs:
    """Tests for listing mentorship logs"""

    def test_mentor_sees_only_own_logs(self, client, db_session):
        """Test that mentors can only see their own logs"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        # Create logs for both mentors
        create_test_mentorship_log(db_session, mentor=mentor1, facility=facility)
        create_test_mentorship_log(db_session, mentor=mentor2, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/mentorship-logs", headers=headers)
        data = assert_success(response)

        assert len(data) == 1
        assert data[0]["mentor_id"] == str(mentor1.id)

    def test_supervisor_sees_all_logs(self, client, db_session):
        """Test that supervisors can see all logs"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)

        # Create logs for both mentors
        create_test_mentorship_log(db_session, mentor=mentor1, facility=facility)
        create_test_mentorship_log(db_session, mentor=mentor2, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/mentorship-logs", headers=headers)
        data = assert_success(response)

        assert len(data) == 2

    def test_filter_by_facility(self, client, db_session):
        """Test filtering logs by facility"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility1 = create_test_facility(db_session, code="FAC1")
        facility2 = create_test_facility(db_session, code="FAC2")

        create_test_mentorship_log(db_session, mentor=mentor, facility=facility1)
        create_test_mentorship_log(db_session, mentor=mentor, facility=facility2)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/mentorship-logs?facility_id={facility1.id}", headers=headers)
        data = assert_success(response)

        assert len(data) == 1
        assert data[0]["facility_id"] == str(facility1.id)

    def test_filter_by_status(self, client, db_session):
        """Test filtering logs by status"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        log1 = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.draft)
        log2 = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/mentorship-logs?status=draft", headers=headers)
        data = assert_success(response)

        assert len(data) == 1
        assert data[0]["status"] == "draft"


@pytest.mark.integration
class TestGetMentorshipLog:
    """Tests for getting a single mentorship log"""

    def test_get_log_success(self, client, db_session):
        """Test getting a mentorship log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/mentorship-logs/{log.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(log.id)
        assert data["mentor_id"] == str(mentor.id)

    def test_mentor_cannot_view_others_log(self, client, db_session):
        """Test that mentors cannot view other mentors' logs"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor1, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor2.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/mentorship-logs/{log.id}", headers=headers)
        assert_forbidden(response)

    def test_supervisor_can_view_any_log(self, client, db_session):
        """Test that supervisors can view any log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/mentorship-logs/{log.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(log.id)


@pytest.mark.integration
class TestUpdateMentorshipLog:
    """Tests for updating mentorship logs"""

    def test_update_draft_log_success(self, client, db_session):
        """Test updating a draft log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.draft)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {
            "strengths_observed": "Updated strengths",
            "gaps_identified": "Updated gaps"
        }

        response = client.put(f"/api/mentorship-logs/{log.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["strengths_observed"] == "Updated strengths"
        assert data["gaps_identified"] == "Updated gaps"

    def test_cannot_update_submitted_log(self, client, db_session):
        """Test that submitted logs cannot be updated"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {"strengths_observed": "Updated"}

        response = client.put(f"/api/mentorship-logs/{log.id}", json=update_data, headers=headers)
        assert response.status_code == 400


@pytest.mark.integration
class TestSubmitMentorshipLog:
    """Tests for submitting mentorship logs"""

    def test_submit_draft_log_success(self, client, db_session):
        """Test submitting a draft log"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.draft)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/submit", headers=headers)
        data = assert_success(response)

        assert data["status"] == "submitted"
        assert data["submitted_at"] is not None

    def test_cannot_submit_already_submitted_log(self, client, db_session):
        """Test that already submitted logs cannot be submitted again"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/submit", headers=headers)
        assert response.status_code == 400


@pytest.mark.integration
class TestApproveMentorshipLog:
    """Tests for approving mentorship logs"""

    def test_supervisor_can_approve_log(self, client, db_session):
        """Test that supervisors can approve submitted logs"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/approve", headers=headers)
        data = assert_success(response)

        assert data["status"] == "approved"
        assert data["approved_at"] is not None
        assert data["approved_by"] == str(supervisor.id)

    def test_mentor_cannot_approve_log(self, client, db_session):
        """Test that mentors cannot approve logs"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/approve", headers=headers)
        assert_forbidden(response)

    def test_cannot_approve_draft_log(self, client, db_session):
        """Test that draft logs cannot be approved"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.draft)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/approve", headers=headers)
        assert response.status_code == 400


@pytest.mark.integration
class TestReturnLogToDraft:
    """Tests for returning logs to draft status"""

    def test_supervisor_can_return_to_draft(self, client, db_session):
        """Test that supervisors can return submitted logs to draft"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/return-to-draft", headers=headers)
        data = assert_success(response)

        assert data["status"] == "draft"
        assert data["submitted_at"] is None

    def test_mentor_cannot_return_to_draft(self, client, db_session):
        """Test that mentors cannot return logs to draft"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.post(f"/api/mentorship-logs/{log.id}/return-to-draft", headers=headers)
        assert_forbidden(response)


@pytest.mark.integration
class TestDeleteMentorshipLog:
    """Tests for deleting mentorship logs"""

    def test_mentor_can_delete_own_draft(self, client, db_session):
        """Test that mentors can delete their own draft logs"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.draft)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/mentorship-logs/{log.id}", headers=headers)
        assert response.status_code == 204

    def test_mentor_cannot_delete_submitted_log(self, client, db_session):
        """Test that mentors cannot delete submitted logs"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.submitted)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/mentorship-logs/{log.id}", headers=headers)
        assert response.status_code == 400

    def test_admin_can_delete_any_log(self, client, db_session):
        """Test that admins can delete any log"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility, status=LogStatus.approved)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/mentorship-logs/{log.id}", headers=headers)
        assert response.status_code == 204
