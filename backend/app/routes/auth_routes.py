"""
Authentication API routes
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.schemas import User
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    decode_access_token,
    get_user_by_id,
)

router = APIRouter()
security = HTTPBearer()


# Request/Response Models
class SignupRequest(BaseModel):
    """User registration request model."""
    name: str
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """User registration request model (alias for SignupRequest)."""
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response model."""
    token: str
    user: UserResponse


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        token = credentials.credentials
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account (signup).
    
    Args:
        request: Signup request with name, email, and password
        db: Database session
        
    Returns:
        AuthResponse: JWT token and user information
        
    Raises:
        HTTPException: 400 if validation fails, 409 if email already exists, 503 if database unavailable
    """
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    # Validate password length
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Validate name
    if not request.name or len(request.name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be at least 2 characters long"
        )
    
    try:
        # Create user (includes email uniqueness check)
        user = create_user(
            db=db,
            email=request.email.lower().strip(),  # Normalize email
            password=request.password,
            name=request.name.strip()
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return AuthResponse(
            token=access_token,
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at
            )
        )
    
    except ValueError as e:
        # Check if it's an email uniqueness error
        error_msg = str(e).lower()
        if "already exists" in error_msg or "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error during signup: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account. Please try again later."
        )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account (alias for /signup for backward compatibility).
    
    This endpoint is kept for backward compatibility. Use /signup instead.
    """
    signup_request = SignupRequest(
        name=request.name,
        email=request.email,
        password=request.password
    )
    return await signup(signup_request, db)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        AuthResponse: JWT token and user information
        
    Raises:
        HTTPException: 401 if credentials are invalid, 503 if database unavailable
    """
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    # Normalize email
    email = request.email.lower().strip()
    
    # Authenticate user
    user = authenticate_user(db, email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    try:
        user.last_login = datetime.utcnow()
        db.commit()
    except Exception:
        # If update fails, continue anyway - not critical
        db.rollback()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AuthResponse(
        token=access_token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from token)
        
    Returns:
        UserResponse: User information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )

