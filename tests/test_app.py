"""
Tests for the Mergington High School Activities API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }

    yield

    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_contains_required_fields(self, client):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing '{field}' in {activity_name}"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_student_email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_registration(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_participant = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_participant}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        registered_student = "michael@mergington.edu"  # Currently registered

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": registered_student}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert registered_student not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        # Arrange
        activity_name = "Chess Club"
        unregistered_student = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": unregistered_student}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not registered for this activity"


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        # Arrange
        expected_redirect_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_location

