# app/core/config.py
"""
Application configuration module.
Contains settings and configuration variables for the application.
"""
from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Task Management System"

    # Security settings
    # Generate using: openssl rand -hex 32
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    SQLITE_URL: str = "sqlite:///./sql_app.db"

    class Config:
        case_sensitive = True


# Create global settings object
settings = Settings() 
