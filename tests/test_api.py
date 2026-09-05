import main
import pytest
from DB import DBWorker
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    previous_database = main.database
    main.database = DBWorker(tmp_path / "test.db")
    with TestClient(main.app) as test_client:
        yield test_client
    main.database.close()
    main.database = previous_database


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_read_schedule(client):
    create_response = client.post(
        "/schedule",
        json={
            "name": "Vitamin D",
            "uuid": 42,
            "time_format": "hours",
            "repeats_value": 12,
            "duration": 10,
        },
    )

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "created"

    schedules_response = client.get("/schedules", params={"user_id": 42})
    assert schedules_response.status_code == 200
    assert schedules_response.json()["Vitamin D"]["repeat_time_minutes"] == 720
    assert schedules_response.json()["Vitamin D"]["repeats"] == 10


def test_rejects_invalid_duration(client):
    response = client.post(
        "/schedule",
        json={
            "name": "Vitamin D",
            "uuid": 42,
            "time_format": "hours",
            "repeats_value": 12,
            "duration": 0,
        },
    )

    assert response.status_code == 422

