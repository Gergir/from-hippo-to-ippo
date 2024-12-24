import pytest
from fastapi.testclient import TestClient
from main import app
from tests import correct_token_user, correct_token_admin

client = TestClient(app)


@pytest.fixture()
def incorrect_fields_data() -> list[tuple[str | float, str, str]]:
    """
    Return incorrect data for fields in the user model. For scenarios:
    - Username length constraints (3-50 characters)
    - Email format validation
    - Password length constraints (8-50 characters)
    - Height range validation (60-280 cm)
    - Weight range validation (30-500 kg)
    """

    return [
        ("n4", "string_too_short", "username"),
        ("a" * 51, "string_too_long", "username"),
        ("incorrect_emai@", "value_error", "email"),
        ("123", "string_too_short", "password"),
        ("a" * 51, "string_too_long", "password"),
        (59, "greater_than_equal", "height"),
        (281, "less_than_equal", "height"),
        (29, "greater_than_equal", "weight"),
        (501, "less_than_equal", "weight"),
    ]


@pytest.fixture()
def check_satisfied_conditions():
    """
    A test set-up function that validates validation errors for user creation and updates.




    """

    def _check_satisfied_conditions(method, url, new_entity, token=None):

        """
        Args:
        method (str): The HTTP method to test - either "post" for user creation
            or "patch" for user updates
        new_entity (dict): The base user data dictionary containing valid values.
            Each test case will modify one field with an invalid value
        token (str, optional): JWT token for authorization. Required only for
            patch operations. Defaults to None.

    Returns:
        None: Assertions are performed within the function

        """
        incorrect_data = incorrect_fields_data
        for li in incorrect_data:
            data_to_replace = li[0]
            error_type = li[1]
            field = li[2]
            if method == "patch":
                response = client.patch("/users/2", json={**new_entity, field: data_to_replace},
                                        headers={"Authorization": f"Bearer {token}"})
            else:
                response = client.post("/users", json={**new_entity, field: data_to_replace})
            data = response.json()
        assert response.status_code == 422
        assert data["detail"][0]["type"] == error_type
        assert field in data["detail"][0]["loc"]
    return _check_satisfied_conditions

@pytest.fixture()
def valid_user():
    return {
        "username": "test_new_user",
        "email": "test_new_user@test.com",
        "password": "<PASSWORD>",
        "height": 280,
        "weight": 500,
    }

@pytest.fixture()
def create_temporally_user(valid_user, correct_token_admin):
    response = client.post("/users", json=valid_user)
    data = response.json()
    yield data
    client.delete(f"/users/{data['id']}", headers={"Authorization": f"Bearer {correct_token_admin}"})

# GET
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
    assert data["username"] == "test_user"
    assert data["email"] == "user@test.com"


def test_incorrect_get_user_me_not_authenticated():
    response = client.get("/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


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


def test_incorrect_get_user_not_found():
    response = client.get("/users/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999999 not found"}


def test_correct_get_user_by_name():
    response = client.get("/users/name/test_user")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"
    assert data["email"] == "user@test.com"
    assert data["role_id"] == 3


def test_incorrect_get_user_by_name_not_found():
    response = client.get("/users/name/NonexistentUser")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with username NonexistentUser not found"}


# POST
def test_correct_create_user(create_temporally_user):
    data = create_temporally_user
    assert "id" in data
    assert data["username"] == "test_new_user"
    assert data["email"] == "test_new_user@test.com"
    assert data["role_id"] == 3


def test_incorrect_create_user_username_already_exists(create_temporally_user, valid_user):
    response = client.post("/users", json=valid_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this username already exists"}


def test_incorrect_create_user_email_already_exists(create_temporally_user, valid_user):
    new_user = {**valid_user, "username": "test_new_user2"} # replace username value to avoid username conflict

    response = client.post("/users", json=new_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_incorrect_create_user_not_all_required_fields_filled(valid_user):
    new_user = {"username": f"{valid_user["username"]}"}

    response = client.post("/users", json=new_user)
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"


def test_incorrect_create_user_fields_conditions_not_satisfied(valid_user, incorrect_fields_data):
    incorrect_data = incorrect_fields_data
    for
    check_satisfied_conditions("post", new_entity=valid_user)


# PATCH
def test_correct_update_user_by_the_same_user(correct_token_user):
    user_to_update = {
        "username": "test_new_user_updated",
    }

    response = client.patch(
        "/users/2",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "test_new_user_updated"


def test_correct_update_user_by_admin(correct_token_admin):
    user_to_update = {
        "username": "test_new_user_updated_by_admin",
        "email": "test_new_user@test.com"
    }

    response = client.patch(
        "/users/3",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "test_new_user_updated_by_admin"
    assert data["email"] == "test_new_user@test.com"
    assert data["role_id"] == 3


def test_incorrect_update_user_by_other_non_admin_user_not_authorized(correct_token_user):
    user_to_update = {
        "username": "test_new_user_updated_but_not_authorized",
    }

    response = client.patch(
        "/users/3",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_update_user_username_already_exists(correct_token_admin):
    user_to_update = {
        "username": "test_new_user_updated_by_admin",
    }

    response = client.patch(
        "/users/2",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this username already exists"}


def test_incorrect_update_user_email_already_exists(correct_token_user):
    user_to_update = {
        "email": "admin@test.com"
    }

    response = client.patch(
        "/users/2",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_incorrect_update_user_empty_request(correct_token_user):
    user_to_update = {}

    response = client.patch(
        "/users/2",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "No data provided"}


def test_incorrect_update_user_not_found(correct_token_admin):
    user_to_update = {
        "username": "test_new_user_updated",
    }

    response = client.patch(
        "/users/999999",
        json=user_to_update,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999999 not found"}


def test_incorrect_update_user_fields_conditions_not_satisfied(correct_token_admin):
    user_to_update = {
        "username": "test_new_user_updated",
    }

    check_satisfied_conditions("patch", new_entity=user_to_update, token=correct_token_admin)


# DELETE
def test_incorrect_delete_user_not_authenticated():
    response = client.delete("/users/2")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_delete_user_by_other_non_admin_user_not_authorized(correct_token_user):
    response = client.delete(
        "/users/3",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_delete_user_not_found(correct_token_admin):
    response = client.delete(
        "/users/999999",
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999999 not found"}


def test_correct_delete_user_with_targets_by_own_user(correct_token_user):
    response = client.delete(
        "/users/2",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"User with id 2 deleted successfully"}


# Moved to the end for sake of the deletion tests
def test_correct_delete_user_with_no_target_by_admin(correct_token_admin):
    response = client.delete(
        "/users/3",
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"User with id 3 deleted successfully"}
