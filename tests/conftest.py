import pytest
from httpx import Response
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Shared Fixtures
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


@pytest.fixture()
def correct_token_specified_user():
    def _correct_token_specified_user(username: str, password: str):
        auth = client.post(
            "/token",
            data={
                "username": username,
                "password": password
            })
        access_token = auth.json().get("access_token")
        assert auth.status_code == 200
        return access_token

    return _correct_token_specified_user


@pytest.fixture()
def make_request():
    def _make_request(method: str, url: str, data: dict | None = None, token: str | None = None) -> Response:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        if data:
            return getattr(client, method)(url, json=data, headers=headers)
        return getattr(client, method)(url, headers=headers)  # response e.g. client.get("/users/")

    return _make_request
