from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

BASE_ACTIVITIES = deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = set(BASE_ACTIVITIES.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == expected_activity_names
    assert data["Chess Club"]["description"] == BASE_ACTIVITIES["Chess Club"]["description"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    original_count = len(activities[activity_name]["participants"])
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(path, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert len(activities[activity_name]["participants"]) == original_count + 1
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = BASE_ACTIVITIES[activity_name]["participants"][0]
    path = f"/activities/{quote(activity_name)}/signup"
    original_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(path, params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert len(activities[activity_name]["participants"]) == original_count


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = BASE_ACTIVITIES[activity_name]["participants"][0]
    original_count = len(activities[activity_name]["participants"])
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.delete(path, params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert len(activities[activity_name]["participants"]) == original_count - 1
    assert participant_email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.delete(path, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
