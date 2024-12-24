import pytest
from httpx import Response
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture()
def make_request():
    def _make_request(method: str, url: str, token: str | None = None) -> Response:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return getattr(client, method)(url, headers=headers) # response e.g. client.get("/users/")

    return _make_request
