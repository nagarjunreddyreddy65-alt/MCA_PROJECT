"""Test suite for sample_app.auth module."""

import pytest
from sample_app.auth import AuthService


@pytest.fixture
def auth_service():
    service = AuthService()
    service.register("alice", "password123", role="admin")
    service.register("bob", "secret456", role="developer")
    return service


def test_register_success(auth_service):
    res = auth_service.register("charlie", "mypassword")
    assert res["username"] == "charlie"
    assert res["status"] == "created"


def test_register_duplicate_fails(auth_service):
    with pytest.raises(ValueError):
        auth_service.register("alice", "anotherpass")


def test_register_empty_credentials(auth_service):
    with pytest.raises(ValueError):
        auth_service.register("", "pass")


def test_authenticate_valid_credentials(auth_service):
    token = auth_service.authenticate("alice", "password123")
    assert token is not None
    assert token.startswith("tok_alice_")


def test_authenticate_invalid_password(auth_service):
    token = auth_service.authenticate("alice", "wrongpassword")
    assert token is None


def test_authenticate_nonexistent_user(auth_service):
    token = auth_service.authenticate("unknown_user", "pass")
    assert token is None


def test_verify_valid_token(auth_service):
    token = auth_service.authenticate("bob", "secret456")
    username = auth_service.verify_token(token)
    assert username == "bob"


def test_deactivate_user(auth_service):
    auth_service.deactivate_user("bob")
    token = auth_service.authenticate("bob", "secret456")
    assert token is None
