"""
User Management Endpoint Tests

Tests for user CRUD operations and role-based access control.
"""

import pytest

from app.models import UserRole
from tests.helpers import (
    create_test_user,
    get_auth_headers, assert_success, assert_forbidden,
    assert_not_found
)


@pytest.mark.integration
class TestListUsers:
    """Tests for listing users"""

    def test_admin_can_list_all_users(self, client, db_session):
        """Test that admins can list all users"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)
        create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users", headers=headers)
        data = assert_success(response)

        assert len(data) >= 4
        emails = [u["email"] for u in data]
        assert "mentor1@test.com" in emails
        assert "supervisor@test.com" in emails

    def test_supervisor_can_list_all_users(self, client, db_session):
        """Test that supervisors can list all users"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users", headers=headers)
        data = assert_success(response)

        assert len(data) >= 2

    def test_mentor_cannot_list_users(self, client, db_session):
        """Test that mentors cannot list users"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users", headers=headers)
        assert_forbidden(response)

    def test_filter_by_role(self, client, db_session):
        """Test filtering users by role"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)
        create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users?role=mentor", headers=headers)
        data = assert_success(response)

        assert len(data) >= 2
        assert all(u["role"] == "mentor" for u in data)

    def test_filter_by_active_status(self, client, db_session):
        """Test filtering users by active status"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        active_user = create_test_user(db_session, email="active@test.com", role=UserRole.mentor)

        # Create inactive user
        inactive_user = create_test_user(db_session, email="inactive@test.com", role=UserRole.mentor)
        inactive_user.is_active = False
        db_session.commit()

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users?is_active=false", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert all(u["is_active"] is False for u in data)

    def test_search_by_name_or_email(self, client, db_session):
        """Test searching users by name or email"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        create_test_user(db_session, email="john.doe@test.com", name="John Doe", role=UserRole.mentor)
        create_test_user(db_session, email="jane.smith@test.com", name="Jane Smith", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get("/api/users?search=john", headers=headers)
        data = assert_success(response)

        assert len(data) >= 1
        assert any("john" in u["email"].lower() or "john" in u["name"].lower() for u in data)

    def test_pagination(self, client, db_session):
        """Test pagination parameters"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        # Create multiple users
        for i in range(5):
            create_test_user(db_session, email=f"user{i}@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        # Test limit
        response = client.get("/api/users?limit=2", headers=headers)
        data = assert_success(response)
        assert len(data) <= 2

        # Test skip
        response = client.get("/api/users?skip=2&limit=2", headers=headers)
        data = assert_success(response)
        assert len(data) <= 2

    def test_list_without_auth(self, client, db_session):
        """Test that listing users requires authentication"""
        response = client.get("/api/users")
        assert_forbidden(response)


@pytest.mark.integration
class TestGetUser:
    """Tests for getting a single user"""

    def test_admin_can_get_any_user(self, client, db_session):
        """Test that admins can get any user"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/users/{mentor.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(mentor.id)
        assert data["email"] == "mentor@test.com"
        assert "password" not in data
        assert "password_hash" not in data

    def test_supervisor_can_get_any_user(self, client, db_session):
        """Test that supervisors can get any user"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.get(f"/api/users/{mentor.id}", headers=headers)
        data = assert_success(response)

        assert data["id"] == str(mentor.id)

    def test_mentor_can_only_get_self(self, client, db_session):
        """Test that mentors can only get their own profile"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        # Can get self
        response = client.get(f"/api/users/{mentor1.id}", headers=headers)
        data = assert_success(response)
        assert data["id"] == str(mentor1.id)

        # Cannot get other mentor
        response = client.get(f"/api/users/{mentor2.id}", headers=headers)
        assert_forbidden(response)

    def test_get_nonexistent_user(self, client, db_session):
        """Test getting a user that doesn't exist"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        response = client.get(f"/api/users/{fake_id}", headers=headers)
        assert_not_found(response)

    def test_get_user_without_auth(self, client, db_session):
        """Test that getting a user requires authentication"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        response = client.get(f"/api/users/{mentor.id}")
        assert_forbidden(response)


@pytest.mark.integration
class TestCreateUser:
    """Tests for creating users"""

    def test_admin_can_create_user(self, client, db_session):
        """Test that admins can create users"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "SecurePassword123!",
            "role": "mentor",
            "designation": "Clinical Officer",
            "region_state": "Kano"
        }

        response = client.post("/api/users", json=user_data, headers=headers)
        data = assert_success(response, 201)

        assert data["email"] == "newuser@test.com"
        assert data["name"] == "New User"
        assert data["role"] == "mentor"
        assert data["is_active"] is True
        assert "password" not in data
        assert "password_hash" not in data

    def test_create_user_duplicate_email(self, client, db_session):
        """Test that duplicate emails are rejected"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        create_test_user(db_session, email="existing@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        user_data = {
            "email": "existing@test.com",
            "name": "Duplicate User",
            "password": "SecurePassword123!",
            "role": "mentor"
        }

        response = client.post("/api/users", json=user_data, headers=headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_user_password_is_hashed(self, client, db_session):
        """Test that passwords are properly hashed"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        user_data = {
            "email": "secure@test.com",
            "name": "Secure User",
            "password": "MySecretPassword123!",
            "role": "mentor"
        }

        response = client.post("/api/users", json=user_data, headers=headers)
        data = assert_success(response, 201)

        # Verify password is not returned
        assert "password" not in data

        # Verify password is hashed in database
        from app.models import User
        user = db_session.query(User).filter(User.email == "secure@test.com").first()
        assert user is not None
        assert user.password_hash != "MySecretPassword123!"
        assert len(user.password_hash) > 50  # Bcrypt hashes are ~60 chars

    def test_supervisor_cannot_create_user(self, client, db_session):
        """Test that supervisors cannot create users"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "Password123!",
            "role": "mentor"
        }

        response = client.post("/api/users", json=user_data, headers=headers)
        assert_forbidden(response)

    def test_mentor_cannot_create_user(self, client, db_session):
        """Test that mentors cannot create users"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "Password123!",
            "role": "mentor"
        }

        response = client.post("/api/users", json=user_data, headers=headers)
        assert_forbidden(response)

    def test_create_user_without_auth(self, client, db_session):
        """Test that creating users requires authentication"""
        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "Password123!",
            "role": "mentor"
        }

        response = client.post("/api/users", json=user_data)
        assert_forbidden(response)


@pytest.mark.integration
class TestUpdateUser:
    """Tests for updating users"""

    def test_admin_can_update_any_user(self, client, db_session):
        """Test that admins can update any user"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", name="Old Name", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {
            "name": "Updated Name",
            "designation": "Senior Mentor"
        }

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["name"] == "Updated Name"
        assert data["designation"] == "Senior Mentor"
        assert data["email"] == "mentor@test.com"  # Unchanged

    def test_admin_can_change_user_role(self, client, db_session):
        """Test that admins can change user roles"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        update_data = {"role": "supervisor"}

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["role"] == "supervisor"

    def test_supervisor_can_update_mentors(self, client, db_session):
        """Test that supervisors can update mentor profiles"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        update_data = {"name": "Updated by Supervisor"}

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["name"] == "Updated by Supervisor"

    def test_supervisor_cannot_change_roles(self, client, db_session):
        """Test that supervisors cannot change user roles"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        update_data = {"role": "admin"}

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        assert response.status_code == 403

    def test_mentor_can_update_self(self, client, db_session):
        """Test that mentors can update their own profile"""
        mentor = create_test_user(db_session, email="mentor@test.com", name="Old Name", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {
            "name": "My New Name",
            "designation": "Updated Designation"
        }

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        data = assert_success(response)

        assert data["name"] == "My New Name"

    def test_mentor_cannot_update_others(self, client, db_session):
        """Test that mentors cannot update other users"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        update_data = {"name": "Hacked Name"}

        response = client.put(f"/api/users/{mentor2.id}", json=update_data, headers=headers)
        assert_forbidden(response)

    def test_mentor_cannot_change_own_role(self, client, db_session):
        """Test that mentors cannot change their own role"""
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor.id)})
        headers = get_auth_headers(token)

        update_data = {"role": "admin"}

        response = client.put(f"/api/users/{mentor.id}", json=update_data, headers=headers)
        assert response.status_code == 403

    def test_update_nonexistent_user(self, client, db_session):
        """Test updating a user that doesn't exist"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"name": "Updated Name"}

        response = client.put(f"/api/users/{fake_id}", json=update_data, headers=headers)
        assert_not_found(response)


@pytest.mark.integration
class TestDeactivateUser:
    """Tests for deactivating users"""

    def test_admin_can_deactivate_user(self, client, db_session):
        """Test that admins can deactivate users"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/users/{mentor.id}/deactivate", headers=headers)
        data = assert_success(response)

        assert data["is_active"] is False

    def test_admin_can_reactivate_user(self, client, db_session):
        """Test that admins can reactivate users"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        mentor.is_active = False
        db_session.commit()

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/users/{mentor.id}/activate", headers=headers)
        data = assert_success(response)

        assert data["is_active"] is True

    def test_supervisor_cannot_deactivate_user(self, client, db_session):
        """Test that supervisors cannot deactivate users"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.put(f"/api/users/{mentor.id}/deactivate", headers=headers)
        assert_forbidden(response)


@pytest.mark.integration
class TestDeleteUser:
    """Tests for deleting users"""

    def test_admin_can_delete_user(self, client, db_session):
        """Test that admins can delete users"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/users/{mentor.id}", headers=headers)
        assert response.status_code == 204

        # Verify deletion
        response = client.get(f"/api/users/{mentor.id}", headers=headers)
        assert_not_found(response)

    def test_cannot_delete_user_with_logs(self, client, db_session):
        """Test that users with mentorship logs cannot be deleted"""
        from tests.helpers import create_test_facility, create_test_mentorship_log

        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)
        facility = create_test_facility(db_session)

        # Create a mentorship log for this mentor
        create_test_mentorship_log(db_session, mentor=mentor, facility=facility)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/users/{mentor.id}", headers=headers)
        assert response.status_code == 400
        assert "mentorship logs" in response.json()["detail"].lower()

    def test_delete_nonexistent_user(self, client, db_session):
        """Test deleting a user that doesn't exist"""
        admin = create_test_user(db_session, email="admin@test.com", role=UserRole.admin)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(admin.id)})
        headers = get_auth_headers(token)

        from uuid import uuid4
        fake_id = uuid4()

        response = client.delete(f"/api/users/{fake_id}", headers=headers)
        assert_not_found(response)

    def test_supervisor_cannot_delete_user(self, client, db_session):
        """Test that supervisors cannot delete users"""
        supervisor = create_test_user(db_session, email="supervisor@test.com", role=UserRole.supervisor)
        mentor = create_test_user(db_session, email="mentor@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(supervisor.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/users/{mentor.id}", headers=headers)
        assert_forbidden(response)

    def test_mentor_cannot_delete_user(self, client, db_session):
        """Test that mentors cannot delete users"""
        mentor1 = create_test_user(db_session, email="mentor1@test.com", role=UserRole.mentor)
        mentor2 = create_test_user(db_session, email="mentor2@test.com", role=UserRole.mentor)

        from app.utils.security import create_access_token
        token = create_access_token(data={"sub": str(mentor1.id)})
        headers = get_auth_headers(token)

        response = client.delete(f"/api/users/{mentor2.id}", headers=headers)
        assert_forbidden(response)
