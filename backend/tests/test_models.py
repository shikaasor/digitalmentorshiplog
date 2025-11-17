"""
Model Tests

Tests for SQLAlchemy models to verify they work correctly.
"""

import pytest
from datetime import date, timedelta

from app.models import (
    User, Facility, MentorshipLog, SkillsTransfer,
    FollowUp, Attachment, UserFacilityAssignment,
    UserRole, LogStatus, FollowUpStatus
)
from tests.helpers import (
    create_test_user, create_test_facility,
    create_test_mentorship_log
)


@pytest.mark.unit
class TestUserModel:
    """Tests for User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = create_test_user(
            db_session,
            email="testuser@example.com",
            name="Test User",
            role=UserRole.mentor
        )

        assert user.id is not None
        assert user.email == "testuser@example.com"
        assert user.name == "Test User"
        assert user.role == UserRole.mentor
        assert user.is_active is True
        assert user.password_hash is not None
        assert user.created_at is not None

    def test_user_role_enum(self, db_session):
        """Test that user roles are properly constrained"""
        # Test valid roles
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        assert mentor.role == UserRole.mentor

        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        assert supervisor.role == UserRole.supervisor

        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        assert admin.role == UserRole.admin

    def test_user_unique_email(self, db_session):
        """Test that email must be unique"""
        create_test_user(db_session, email="unique@test.com")

        # Attempting to create another user with same email should fail
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            create_test_user(db_session, email="unique@test.com")
            db_session.commit()


@pytest.mark.unit
class TestFacilityModel:
    """Tests for Facility model"""

    def test_create_facility(self, db_session):
        """Test creating a facility"""
        facility = create_test_facility(
            db_session,
            name="Test Clinic",
            code="TC-001",
            location="Test City",
            state="Test State"
        )

        assert facility.id is not None
        assert facility.name == "Test Clinic"
        assert facility.code == "TC-001"
        assert facility.location == "Test City"
        assert facility.state == "Test State"
        assert facility.created_at is not None

    def test_facility_unique_code(self, db_session):
        """Test that facility code must be unique"""
        create_test_facility(db_session, code="UNIQUE-001")

        # Attempting to create another facility with same code should fail
        with pytest.raises(Exception):
            create_test_facility(db_session, code="UNIQUE-001")
            db_session.commit()


@pytest.mark.unit
class TestMentorshipLogModel:
    """Tests for MentorshipLog model"""

    def test_create_mentorship_log(self, db_session):
        """Test creating a mentorship log"""
        mentor = create_test_user(db_session, email="mentor@test.com")
        facility = create_test_facility(db_session)

        log = create_test_mentorship_log(
            db_session,
            mentor=mentor,
            facility=facility,
            visit_date=date.today() + timedelta(days=7)
        )

        assert log.id is not None
        assert log.mentor_id == mentor.id
        assert log.facility_id == facility.id
        assert log.status == LogStatus.draft
        assert log.created_at is not None

    def test_mentorship_log_relationships(self, db_session):
        """Test mentorship log relationships with facility and mentor"""
        mentor = create_test_user(db_session, email="mentor@test.com")
        facility = create_test_facility(db_session)

        log = create_test_mentorship_log(
            db_session,
            mentor=mentor,
            facility=facility
        )

        # Test relationships work
        db_session.refresh(log)
        assert log.mentor.email == "mentor@test.com"
        assert log.facility.name == facility.name

    def test_mentorship_log_status_enum(self, db_session):
        """Test that log status uses proper enum values"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)

        # Test each status
        for status in [LogStatus.draft, LogStatus.submitted, LogStatus.approved, LogStatus.completed]:
            log = create_test_mentorship_log(
                db_session,
                mentor=mentor,
                facility=facility,
                status=status
            )
            assert log.status == status


@pytest.mark.unit
class TestSkillsTransferModel:
    """Tests for SkillsTransfer model (Section 4 of PDF)"""

    def test_create_skills_transfer(self, db_session):
        """Test creating a skills transfer record"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        skills_transfer = SkillsTransfer(
            mentorship_log_id=log.id,
            skill_knowledge_transferred="Advanced ART initiation and monitoring",
            recipient_name="Dr. Ahmed Ibrahim",
            recipient_cadre="Doctor",
            method="Side-by-side mentorship",
            competency_level="Intermediate",
            followup_needed=True
        )
        db_session.add(skills_transfer)
        db_session.commit()
        db_session.refresh(skills_transfer)

        assert skills_transfer.id is not None
        assert skills_transfer.mentorship_log_id == log.id
        assert skills_transfer.skill_knowledge_transferred == "Advanced ART initiation and monitoring"
        assert skills_transfer.recipient_name == "Dr. Ahmed Ibrahim"
        assert skills_transfer.recipient_cadre == "Doctor"
        assert skills_transfer.method == "Side-by-side mentorship"
        assert skills_transfer.competency_level == "Intermediate"
        assert skills_transfer.followup_needed is True

    def test_skills_transfer_relationship(self, db_session):
        """Test skills transfer relationship with mentorship log"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        skills_transfer = SkillsTransfer(
            mentorship_log_id=log.id,
            skill_knowledge_transferred="TB/HIV co-infection management",
            recipient_name="Nurse Fatima Usman",
            recipient_cadre="Nurse"
        )
        db_session.add(skills_transfer)
        db_session.commit()

        # Refresh and test relationship
        db_session.refresh(log)
        assert len(log.skills_transfers) == 1
        assert log.skills_transfers[0].skill_knowledge_transferred == "TB/HIV co-infection management"


@pytest.mark.unit
class TestFollowUpModel:
    """Tests for FollowUp model"""

    def test_create_follow_up(self, db_session):
        """Test creating a follow-up"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        follow_up = FollowUp(
            mentorship_log_id=log.id,
            action_item="Schedule training session",
            status=FollowUpStatus.pending,
            assigned_to=mentor.id,
            target_date=date.today() + timedelta(days=30),
            responsible_person="Dr. Ahmed Ibrahim",
            priority="High",
            resources_needed="Training materials and venue"
        )
        db_session.add(follow_up)
        db_session.commit()
        db_session.refresh(follow_up)

        assert follow_up.id is not None
        assert follow_up.action_item == "Schedule training session"
        assert follow_up.status == FollowUpStatus.pending
        assert follow_up.assigned_to == mentor.id
        assert follow_up.target_date == date.today() + timedelta(days=30)
        assert follow_up.responsible_person == "Dr. Ahmed Ibrahim"
        assert follow_up.priority == "High"
        assert follow_up.resources_needed == "Training materials and venue"

    def test_follow_up_status_enum(self, db_session):
        """Test follow-up status enum values"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        # Test each status
        for status in [FollowUpStatus.pending, FollowUpStatus.in_progress, FollowUpStatus.completed]:
            follow_up = FollowUp(
                mentorship_log_id=log.id,
                action_item=f"Test action - {status}",
                status=status
            )
            db_session.add(follow_up)
            db_session.commit()
            db_session.refresh(follow_up)
            assert follow_up.status == status


@pytest.mark.unit
class TestUserFacilityAssignmentModel:
    """Tests for UserFacilityAssignment model"""

    def test_create_assignment(self, db_session):
        """Test creating a user-facility assignment"""
        user = create_test_user(db_session)
        facility = create_test_facility(db_session)

        assignment = UserFacilityAssignment(
            user_id=user.id,
            facility_id=facility.id
        )
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)

        assert assignment.id is not None
        assert assignment.user_id == user.id
        assert assignment.facility_id == facility.id
        assert assignment.assigned_at is not None

    def test_assignment_relationships(self, db_session):
        """Test assignment relationships"""
        user = create_test_user(db_session, email="mentor@test.com")
        facility = create_test_facility(db_session, name="Test Clinic")

        assignment = UserFacilityAssignment(
            user_id=user.id,
            facility_id=facility.id
        )
        db_session.add(assignment)
        db_session.commit()

        # Test relationships
        db_session.refresh(user)
        db_session.refresh(facility)
        assert len(user.facility_assignments) == 1
        assert len(facility.user_assignments) == 1


@pytest.mark.unit
class TestModelCascadeDeletes:
    """Tests for cascade delete behavior"""

    def test_delete_mentorship_log_deletes_skills_transfers(self, db_session):
        """Test that deleting a log deletes its skills transfers"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        # Add skills transfers
        skills1 = SkillsTransfer(
            mentorship_log_id=log.id,
            skill_knowledge_transferred="ART initiation",
            recipient_name="Dr. Ahmed",
            recipient_cadre="Doctor"
        )
        skills2 = SkillsTransfer(
            mentorship_log_id=log.id,
            skill_knowledge_transferred="TB screening",
            recipient_name="Nurse Fatima",
            recipient_cadre="Nurse"
        )
        db_session.add_all([skills1, skills2])
        db_session.commit()

        log_id = log.id

        # Delete the log
        db_session.delete(log)
        db_session.commit()

        # Verify skills transfers were also deleted
        skills = db_session.query(SkillsTransfer).filter_by(
            mentorship_log_id=log_id
        ).all()
        assert len(skills) == 0

    def test_delete_mentorship_log_deletes_follow_ups(self, db_session):
        """Test that deleting a log deletes its follow-ups"""
        mentor = create_test_user(db_session)
        facility = create_test_facility(db_session)
        log = create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        # Add follow-up
        follow_up = FollowUp(
            mentorship_log_id=log.id,
            action_item="Test action",
            status=FollowUpStatus.pending
        )
        db_session.add(follow_up)
        db_session.commit()

        log_id = log.id

        # Delete the log
        db_session.delete(log)
        db_session.commit()

        # Verify follow-up was also deleted
        follow_ups = db_session.query(FollowUp).filter_by(
            mentorship_log_id=log_id
        ).all()
        assert len(follow_ups) == 0
