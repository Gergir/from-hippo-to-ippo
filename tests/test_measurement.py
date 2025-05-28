import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture()
def incorrect_fields_data() -> list[tuple[str | float, str, str]]:
    return [
        (29, "greater_than_equal", "weight"),
        (501, "less_than_equal", "weight"),
    ]


@pytest.fixture()
def valid_measurement() -> dict:
    return {
        "weight": 80.5,
        "date": str(datetime.now().date()),
    }


@pytest.fixture()
def temporary_measurement(valid_measurement, correct_token_user) -> dict:
    response = client.post(
        "/users/2/targets/2/measurements/",
        json=valid_measurement,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    measurement = response.json()
    yield measurement
    client.delete(f"/users/2/targets/1/measurements/{measurement['id']}",
                  headers={"Authorization": f"Bearer {correct_token_user}"})


def check_satisfied_conditions(method, new_entity, token=None, user_id=None, target_id=None):
    """
    Test set-up function that validates validation errors for measurement creation and updates.
    """
    incorrect_data = (
        [29, "greater_than_equal", "weight"],
        [501, "less_than_equal", "weight"]
    )

    for li in incorrect_data:
        data_to_replace = li[0]
        error_type = li[1]
        field = li[2]

        if method == "patch":
            response = client.patch(
                f"/users/{user_id}/targets/{target_id}/measurements/1",
                json={**new_entity, field: data_to_replace},
                headers={"Authorization": f"Bearer {token}"}
            )
        else:
            response = client.post(
                f"/users/{user_id}/targets/{target_id}/measurements/",
                json={**new_entity, field: data_to_replace},
                headers={"Authorization": f"Bearer {token}"}
            )

        data = response.json()
        assert response.status_code == 422
        assert data["detail"][0]["type"] == error_type
        assert field in data["detail"][0]["loc"]


# GET
def test_correct_get_all_measurements():
    response = client.get("/users/targets/measurements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_correct_get_my_measurements(correct_token_user):
    response = client.get(
        "/users/me/targets/measurements",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_correct_get_my_target_measurements(correct_token_user):
    response = client.get(
        "/users/me/targets/2/measurements",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_correct_get_target_measurements():
    response = client.get("/users/1/targets/1/measurements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_correct_get_measurement():
    response = client.get("/users/1/targets/1/measurements/1")
    assert response.status_code == 200
    data = response.json()
    assert "weight" in data
    assert "measurement_date" in data


# POST
def test_correct_create_measurement(temporary_measurement, valid_measurement):
    data = temporary_measurement
    assert data["weight"] == valid_measurement["weight"]
    assert "target_id" in data


def test_incorrect_create_measurement_not_authenticated(valid_measurement):
    response = client.post("/users/2/targets/1/measurements/", json=valid_measurement)
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_create_measurement_not_authorized(valid_measurement, correct_token_user):
    response = client.post(
        "/users/1/targets/1/measurements/",
        json=valid_measurement,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_create_measurement_fields_conditions_not_satisfied(
        valid_measurement,
        incorrect_fields_data,
        make_request,
        correct_token_user
):
    for incorrect_field_entry in incorrect_fields_data:
        data_to_insert = incorrect_field_entry[0]
        error_type = incorrect_field_entry[1]
        field_to_check = incorrect_field_entry[2]
        response = make_request(
            method="post",
            url="/users/2/targets/1/measurements/",
            data={**valid_measurement, field_to_check: data_to_insert},
            token=correct_token_user
        )
        assert response.status_code == 422
        assert field_to_check in response.json()["detail"][0]["loc"]
        assert response.json()["detail"][0]["type"] == error_type


# PATCH
def test_correct_update_measurement_by_admin(temporary_measurement, correct_token_admin):
    update_data = {"weight": 80.35}
    response = client.patch(
        "/users/2/targets/1/measurements/1",
        json=update_data,
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )
    assert response.status_code == 200
    assert response.json()["weight"] == 80.35


def test_correct_update_measurement_by_the_same_user(temporary_measurement, correct_token_user):
    update_data = {"weight": 80.35}
    response = client.patch(
        "/users/2/targets/1/measurements/1",
        json=update_data,
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    assert response.json()["weight"] == 80.35


def test_incorrect_update_measurement_not_authenticated():
    response = client.patch("/users/2/targets/1/measurements/1", json={"weight": 82.5})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_update_measurement_not_authorized(correct_token_user):
    response = client.patch(
        "/users/1/targets/1/measurements/1",
        json={"weight": 82.5},
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden, you lack privileges for this action"}


def test_incorrect_update_measurement_not_found(correct_token_user):
    response = client.patch(
        "/users/2/targets/1/measurements/999999",
        json={"weight": 82.5},
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Measurement with id 999999 not found"}


def test_incorrect_update_measurement_fields_conditions_not_satisfied(
        temporary_measurement,
        incorrect_fields_data,
        make_request,
        correct_token_admin
):
    for incorrect_field_entry in incorrect_fields_data:
        data_to_insert = incorrect_field_entry[0]
        error_type = incorrect_field_entry[1]
        field_to_check = incorrect_field_entry[2]
        response = make_request(
            method="patch",
            url=f"/users/2/targets/1/measurements/{temporary_measurement['id']}",
            data={field_to_check: data_to_insert},
            token=correct_token_admin
        )
        assert response.status_code == 422
        assert field_to_check in response.json()["detail"][0]["loc"]
        assert response.json()["detail"][0]["type"] == error_type


# DELETE Tests
def test_correct_delete_measurement_by_admin(temporary_measurement, correct_token_admin):
    response = client.delete(
        f"/users/2/targets/1/measurements/{temporary_measurement['id']}",
        headers={"Authorization": f"Bearer {correct_token_admin}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == f"Measurement with id {temporary_measurement['id']} deleted successfully"


def test_correct_delete_measurement_by_the_same_user(temporary_measurement, correct_token_user):
    response = client.delete(
        f"/users/2/targets/1/measurements/{temporary_measurement['id']}",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == f"Measurement with id {temporary_measurement['id']} deleted successfully"


def test_incorrect_delete_measurement_not_found(correct_token_user):
    response = client.delete(
        "/users/2/targets/1/measurements/999999",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Measurement with id 999999 not found"}


def test_incorrect_delete_measurement_not_authenticated():
    response = client.delete("/users/2/targets/1/measurements/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_incorrect_delete_measurement_not_authorized(correct_token_user):
    response = client.delete(
        "/users/1/targets/1/measurements/1",
        headers={"Authorization": f"Bearer {correct_token_user}"}
    )
    assert response.status_code == 403
