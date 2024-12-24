# tests/test_auth.py
"""
Tests for authentication endpoints.
"""
import os
import pytest
import logging
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
# Import models and dependencies
from app.db.base import Base, init_database
from app.main import app
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.token import Token

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test database path and configuration
TEST_DB_PATH = "./test.db"

# Check test database path and permissions
logger.info(f"Test database path: {TEST_DB_PATH}")
try:
    test_db_dir = os.path.dirname(TEST_DB_PATH) or '.'
    if os.access(test_db_dir, os.W_OK):
        logger.info(f"Test directory {test_db_dir} is writable")
    else:
        logger.error(f"No write permission in test directory {test_db_dir}")
except Exception as e:
    logger.error(f"Error checking test directory permissions: {e}")

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Added SQL logging
)

# # Enable SQLite foreign key support
# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test client
client = TestClient(app)
# helper function to get API URL
def get_api_url(path: str) -> str:
    """Get full API URL for given path"""
    return f"{settings.API_V1_STR}{path}"

# Override the get_db dependency
def override_get_db():
    """Get test database session."""
    try:
        db = TestingSessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")  # Added error logging
        raise
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before tests and drop them after."""
    logger.info("Setting up test database...")
    logger.info(f"Registered models before creation: {Base.metadata.tables.keys()}")
    try:
        # Drop all tables if they exist
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all previous tables")
        # test  connecting to the database
        with engine.connect() as conn:
            logger.info("Successfully connected to database")

        # Create database tables in the right order ("create_all cause errors here)
        User.__table__.create(engine, checkfirst=True)
        logger.info("Created Users table")
        Task.__table__.create(engine, checkfirst=True)
        logger.info("Created Tasks table")
        app.dependency_overrides[get_db] = override_get_db
        # run the test
        yield
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")  # Added error logging
        raise
    finally:
        # drop Tables
        Base.metadata.drop_all(bind=engine)
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
            logger.info("Test database file removed")
        app.dependency_overrides.clear()
        logger.info("Test database cleanup complete")


def test_register():
    """Test user registration"""
    logger.info("Starting test_register")
    response = client.post(
        get_api_url("/register"),
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    logger.info(f"Registration response: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Response content: {response.content}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_register_existing_user():
    """Test registering an existing username"""
    # First registration
    response = client.post(
        get_api_url("/register"),
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200

    # Try to register the same username
    response = client.post(
        get_api_url("/register"),
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_login():
    """Test user login with OAuth2 form data"""
    # First register a user
    client.post(
        get_api_url("/register"),
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )

    # Login with form data
    response = client.post(
        get_api_url("/login"),
        data={  # Changed from json to form data
            "username": "testuser",
            "password": "TestPass123",
            "grant_type": "password"  # Added required OAuth2 field
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password"""
    # First register a user
    client.post(
        get_api_url("/register"),
        json={
            "username": "testuser",
            "password": "TestPass123"
        }
    )

    # Try login with wrong password
    response = client.post(
        get_api_url("/login"),
        data={
            "username": "testuser",
            "password": "wrongpass",
            "grant_type": "password"
        }
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"

def test_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    logger.info(f"inside test_invalid_token...")

    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(get_api_url("/tasks"), headers=headers)
    logger.info(f"Full response: {response.json()}")

    details_json = response.json()["detail"]
    logger.info(f"Details json is: {details_json}")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert "Could not validate credentials" in response.json()["detail"]

