# tests/test_schemas/test_token.py
"""
Tests for token schemas validation.
"""
import pytest
from pydantic import ValidationError
from app.schemas.token import Token, TokenData


def test_token_schema():
    """Test Token schema validation"""
    # Test valid token
    token = Token(access_token="some-token", token_type="bearer")
    assert token.access_token == "some-token"
    assert token.token_type == "bearer"

    # Test case insensitive token type
    token = Token(access_token="some-token", token_type="Bearer")
    assert token.token_type == "bearer"

    # Test invalid token type
    with pytest.raises(ValidationError):
        Token(access_token="some-token", token_type="invalid")


def test_token_data_schema():
    """Test TokenData schema validation"""
    # Test valid token data
    token_data = TokenData(username="testuser")
    assert token_data.username == "testuser"

    # Test optional username
    token_data = TokenData()
    assert token_data.username is None

    # Test empty username validation
    with pytest.raises(ValidationError):
        TokenData(username="   ")
