import pytest
import httpx
from app.core.logging_utils import logger
import os



# Set test environment
os.environ["ENV"] = "test"

BASE_URL = "http://127.0.0.1:8000/api/v1"


@pytest.fixture(scope="module")
def client():
    """
    Fixture to create a client for making HTTP requests.
    This client is reused for all tests in the module.
    """
    with httpx.Client() as client:
        yield client


@pytest.fixture(scope="module")
def user_and_token(client):
    """
    Fixture to register a new user, log them in, and return user details and token.
    This fixture is used by other tests that require an authenticated user.

    Returns:
    dict: A dictionary containing user_id, username, and access token.
    """
    # Register a new user
    username = "testuser"
    password = "testpass"
    register_data = {"username": username, "password": password}
    response = client.post(f"{BASE_URL}/register", json=register_data)
    assert response.status_code == 200, "User registration failed"
    user_data = response.json()
    assert "id" in user_data and "username" in user_data, "User registration response format incorrect"

    # Login and get token
    login_data = {"username": username, "password": password}
    response = client.post(f"{BASE_URL}/login", data=login_data)
    assert response.status_code == 200, "Login failed"
    token_data = response.json()
    assert "access_token" in token_data, "Login response format incorrect"
    return {"user_id": user_data["id"], "username": username, "token": token_data["access_token"]}


def test_register(client):
    """
    Test user registration functionality.

    This test attempts to register a new user and checks if the registration is successful
    and if the response contains the expected user data.
    """
    register_data = {"username": "newuser2", "password": "TestPass123"}
    logger.info(f"Registration data: {register_data}")

    reg_route = f"{BASE_URL}/register"
    logger.info(f"Registration route: -{reg_route}-")

    response = client.post(reg_route, json=register_data)
    if response.status_code != 200:
        logger.error(f"Response content: {response.content}")
    assert response.status_code == 200, "User registration failed"
    data = response.json()
    assert "id" in data and "username" in data, "User registration response format incorrect"



def test_login(client, user_and_token):
    """
    Test user login functionality.

    This test attempts to log in with the credentials of a previously registered user
    and checks if the login is successful and returns an access token.
    """
    login_data = {"username": user_and_token["username"], "password": "testpass"}
    response = client.post(f"{BASE_URL}/login", data=login_data)
    assert response.status_code == 200, "Login failed"
    data = response.json()
    assert "access_token" in data, "Login response format incorrect"


def test_create_task(client, user_and_token):
    """
    Test task creation functionality.

    This test attempts to create a new task for an authenticated user and checks
    if the task is created successfully with the correct details.
    """
    headers = {"Authorization": f"Bearer {user_and_token['token']}"}
    task_data = {"description": "Test task"}
    response = client.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    assert response.status_code == 200, f"Failed to create task, got {response.status_code}"
    data = response.json()
    assert all(
        key in data for key in ["id", "description", "completed", "user_id"]), "Task creation response format incorrect"
    assert data["description"] == "Test task"
    assert data["completed"] == False
    assert data["user_id"] == user_and_token["user_id"]


def test_get_tasks(client, user_and_token):
    """
    Test retrieval of tasks for an authenticated user.

    This test attempts to retrieve all tasks for an authenticated user and checks
    if the response is a list of tasks with the correct format.
    """
    headers = {"Authorization": f"Bearer {user_and_token['token']}"}
    response = client.get(f"{BASE_URL}/tasks", headers=headers)
    assert response.status_code == 200, "Failed to retrieve tasks"
    tasks = response.json()
    assert isinstance(tasks, list), "Tasks response should be a list"
    assert len(tasks) > 0, "No tasks found"
    for task in tasks:
        assert all(
            key in task for key in ["id", "description", "completed", "user_id"]), "Task response format incorrect"


def test_update_task(client, user_and_token):
    """
    Test task update functionality.

    This test attempts to update an existing task for an authenticated user and checks
    if the task is updated successfully with the new details.
    """
    headers = {"Authorization": f"Bearer {user_and_token['token']}"}
    # Get the first task
    response = client.get(f"{BASE_URL}/tasks", headers=headers)
    tasks = response.json()
    task_id = tasks[0]['id']

    # Update the task
    updated_task = {"description": "Updated test task", "completed": True}
    response = client.put(f"{BASE_URL}/tasks/{task_id}", json=updated_task, headers=headers)
    assert response.status_code == 200, "Failed to update task"
    data = response.json()
    assert data["description"] == "Updated test task", "Task update failed"
    assert data["completed"] is True, "Task completion status was not updated"


def test_delete_task(client, user_and_token):
    """
    Test task deletion functionality.

    This test attempts to delete an existing task for an authenticated user and checks
    if the task is deleted successfully. It also verifies that the deleted task
    no longer appears in the user's task list.
    """
    headers = {"Authorization": f"Bearer {user_and_token['token']}"}
    # Get the first task
    response = client.get(f"{BASE_URL}/tasks", headers=headers)
    tasks = response.json()
    task_id = tasks[0]['id']

    # Delete the task
    response = client.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200, "Failed to delete task"
    data = response.json()
    assert data["message"] == "Task deleted successfully", "Incorrect delete response message"

    # Verify the task was deleted
    response = client.get(f"{BASE_URL}/tasks", headers=headers)
    tasks = response.json()
    assert all(task['id'] != task_id for task in tasks), "Task was not deleted properly"
