import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# AUTH
def test_correct_user_auth(correct_token_user):
    assert correct_token_user


def test_correct_admin_auth(correct_token_admin):
    assert correct_token_admin


def test_incorrect_auth():
    auth = client.post(
        "/token",
        data={
            "username": "wrong_cred",
            "password": "wrong_cred"
        })
    assert auth.status_code == 401
    assert auth.json() == {"detail": "Invalid username or password"}
