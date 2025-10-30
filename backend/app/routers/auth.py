"""
Authentication Router

Endpoints for user authentication including registration, login, and user info.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_active_user
from app.models import User, UserRole
from app.schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from app.utils.security import verify_password, hash_password, create_access_token


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account with the provided information.
    Email must be unique.

    Args:
        user_data: User registration data (email, password, name, etc.)
        db: Database session

    Returns:
        UserResponse: The created user (without password)

    Raises:
        HTTPException 400: If email already exists

    Example:
        ```json
        POST /api/auth/register
        {
            "email": "mentor@example.com",
            "password": "securepassword123",
            "name": "John Doe",
            "role": "mentor",
            "designation": "Senior Mentor",
            "region_state": "Lagos"
        }
        ```
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        role=user_data.role,
        designation=user_data.designation,
        region_state=user_data.region_state,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token.

    Authenticates user with email and password, returns JWT token.

    Args:
        login_data: Login credentials (email and password)
        db: Database session

    Returns:
        TokenResponse: JWT access token and token type

    Raises:
        HTTPException 401: If credentials are invalid

    Example:
        ```json
        POST /api/auth/login
        {
            "email": "mentor@example.com",
            "password": "securepassword123"
        }

        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.

    Returns the profile of the currently authenticated user.
    Requires valid JWT token in Authorization header.

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        UserResponse: User profile information

    Example:
        ```bash
        GET /api/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "mentor@example.com",
            "name": "John Doe",
            "role": "mentor",
            "designation": "Senior Mentor",
            "region_state": "Lagos",
            "is_active": true,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
        ```
    """
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout user (placeholder for token blacklisting).

    In a stateless JWT system, logout is typically handled client-side
    by discarding the token. For enhanced security, implement token
    blacklisting with Redis or database.

    Returns:
        dict: Logout success message

    Example:
        ```bash
        POST /api/auth/logout
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        Response:
        {
            "message": "Successfully logged out"
        }
        ```

    Note:
        Token blacklisting implementation pending.
        Client should discard token immediately.
    """
    # TODO: Implement token blacklisting with Redis
    # For now, client-side token removal is sufficient
    return {"message": "Successfully logged out"}
