"""
Tests for Authentication Dependencies

Tests for JWT token validation, user extraction, and role-based access control.
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.dependencies import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    require_role,
    require_admin,
    require_supervisor_or_admin,
)
from app.models import User, UserRole
from app.utils.security import create_access_token


@pytest.mark.auth
@pytest.mark.unit
class TestGetCurrentUser:
    """Tests for get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self, db_session: Session, test_user: User, auth_token: str):
        """Test that a valid token returns the correct user"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_token)

        user = await get_current_user(credentials=credentials, db=db_session)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.name == test_user.name

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, db_session: Session):
        """Test that an invalid token raises 401"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self, db_session: Session, test_user: User):
        """Test that an expired token raises 401"""
        from datetime import timedelta

        # Create token that expires immediately
        expired_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_401(self, db_session: Session):
        """Test that a token for non-existent user raises 401"""
        import uuid

        # Create token for user that doesn't exist
        fake_user_id = str(uuid.uuid4())
        token = create_access_token(data={"sub": fake_user_id})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_inactive_user_raises_403(self, db_session: Session, test_user: User):
        """Test that an inactive user raises 403"""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()

        token = create_access_token(data={"sub": str(test_user.id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=db_session)

        assert exc_info.value.status_code == 403
        assert "Inactive user" in exc_info.value.detail


@pytest.mark.auth
@pytest.mark.unit
class TestGetCurrentActiveUser:
    """Tests for get_current_active_user dependency"""

    @pytest.mark.asyncio
    async def test_returns_active_user(self, test_user: User):
        """Test that it returns an active user"""
        user = await get_current_active_user(current_user=test_user)

        assert user.id == test_user.id
        assert user.is_active is True


@pytest.mark.auth
@pytest.mark.unit
class TestGetOptionalUser:
    """Tests for get_optional_user dependency"""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self, db_session: Session, test_user: User, auth_token: str):
        """Test that a valid token returns user"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_token)

        user = await get_optional_user(credentials=credentials, db=db_session)

        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_no_credentials_returns_none(self, db_session: Session):
        """Test that no credentials returns None"""
        user = await get_optional_user(credentials=None, db=db_session)

        assert user is None

    @pytest.mark.asyncio
    async def test_invalid_token_returns_none(self, db_session: Session):
        """Test that invalid token returns None (doesn't raise exception)"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        user = await get_optional_user(credentials=credentials, db=db_session)

        assert user is None

    @pytest.mark.asyncio
    async def test_inactive_user_returns_none(self, db_session: Session, test_user: User):
        """Test that inactive user returns None"""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()

        token = create_access_token(data={"sub": str(test_user.id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_optional_user(credentials=credentials, db=db_session)

        assert user is None


@pytest.mark.auth
@pytest.mark.unit
class TestRequireRole:
    """Tests for require_role dependency factory"""

    @pytest.mark.asyncio
    async def test_user_with_required_role_passes(self, test_user: User):
        """Test that user with required role passes"""
        role_checker = require_role(UserRole.mentor)

        user = await role_checker(current_user=test_user)

        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_user_with_one_of_multiple_roles_passes(self, test_supervisor: User):
        """Test that user with one of multiple allowed roles passes"""
        role_checker = require_role(UserRole.supervisor, UserRole.admin)

        user = await role_checker(current_user=test_supervisor)

        assert user.id == test_supervisor.id

    @pytest.mark.asyncio
    async def test_user_without_required_role_raises_403(self, test_user: User):
        """Test that user without required role raises 403"""
        role_checker = require_role(UserRole.admin)

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user=test_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_mentor_cannot_access_admin_only(self, test_user: User):
        """Test that mentor cannot access admin-only endpoint"""
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=test_user)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_access_admin_only(self, test_admin: User):
        """Test that admin can access admin-only endpoint"""
        user = await require_admin(current_user=test_admin)

        assert user.id == test_admin.id
        assert user.role == UserRole.admin

    @pytest.mark.asyncio
    async def test_supervisor_can_access_supervisor_or_admin(self, test_supervisor: User):
        """Test that supervisor can access supervisor-or-admin endpoint"""
        user = await require_supervisor_or_admin(current_user=test_supervisor)

        assert user.id == test_supervisor.id
        assert user.role == UserRole.supervisor

    @pytest.mark.asyncio
    async def test_admin_can_access_supervisor_or_admin(self, test_admin: User):
        """Test that admin can access supervisor-or-admin endpoint"""
        user = await require_supervisor_or_admin(current_user=test_admin)

        assert user.id == test_admin.id
        assert user.role == UserRole.admin

    @pytest.mark.asyncio
    async def test_mentor_cannot_access_supervisor_or_admin(self, test_user: User):
        """Test that mentor cannot access supervisor-or-admin endpoint"""
        with pytest.raises(HTTPException) as exc_info:
            await require_supervisor_or_admin(current_user=test_user)

        assert exc_info.value.status_code == 403
