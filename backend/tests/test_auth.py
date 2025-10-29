"""
Tests for Authentication Endpoints

Tests for user registration, login, logout, and current user info endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.utils.security import create_access_token


@pytest.mark.auth
@pytest.mark.integration
class TestRegisterEndpoint:
    """Tests for POST /api/auth/register"""

    def test_register_new_user_success(self, client: TestClient, db_session: Session):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "name": "New User",
            "role": "mentor",
            "designation": "Senior Mentor",
            "region_state": "Lagos"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["role"] == user_data["role"]
        assert data["designation"] == user_data["designation"]
        assert data["region_state"] == user_data["region_state"]
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_minimal_fields(self, client: TestClient, db_session: Session):
        """Test registration with only required fields"""
        user_data = {
            "email": "minimal@example.com",
            "password": "password123",
            "name": "Minimal User",
            "role": "mentor"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["designation"] is None
        assert data["region_state"] is None

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration fails with duplicate email"""
        user_data = {
            "email": test_user.email,  # Use existing user's email
            "password": "password123",
            "name": "Duplicate User",
            "role": "mentor"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration fails with invalid email"""
        user_data = {
            "email": "not-an-email",
            "password": "password123",
            "name": "Test User",
            "role": "mentor"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_missing_required_fields(self, client: TestClient):
        """Test registration fails without required fields"""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
            # Missing name and role
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_invalid_role(self, client: TestClient):
        """Test registration fails with invalid role"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
            "role": "invalid_role"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_all_roles(self, client: TestClient, db_session: Session):
        """Test registration with different valid roles"""
        roles = ["mentor", "supervisor", "admin"]

        for role in roles:
            user_data = {
                "email": f"{role}@example.com",
                "password": "password123",
                "name": f"{role.capitalize()} User",
                "role": role
            }

            response = client.post("/api/auth/register", json=user_data)

            assert response.status_code == 201
            data = response.json()
            assert data["role"] == role


@pytest.mark.auth
@pytest.mark.integration
class TestLoginEndpoint:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        login_data = {
            "email": test_user.email,
            "password": "password123"  # From fixture
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login fails with wrong password"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login fails for non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_inactive_user(self, client: TestClient, test_user: User, db_session: Session):
        """Test login fails for inactive user"""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()

        login_data = {
            "email": test_user.email,
            "password": "password123"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 403
        assert "Account is inactive" in response.json()["detail"]

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        login_data = {
            "email": "not-an-email",
            "password": "password123"
        }

        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 422

    def test_login_missing_fields(self, client: TestClient):
        """Test login fails without required fields"""
        # Missing password
        response = client.post("/api/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        # Missing email
        response = client.post("/api/auth/login", json={"password": "password123"})
        assert response.status_code == 422

    def test_login_different_roles(self, client: TestClient, test_user: User, test_supervisor: User, test_admin: User):
        """Test login works for all user roles"""
        users = [
            (test_user, "password123"),
            (test_supervisor, "supervisorPassword123"),
            (test_admin, "adminPassword123")
        ]

        for user, password in users:
            login_data = {
                "email": user.email,
                "password": password
            }

            response = client.post("/api/auth/login", json=login_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


@pytest.mark.auth
@pytest.mark.integration
class TestGetCurrentUserEndpoint:
    """Tests for GET /api/auth/me"""

    def test_get_current_user_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test getting current user info with valid token"""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role.value
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_current_user_without_token(self, client: TestClient):
        """Test getting current user fails without token"""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # No credentials provided

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user fails with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client: TestClient, test_user: User):
        """Test getting current user fails with expired token"""
        from datetime import timedelta

        # Create expired token
        expired_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_different_roles(
        self,
        client: TestClient,
        test_user: User,
        test_supervisor: User,
        test_admin: User,
        auth_token: str,
        supervisor_token: str,
        admin_token: str
    ):
        """Test getting current user works for all roles"""
        test_cases = [
            (test_user, auth_token),
            (test_supervisor, supervisor_token),
            (test_admin, admin_token)
        ]

        for user, token in test_cases:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/auth/me", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(user.id)
            assert data["email"] == user.email
            assert data["role"] == user.role.value


@pytest.mark.auth
@pytest.mark.integration
class TestLogoutEndpoint:
    """Tests for POST /api/auth/logout"""

    def test_logout_success(self, client: TestClient, auth_headers: dict):
        """Test logout returns success message"""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    def test_logout_without_token(self, client: TestClient):
        """Test logout without token (currently allowed)"""
        response = client.post("/api/auth/logout")

        # Note: Current implementation doesn't require authentication
        # This is acceptable for stateless JWT systems
        assert response.status_code == 200


@pytest.mark.auth
@pytest.mark.e2e
class TestAuthenticationFlow:
    """End-to-end tests for complete authentication flows"""

    def test_register_login_get_user_flow(self, client: TestClient):
        """Test complete flow: register -> login -> get user info"""
        # Step 1: Register
        register_data = {
            "email": "flowtest@example.com",
            "password": "securepass123",
            "name": "Flow Test User",
            "role": "mentor",
            "designation": "Test Mentor"
        }

        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        user_data = register_response.json()

        # Step 2: Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }

        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]

        # Step 3: Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        me_data = me_response.json()

        # Verify data consistency
        assert me_data["id"] == user_data["id"]
        assert me_data["email"] == register_data["email"]
        assert me_data["name"] == register_data["name"]

    def test_register_logout_login_again(self, client: TestClient):
        """Test logout doesn't prevent subsequent login"""
        # Register
        register_data = {
            "email": "logouttest@example.com",
            "password": "password123",
            "name": "Logout Test",
            "role": "mentor"
        }
        client.post("/api/auth/register", json=register_data)

        # First login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        login_response1 = client.post("/api/auth/login", json=login_data)
        assert login_response1.status_code == 200
        token1 = login_response1.json()["access_token"]

        # Logout
        headers = {"Authorization": f"Bearer {token1}"}
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200

        # Login again (should work)
        login_response2 = client.post("/api/auth/login", json=login_data)
        assert login_response2.status_code == 200
        token2 = login_response2.json()["access_token"]

        # Verify can still access protected endpoint
        headers2 = {"Authorization": f"Bearer {token2}"}
        me_response = client.get("/api/auth/me", headers=headers2)
        assert me_response.status_code == 200
