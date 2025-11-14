"""
Authentication utilities for password hashing and JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.schemas import User

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email address (case-insensitive)."""
    if not db:
        return None
    # Normalize email for lookup
    email_normalized = email.lower().strip()
    return db.query(User).filter(User.email.ilike(email_normalized)).first()


def get_user_by_id(db: Session, user_id: Union[str, bytes]) -> Optional[User]:
    """Get a user by ID."""
    if not db:
        return None
    from uuid import UUID
    try:
        user_uuid = UUID(str(user_id))
        return db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, TypeError):
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_user(db: Session, email: str, password: str, name: str) -> User:
    """
    Create a new user account with secure password hashing.
    
    Args:
        db: Database session
        email: User email (will be normalized to lowercase)
        password: Plain text password (will be hashed)
        name: User's full name
        
    Returns:
        User: The created user object
        
    Raises:
        ValueError: If database unavailable or email already exists
    """
    if not db:
        raise ValueError("Database not available")
    
    # Normalize email
    email_normalized = email.lower().strip()
    
    # Validate email format
    if not email_normalized or "@" not in email_normalized:
        raise ValueError("Invalid email format")
    
    # Check if user already exists (case-insensitive)
    existing_user = get_user_by_email(db, email_normalized)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Validate password
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    
    # Hash password securely using bcrypt
    hashed_password = get_password_hash(password)
    
    # Create new user
    user = User(
        email=email_normalized,
        hashed_password=hashed_password,
        name=name.strip() if name else "",
        is_active=True,
        is_verified=False
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        # Check if it's a unique constraint violation
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise ValueError("User with this email already exists")
        raise ValueError(f"Failed to create user: {str(e)}")

