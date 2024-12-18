import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


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
            "username": "admin@test.com",
            "password": "admin"
        })
    access_token = auth.json().get("access_token")
    assert auth.status_code == 200
    return access_token


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


def test_correct_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_correct_get_user_me(correct_token_user):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {correct_token_user}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_admin"
    assert data["email"] == "admin@test.com"


def test_incorrect_get_user_me():
    response = client.get("/users/me")
    assert response.status_code == 401


def test_correct_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    data: dict = response.json()
    data_to_ensure = {
        "id": 1,
        "role_id": 1,
        "username": "test_admin",
        "email": "admin@test.com",
    }

    assert data.items() >= data_to_ensure.items()
    assert data["targets"] is not None


def test_incorrect_get_user_404():
    response = client.get("/users/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999999 not found"}


def test_correct_create_user():
    new_user = {
        "username": "test_new_user",
        "email": "test_new_user@test.com",
        "password": "<PASSWORD>",
        "height": 280,
        "weight": 500,
    }

    response = client.post("/users", json=new_user)

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["username"] == "test_new_user"
    assert data["email"] == "test_new_user@test.com"
    assert data["role_id"] == 3

# TODO: Add duplication - user exists
# TODO: Add not all required fields filled - user exists
