# tests/test_security.py
"""
Tests for security utilities.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
from app.core.config import settings
from datetime import timedelta





def test_password_hash():
    """Test password hashing and verification"""
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_token_payload_content():
    """Test that created token includes all expected data in the payload"""
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data)
    payload = verify_token(token)
    assert payload["sub"] == "testuser"
    assert payload["role"] == "admin"
    assert "exp" in payload  # Expiration exists

def test_create_token():
    """Test JWT token creation and verification"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None

    # Verify token
    payload = verify_token(token)
    assert payload["sub"] == "testuser"


def test_token_expiration():
    """Test JWT token expiration by creating an expired token(-1 minutes ago) and
     check that verify_token raise an error """
    data = {"sub": "testuser"}
    # creates a token that is already expired by setting expiration to -1 minutes:
    token = create_access_token(data, expires_delta=timedelta(minutes=-1))
    # 'verify_token' should raise InvalidTokenError becase the token is expired:
    with pytest.raises(InvalidTokenError):
        verify_token(token)

def test_invalid_token_signature():
    """Test token with invalid signature"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    # change last the char of token to invalidate its signature
    invalid_token = token[:-1] + ('1' if token[-1] != '1' else '2')
    with pytest.raises(InvalidTokenError):
        verify_token(invalid_token)

def test_incorrect_token():
    """Test for verify_token with completely incorrect token"""
    with pytest.raises(InvalidTokenError):
        verify_token("not.a.token")

def test_empty_token_data():
    """Test creating token with empty data"""
    with pytest.raises(ValueError):
        create_access_token({})  # Empty data should raise error
