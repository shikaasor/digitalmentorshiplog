"""
Security Utilities

Functions for password hashing, JWT token generation, and authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> len(hashed) > 0
        True

    Note:
        Bcrypt has a 72-byte password limit. Longer passwords are automatically
        truncated to 72 bytes.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Bcrypt can only handle passwords up to 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    # Convert to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # Truncate password if needed (to match hash_password behavior)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Check password
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        str: Encoded JWT token

    Example:
        >>> token = create_access_token(data={"sub": "user_id_123"})
        >>> len(token) > 0
        True
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Optional[Dict]: Decoded token payload if valid, None otherwise

    Example:
        >>> token = create_access_token(data={"sub": "user_123"})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        'user_123'
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and extract the user ID.

    Args:
        token: JWT token to verify

    Returns:
        Optional[str]: User ID if token is valid, None otherwise

    Example:
        >>> token = create_access_token(data={"sub": "user_123"})
        >>> user_id = verify_token(token)
        >>> user_id
        'user_123'
    """
    payload = decode_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    return user_id
