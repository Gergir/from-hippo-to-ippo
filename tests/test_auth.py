import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Fixtures
@pytest.fixture()
def correct_token_admin():
    auth = client.post(
        "/token",
        data={
            "username": "admin@test.com",
            "password": "admin"
        })
    access_token = auth.json().get("access_token")
    assert auth.status_code == 200
    return access_token


@pytest.fixture()
def correct_token_user():
    auth = client.post(
        "/token",
        data={
            "username": "user@test.com",
            "password": "user"
        })
    access_token = auth.json().get("access_token")
    assert auth.status_code == 200
    return access_token


# AUTH
def test_correct_auth(correct_token_user):
    assert correct_token_user


def test_incorrect_auth():
    auth = client.post(
        "/token",
        data={
            "username": "wrong_cred",
            "password": "wrong_cred"
        })
    assert auth.status_code == 401
    assert auth.json() == {"detail": "Invalid username or password"}
