# tests/test_auth.py
"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models and dependencies
from app.db.base_class import Base
from app.main import app
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User  # noqa
from app.models.task import Task  # noqa

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test client
client = TestClient(app)


# Override the get_db dependency
def override_get_db():
    """Get test database session."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before tests and drop them after."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Run the test
    yield

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_register():
    """Test user registration"""
    response = client.post(
        "/api/v1/register",
        json={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_existing_user():
    """Test registering an existing username"""
    # First registration
    response = client.post(
        "/api/v1/register",
        json={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 200

    # Try to register the same username
    response = client.post(
        "/api/v1/register",
        json={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 400


def test_login():
    """Test user login"""
    # Register user first
    client.post(
        "/api/v1/register",
        json={"username": "testuser", "password": "TestPass123"}
    )

    # Try to login
    response = client.post(
        "/api/v1/login",
        data={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password"""
    # Register user first
    client.post(
        "/api/v1/register",
        json={"username": "testuser", "password": "TestPass123"}
    )

    # Try to login with wrong password
    response = client.post(
        "/api/v1/login",
        data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
