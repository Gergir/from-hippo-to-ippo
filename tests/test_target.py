import pytest
from datetime import date
from tests import correct_token_user, correct_token_admin
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def check_satisfied_conditions(method, new_entity, token=None):
    """
    Test set-up function that validates validation errors for target creation and updates.
    """
    incorrect_data = (
        ["ab", "string_too_short", "name"],
        ["a" * 51, "string_too_long", "name"],
        [29, "greater_than_equal", "target_weight"],
        [301, "less_than_equal", "target_weight"],
    )

    for li in incorrect_data:
        data_to_replace = li[0]
        error_type = li[1]
        field = li[2]

        if method == "patch":
            response = client.patch(
                f"/users/2/targets/1",
                json={**new_entity, field: data_to_replace},
                headers={"Authorization": f"Bearer {token}"}
            )
        else:
            response = client.post(
                f"/users/2/targets",
                json={**new_entity, field: data_to_replace},
                headers={"Authorization": f"Bearer {token}"}
            )

        data = response.json()
        assert response.status_code == 422
        assert data["detail"][0]["type"] == error_type
        assert field in data["detail"][0]["loc"]


# Fixtures
@pytest.fixture()
def valid_target():
    return {
        "name": "test_individual_target",
        "target_weight": 65.0,
        "start_date": "2010-10-01",
        "end_date": "2010-10-31",
        "public": False
    }


# GET
def test_correct_get_all_targets():
    response = client.get("/users/targets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Should have at least admin's and user's targets


def test_correct_get_my_targets(correct_token_user):
    response = client.get(
        "/users/me/targets",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least one target
    assert data[0]["name"] == "test_individual_target"


def test_incorrect_get_my_targets_unauthorized():
    response = client.get("/users/me/targets")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_correct_get_target_by_name():
    response = client.get("/users/targets/name/test_individual_target")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_individual_target"
    assert data["target_weight"] == 65.0


def test_incorrect_get_target_by_name_not_found():
    response = client.get("/users/targets/name/NonexistentTarget")
    assert response.status_code == 404


def test_correct_get_user_targets():
    response = client.get("/users/1/targets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "test_individual_target"


def test_incorrect_get_user_targets_user_not_found():
    response = client.get("/users/999999/targets")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999999 not found"}


# POST
def test_correct_create_target(correct_token_user, valid_target):
    response = client.post(
        "/users/2/targets",
        json=valid_target,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == valid_target["name"]
    assert data["target_weight"] == valid_target["target_weight"]
    assert data["user_id"] == 2
    assert not data["reached"]
    assert not data["closed"]


def test_incorrect_create_target_not_authenticated(valid_target):
    response = client.post("/users/2/targets", json=valid_target)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_create_target_not_authorized(correct_token_user, valid_target):
    response = client.post(
        "/users/1/targets",
        json=valid_target,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_create_target_fields_conditions_no_satisfied(correct_token_user, valid_target):
    check_satisfied_conditions("post", valid_target, correct_token_user)


def test_incorrect_create_target_not_all_required_fields_filled():
    new_target = {"name": "test_new_user3"}

    response = client.post("/users", json=new_target)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"


# PATCH
def test_correct_update_target_by_the_same_user(correct_token_user):
    update_data = {"name": "updated_target_name"}
    response = client.patch(
        "/users/2/targets/2",  # Using target_id=2 which belongs to user_id=2
        json=update_data,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "updated_target_name"


def test_correct_update_target_by_admin(correct_token_admin):
    update_data = {"name": "updated_target_name_by_admin"}
    response = client.patch(
        "/users/2/targets/2",
        json=update_data,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "updated_target_name_by_admin"


def test_incorrect_update_target_by_other_non_admin_user_not_authorized(correct_token_user):
    target_to_update = {
        "username": "updated_target_name_but_not_authorized",
    }

    response = client.patch(
        "/users/1/targets/1",
        json=target_to_update,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_update_target_not_found(correct_token_user):
    response = client.patch(
        "/users/2/targets/999999",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 404


def test_incorrect_update_target_not_authenticated():
    response = client.patch(
        "/users/1/targets/1",  # Trying to update admin's target
        json={"name": "Updated Name"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_update_target_not_all_field_satisfied(correct_token_user, valid_target):
    check_satisfied_conditions("patch", valid_target, correct_token_user)


# DELETE
def test_incorrect_delete_target_not_authenticated():
    response = client.delete("/users/2/targets/2")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_delete_target_by_other_non_admin_user_not_authorized(correct_token_user):
    response = client.delete(
        "/users/1/targets/1",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_delete_target_user_not_found(correct_token_admin):
    response = client.delete(
        "/users/999999/targets/1",
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Target with id 1 for user 999999 not found"}


def test_incorrect_delete_target_not_found(correct_token_user):
    response = client.delete(
        "/users/2/targets/999999",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Target with id 999999 for user 2 not found"}


def test_correct_delete_target_by_admin(correct_token_admin):
    response = client.delete(
        "/users/2/targets/2",
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Target with id 2 deleted successfully"}


def test_correct_delete_target_by_own_user(correct_token_admin):
    response = client.delete(
        "/users/1/targets/1",  # This target belongs to user_id=1, which is admin
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Target with id 1 deleted successfully"}
