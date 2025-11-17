"""
Authentication Dependencies

FastAPI dependencies for authentication and authorization.
Used to protect routes and extract user information from JWT tokens.
"""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.utils.security import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Example:
        ```python
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
        ```
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify token and get user ID
    user_id_str = verify_token(token)
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert user_id string to UUID
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user (alias for get_current_user).

    This is redundant since get_current_user already checks is_active,
    but provided for API consistency.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User: The authenticated active user
    """
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise.

    Useful for endpoints that have different behavior for authenticated vs anonymous users.

    Args:
        credentials: Optional HTTP Bearer token
        db: Database session

    Returns:
        Optional[User]: User if authenticated, None otherwise

    Example:
        ```python
        @router.get("/public")
        async def public_endpoint(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello, {user.name}"}
            return {"message": "Hello, anonymous"}
        ```
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        user_id_str = verify_token(token)
        if user_id_str is None:
            return None

        # Convert user_id string to UUID
        user_id = uuid.UUID(user_id_str)

        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
    except Exception:
        return None


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.

    Creates a dependency that checks if the current user has one of the allowed roles.

    Args:
        *allowed_roles: One or more UserRole values that are allowed

    Returns:
        Callable: A dependency function that checks user role

    Raises:
        HTTPException: 403 if user doesn't have required role

    Example:
        ```python
        @router.post("/facilities")
        async def create_facility(
            facility: FacilityCreate,
            current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor))
        ):
            # Only admins and supervisors can create facilities
            ...
        ```
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user

    return role_checker


# Convenience dependencies for common role checks
require_admin = require_role(UserRole.admin)
require_supervisor_or_admin = require_role(UserRole.supervisor, UserRole.admin)
require_any_role = require_role(UserRole.mentor, UserRole.supervisor, UserRole.admin)


def can_approve_log(
    log,
    current_user: User,
    db: Session
) -> bool:
    """
    Check if current user can approve a specific mentorship log.

    Rules:
    - Admins can approve any log
    - Supervisors can only approve logs from their direct mentees
    - Mentors cannot approve logs

    Args:
        log: MentorshipLog object
        current_user: Current authenticated user
        db: Database session

    Returns:
        bool: True if user can approve, False otherwise
    """
    from app.models import MentorshipLog

    # Admins can approve anything
    if current_user.role == UserRole.admin:
        return True

    # Supervisors can only approve their mentees' logs
    if current_user.role == UserRole.supervisor:
        # Get the mentor of this log
        mentor = db.query(User).filter(User.id == log.mentor_id).first()
        if mentor and mentor.supervisor_id == current_user.id:
            return True

    return False


def can_view_as_specialist(
    log,
    user: User,
    db: Session
) -> bool:
    """
    Check if user can view log as a specialist.
    Returns True if user has specialization matching log's thematic areas.

    Args:
        log: MentorshipLog object
        user: User to check
        db: Database session

    Returns:
        bool: True if user has specialist access, False otherwise
    """
    from app.models import UserSpecialization

    if not log.thematic_areas or not isinstance(log.thematic_areas, list):
        return False

    # Get user's specializations
    user_specs = db.query(UserSpecialization).filter(
        UserSpecialization.user_id == user.id
    ).all()

    user_thematic_areas = {spec.thematic_area for spec in user_specs}
    log_thematic_areas = set(log.thematic_areas)

    # Check if there's any overlap
    return bool(user_thematic_areas & log_thematic_areas)


def get_visible_logs_query(
    current_user: User,
    db: Session
):
    """
    Build query for logs visible to current user based on role and access:
    - Mentor: Own logs only
    - Supervisor: Own logs + mentees' logs
    - Admin: All logs
    - Specialist: Logs matching their thematic areas (submitted status only)

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Query: SQLAlchemy query for visible logs
    """
    from sqlalchemy import or_, and_, func
    from app.models import MentorshipLog, UserSpecialization

    if current_user.role == UserRole.admin:
        # Admins see everything
        return db.query(MentorshipLog)

    conditions = []

    # Always see own logs
    conditions.append(MentorshipLog.mentor_id == current_user.id)

    # Supervisors see their mentees' logs
    if current_user.role == UserRole.supervisor:
        mentee_ids = db.query(User.id).filter(User.supervisor_id == current_user.id).scalar_subquery()
        conditions.append(MentorshipLog.mentor_id.in_(mentee_ids))

    # Specialist access: see submitted/approved logs with matching thematic areas
    user_specs = db.query(UserSpecialization).filter(
        UserSpecialization.user_id == current_user.id
    ).all()

    if user_specs:
        specialist_areas = [spec.thematic_area for spec in user_specs]
        if specialist_areas:
            # PostgreSQL: Check if JSON array contains any of the specialist areas
            # Cast JSON to JSONB before using ?| operator for overlap between arrays
            from sqlalchemy import text
            specialist_condition = and_(
                text(f"mentorship_logs.thematic_areas::jsonb ?| ARRAY{specialist_areas}"),
                MentorshipLog.status.in_(['submitted', 'approved'])  # Only see submitted/approved logs as specialist
            )
            conditions.append(specialist_condition)

    return db.query(MentorshipLog).filter(or_(*conditions))
