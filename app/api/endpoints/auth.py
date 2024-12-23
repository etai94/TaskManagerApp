# app/api/endpoints/auth.py
"""
Authentication endpoints for user registration and login.
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
) -> Any:
    """
    Register a new user.

    Args:
        db: Database session
        user_in: User registration data

    Returns:
        Newly created user

    Raises:
        HTTPException: If username already exists
    """
    # Check if user exists
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login")
def login(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.

    Args:
        db: Database session
        form_data: Login credentials

    Returns:
        Dict with access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 
