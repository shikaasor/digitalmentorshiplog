"""
User Management Endpoints

Endpoints for managing system users (mentors, supervisors, admins).
Includes user CRUD operations with role-based access control.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, UserRole, UserSpecialization
from app.schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse
from app.dependencies import get_current_user, require_role
from app.utils.security import hash_password


router = APIRouter(prefix="/api/users", tags=["users"])


def check_user_update_permissions(current_user: User, target_user: User, update_data: dict) -> None:
    """
    Check if current user has permission to update target user.

    Rules:
    - Admins can update anyone and change roles
    - Supervisors can update mentors but cannot change roles
    - Mentors can only update themselves and cannot change roles
    """
    # Admins can do anything
    if current_user.role == UserRole.admin:
        return

    # Supervisors can update mentors, but not change roles
    if current_user.role == UserRole.supervisor:
        if "role" in update_data and update_data["role"] is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisors cannot change user roles"
            )
        if target_user.role not in [UserRole.mentor]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisors can only update mentor profiles"
            )
        return

    # Mentors can only update themselves and cannot change roles
    if current_user.role == UserRole.mentor:
        if current_user.id != target_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Mentors can only update their own profile"
            )
        if "role" in update_data and update_data["role"] is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role"
            )
        return


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.supervisor)),
):
    """
    List all users with optional filtering.

    Permissions:
    - Admins and supervisors can list users
    - Mentors cannot access this endpoint

    Filters:
    - **role**: Filter by user role (mentor, supervisor, admin)
    - **is_active**: Filter by active status (true/false)
    - **search**: Search by name or email
    """
    query = db.query(User)

    # Apply filters
    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination and ordering
    users = (
        query
        .order_by(User.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single user by ID.

    Permissions:
    - Admins and supervisors can view any user
    - Mentors can only view their own profile
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions
    if current_user.role == UserRole.mentor and current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Create a new user (Admin only).

    Permissions:
    - Only admins can create users

    Accepts:
    - supervisor_id: Assign a supervisor (for mentors)
    - specializations: List of thematic area specializations
    """
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_data.email}' already exists"
        )

    # Validate supervisor_id if provided
    if user_data.supervisor_id:
        supervisor = db.query(User).filter(
            User.id == user_data.supervisor_id,
            User.role == UserRole.supervisor
        ).first()
        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid supervisor_id. Must be an existing supervisor."
            )

    # Hash the password
    password_hash = hash_password(user_data.password)

    # Create user (exclude password and specializations from dict, add password_hash)
    user_dict = user_data.model_dump(exclude={"password", "specializations"})
    user = User(**user_dict, password_hash=password_hash)

    db.add(user)
    db.flush()  # Flush to get user.id without committing

    # Add specializations if provided
    if user_data.specializations:
        for thematic_area in user_data.specializations:
            specialization = UserSpecialization(
                user_id=user.id,
                thematic_area=thematic_area
            )
            db.add(specialization)

    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user.

    Permissions:
    - Admins can update anyone and change roles
    - Supervisors can update mentors but cannot change roles
    - Mentors can only update themselves and cannot change their role

    Can update:
    - supervisor_id: Change assigned supervisor
    - specializations: Update thematic area specializations
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get update data and check permissions
    update_dict = user_data.model_dump(exclude_unset=True)
    check_user_update_permissions(current_user, user, update_dict)

    # Handle specializations update separately
    specializations = update_dict.pop("specializations", None)

    # Validate supervisor_id if provided
    if "supervisor_id" in update_dict and update_dict["supervisor_id"]:
        supervisor = db.query(User).filter(
            User.id == update_dict["supervisor_id"],
            User.role == UserRole.supervisor
        ).first()
        if not supervisor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid supervisor_id. Must be an existing supervisor."
            )

    # Update user fields
    for field, value in update_dict.items():
        setattr(user, field, value)

    # Update specializations if provided
    if specializations is not None:
        # Remove existing specializations
        db.query(UserSpecialization).filter(
            UserSpecialization.user_id == user.id
        ).delete()

        # Add new specializations
        for thematic_area in specializations:
            specialization = UserSpecialization(
                user_id=user.id,
                thematic_area=thematic_area
            )
            db.add(specialization)

    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Deactivate a user (Admin only).

    Permissions:
    - Only admins can deactivate users
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Activate a user (Admin only).

    Permissions:
    - Only admins can activate users
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Delete a user (Admin only).

    Permissions:
    - Only admins can delete users

    Note: This will fail if the user has associated mentorship logs.
    Consider deactivating users instead of deleting them.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user has mentorship logs
    if user.mentorship_logs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete user with associated mentorship logs. Consider deactivating the user instead."
        )

    db.delete(user)
    db.commit()

    return None
