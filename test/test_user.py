from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

def test_get_user():
    response = client.get("/users/1000")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "id": 1000,
        "name": "test_user",
        "email": "test@test.com",
        "password": "test",
        "height": 166.5,
        "weight": 80,
    }


def test_get_nonexistent_user():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 999 not found"}


# test_user = User(id=1000, username="test_user", email="test@test.com", password="test", targets=[], height=166.5,
#                      weight=80)
#     test_target = Target(id=1000, user_id=1000, title="test_target", target_weight=65,
#                          end_date=datetime.date(2010, 10, 31),
#                          start_date=datetime.date(2010, 10, 1), reached=False, public=False, measurements=[])
#     test_measurement = Measurement(id=1000, target_id=1000, weight=78.5, measurement_date=datetime.date(2010, 10, 1))