import pytest
from fastapi.testclient import TestClient
from httpx import Response
from main import app
from models import RoleType
from tests import correct_token_admin, correct_token_user

client = TestClient(app)


@pytest.fixture()
def valid_methods_and_endpoints() -> list[tuple[str, str]]:
    """Used to test all endpoints for incorrect authentication and authorization."""
    return [
        ("get", "/roles/"),
        ("get", "/roles/1"),
        ("get", "/roles/name/admin"),
        ("post", "/roles/"),
        ("patch", "/roles/1"),
        ("delete", "/roles/1")
    ]


@pytest.fixture()
def valid_role_tester() -> dict[str, str]:
    return {"role_type": RoleType.tester.value}  # "tester"


@pytest.fixture()
def valid_role_subscriber() -> dict[str, str]:
    return {"role_type": RoleType.subscriber.value}  # "subscriber"


@pytest.fixture()
def temporary_tester_role(correct_token_admin, valid_role_tester) -> dict:
    """Create 'tester' role for testing and delete it after test."""
    response = client.post("/roles/", json=valid_role_tester,
                           headers={"Authorization": f"Bearer {correct_token_admin}"})
    role = response.json()  # data
    yield role

    client.delete(f"/roles/{role['id']}", headers={"Authorization": f"Bearer {correct_token_admin}"})


# General
def test_incorrect_all_endpoints_not_authenticated(make_request, valid_methods_and_endpoints):
    endpoints = valid_methods_and_endpoints
    for endpoint in endpoints:
        response: Response = make_request(method=endpoint[0], url=endpoint[1])
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_all_endpoints_non_admin_user_not_authorized(
        correct_token_user,
        make_request,
        valid_methods_and_endpoints
):
    endpoints = valid_methods_and_endpoints
    for endpoint in endpoints:
        response = make_request(method=endpoint[0], url=endpoint[1], token=correct_token_user)
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


# GET
def test_correct_get_all_roles(correct_token_admin):
    response = client.get("/roles/", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_correct_get_role(correct_token_admin):
    response = client.get("/roles/1", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["role_type"] == "admin"


def test_incorrect_get_role_not_found(correct_token_admin):
    response = client.get("/roles/999999", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Role with id 999999 not found"}


def test_correct_get_role_by_name(correct_token_admin):
    response = client.get("/roles/name/admin", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["role_type"] == "admin"


def test_incorrect_get_role_by_name_not_found(correct_token_admin):
    response = client.get("/roles/name/nonexistent", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Role with role type nonexistent not found"}


# POST
def test_correct_create_role(temporary_tester_role, correct_token_admin):
    data = temporary_tester_role
    assert data["role_type"] == "tester"


def test_incorrect_create_role_already_exists(temporary_tester_role, valid_role_tester, correct_token_admin):
    assert temporary_tester_role["role_type"] == "tester"
    response = client.post("/roles/", json=valid_role_tester,
                           headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Role with role type tester already exists"}


def test_incorrect_create_role_non_valid_enum(correct_token_admin):
    response = client.post("/roles/", json={"role_type": "nonexistent"},
                           headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["type"] == "enum"  # error type
    expected_message = "Input should be 'premium', 'admin', 'user', 'tester' or 'subscriber'"
    assert data["detail"][0]["msg"] == expected_message


# PATCH
def test_correct_update_role(temporary_tester_role, correct_token_admin, valid_role_subscriber):
    assert temporary_tester_role["role_type"] == "tester"

    # Perform update
    response = client.patch(
        f"/roles/{temporary_tester_role['id']}",
        json=valid_role_subscriber,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["role_type"] == "subscriber"


def test_incorrect_update_role_not_found(correct_token_admin, valid_role_tester):
    response = client.patch("/roles/999999", json=valid_role_tester,
                            headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Role with id 999999 not found"}


def test_incorrect_update_role_non_valid_enum(correct_token_admin):
    response = client.patch("/roles/1", json={"role_type": "nonexistent"},
                            headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["type"] == "enum"  # error type
    expected_message = "Input should be 'premium', 'admin', 'user', 'tester' or 'subscriber'"
    assert data["detail"][0]["msg"] == expected_message


# DELETE
def test_correct_delete_role(temporary_tester_role, correct_token_admin):
    role_id = temporary_tester_role["id"]
    response = client.delete(f"/roles/{role_id}", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 200
    assert response.json() == {"message": f"Role type tester with id {role_id} deleted successfully"}


def test_incorrect_delete_role_not_found(correct_token_admin):
    response = client.delete("/roles/999999", headers={"Authorization": f"Bearer {correct_token_admin}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Role with id 999999 not found"}
