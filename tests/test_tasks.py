# tests/test_tasks.py
"""
Tests for task management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from .test_auth import setup_db, override_get_db  # Reuse auth test fixtures

client = TestClient(app)


def get_api_url(path: str) -> str:
    """Get full API URL for given path"""
    return f"{settings.API_V1_STR}{path}"


def test_create_task(setup_db):
    """Test creating a new task"""
    # First register and login a user
    register_response = client.post(
        get_api_url("/register"),
        json={
            "username": "taskuser",
            "password": "TestPass123"
        }
    )
    assert register_response.status_code == 200

    # Login to get token
    login_response = client.post(
        get_api_url("/login"),
        data={
            "username": "taskuser",
            "password": "TestPass123",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {"description": "Test task"}
    response = client.post(
        get_api_url("/tasks"),
        json=task_data,
        headers=headers
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test task"
    assert data["completed"] is False
    assert "id" in data
    assert "user_id" in data


def test_create_task_unauthorized():
    """Test creating a task without authentication"""
    task_data = {"description": "Test task"}
    response = client.post(
        get_api_url("/tasks"),
        json=task_data
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_create_task_empty_description():
    """Test creating a task with empty description"""
    # First register and login a user
    register_response = client.post(
        get_api_url("/register"),
        json={
            "username": "taskuser2",
            "password": "TestPass123"
        }
    )
    assert register_response.status_code == 200

    # Login to get token
    login_response = client.post(
        get_api_url("/login"),
        data={
            "username": "taskuser2",
            "password": "TestPass123",
            "grant_type": "password"
        }
    )
    token = login_response.json()["access_token"]

    # Try to create a task with empty description
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {"description": ""}
    response = client.post(
        get_api_url("/tasks"),
        json=task_data,
        headers=headers
    )

    # Verify response
    assert response.status_code == 422  # Validation error
