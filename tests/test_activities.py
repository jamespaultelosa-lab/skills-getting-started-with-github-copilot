"""
FastAPI Tests for Mergington High School Activities API

Tests use the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions
- Act: Perform the action being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client: TestClient, reset_activities):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Response status is 200
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client: TestClient, reset_activities):
        """
        Arrange: Activities are loaded in the app
        Act: Make GET request to /activities
        Assert: Response contains all activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert len(activities) >= 3
    
    def test_get_activities_returns_activity_details(self, client: TestClient, reset_activities):
        """
        Arrange: Activities with specific structure are loaded
        Act: Make GET request to /activities
        Assert: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_returns_participants_list(self, client: TestClient, reset_activities):
        """
        Arrange: Activities have participants
        Act: Make GET request to /activities
        Assert: Participants are returned as a list
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert isinstance(chess_club["participants"], list)
        assert len(chess_club["participants"]) > 0


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_returns_200(self, client: TestClient, reset_activities):
        """
        Arrange: Activity exists and student email is provided
        Act: POST to /activities/{activity}/signup
        Assert: Response status is 200
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self, client: TestClient, reset_activities):
        """
        Arrange: Activity exists
        Act: POST signup request
        Assert: Response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client: TestClient, reset_activities):
        """
        Arrange: Get initial participant count
        Act: POST signup request
        Assert: Participant is added to the activity
        """
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - verify participant was added
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert email in final_response.json()[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client: TestClient, reset_activities):
        """
        Arrange: Activity does not exist
        Act: POST signup for nonexistent activity
        Assert: Response status is 404
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_twice_returns_400(self, client: TestClient, reset_activities):
        """
        Arrange: Student signs up for activity once
        Act: Student tries to sign up for same activity again
        Assert: Response status is 400 (Bad Request)
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "newstudent@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestDeleteParticipant:
    """Tests for the DELETE /activities/{activity_name}/delete endpoint."""
    
    def test_delete_participant_returns_200(self, client: TestClient, reset_activities):
        """
        Arrange: Activity and participant exist
        Act: DELETE request to remove participant
        Assert: Response status is 200
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/delete",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_delete_returns_success_message(self, client: TestClient, reset_activities):
        """
        Arrange: Participant exists in activity
        Act: DELETE request
        Assert: Response contains success message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/delete",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_delete_removes_participant_from_activity(self, client: TestClient, reset_activities):
        """
        Arrange: Get initial participant list
        Act: DELETE request to remove participant
        Assert: Participant is removed from activity
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Known participant
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        assert email in initial_response.json()[activity_name]["participants"]
        
        # Act
        client.delete(
            f"/activities/{activity_name}/delete",
            params={"email": email}
        )
        
        # Assert - verify participant was removed
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert email not in final_response.json()[activity_name]["participants"]
    
    def test_delete_from_nonexistent_activity_returns_404(self, client: TestClient, reset_activities):
        """
        Arrange: Activity does not exist
        Act: DELETE request for nonexistent activity
        Assert: Response status is 404
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/delete",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_nonexistent_participant_returns_404(self, client: TestClient, reset_activities):
        """
        Arrange: Participant does not exist in activity
        Act: DELETE request for nonexistent participant
        Assert: Response status is 404
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/delete",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
