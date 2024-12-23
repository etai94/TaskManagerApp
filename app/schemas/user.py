# app/schemas/user.py
"""
Pydantic schemas for user data validation and serialization.
"""
from pydantic import BaseModel, validator
import re

class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str

    @validator('username')
    def username_valid(cls, v):
        """Validate username format."""
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

    @validator('password')
    def password_strong(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search("[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search("[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search("[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

class User(UserBase):
    """Schema for user responses."""
    id: int

    class Config:
        """Pydantic configuration."""
        orm_mode = True  # Allows the model to read data from ORM objects 
