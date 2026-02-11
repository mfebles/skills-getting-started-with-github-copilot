import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities_state():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_rejects_duplicate():
    activity = "Soccer Team"
    email = "test@mergington.edu"

    first = client.post(f"/activities/{activity}/signup", params={"email": email})
    second = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert first.status_code == 200
    assert second.status_code == 400


def test_remove_participant():
    activity = "Soccer Team"
    email = "remove-me@mergington.edu"

    client.post(f"/activities/{activity}/signup", params={"email": email})
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_found():
    activity = "Soccer Team"
    email = "missing@mergington.edu"

    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
