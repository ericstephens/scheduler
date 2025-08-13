import pytest
from fastapi.testclient import TestClient
from datetime import date, time

class TestSessionDayEndpoints:
    def test_create_session_day(self, client: TestClient, sample_session, sample_location):
        """Test creating a new session day."""
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-08-15",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == sample_session.id
        assert data["day_number"] == 1
        assert data["date"] == "2024-08-15"
        assert data["location_id"] == sample_location.id
        assert data["start_time"] == "09:00:00"
        assert data["end_time"] == "17:00:00"
        assert data["session_type"] == "full_day"
        assert "id" in data

    def test_create_half_day_session_day(self, client: TestClient, sample_session, sample_location):
        """Test creating a half-day session day."""
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-08-20",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "13:00:00",
            "session_type": "half_day"
        }
        
        response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_type"] == "half_day"
        assert data["start_time"] == "09:00:00"
        assert data["end_time"] == "13:00:00"

    def test_create_session_day_invalid_session(self, client: TestClient, sample_location):
        """Test creating session day with invalid session ID."""
        session_day_data = {
            "session_id": 99999,
            "day_number": 1,
            "date": "2024-08-15",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        response = client.post("/api/v1/sessions/99999/days", json=session_day_data)
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_create_session_day_invalid_location(self, client: TestClient, sample_session):
        """Test creating session day with invalid location ID."""
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-08-15",
            "location_id": 99999,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        assert response.status_code == 404
        assert "Location not found" in response.json()["detail"]

    def test_create_session_day_invalid_times(self, client: TestClient, sample_session, sample_location):
        """Test creating session day with invalid times."""
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-08-15",
            "location_id": sample_location.id,
            "start_time": "17:00:00",  # End time before start time
            "end_time": "09:00:00",
            "session_type": "full_day"
        }
        
        response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        assert response.status_code == 400
        assert "Invalid session times" in response.json()["detail"]

    def test_get_session_days(self, client: TestClient, sample_session, sample_location):
        """Test retrieving all session days for a session."""
        # Create multiple session days
        for i in range(3):
            session_day_data = {
                "session_id": sample_session.id,
                "day_number": i + 1,
                "date": f"2024-09-{5 + i:02d}",
                "location_id": sample_location.id,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "session_type": "full_day"
            }
            client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        response = client.get(f"/api/v1/sessions/{sample_session.id}/days")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Should be ordered by day_number
        assert data[0]["day_number"] == 1
        assert data[1]["day_number"] == 2
        assert data[2]["day_number"] == 3

    def test_get_session_days_invalid_session(self, client: TestClient):
        """Test retrieving session days for invalid session."""
        response = client.get("/api/v1/sessions/99999/days")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_get_session_day_by_id(self, client: TestClient, sample_session, sample_location):
        """Test retrieving a specific session day by ID."""
        # Create a session day
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-09-15",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        create_response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        created_day = create_response.json()
        
        response = client.get(f"/api/v1/sessions/session-days/{created_day['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_day["id"]
        assert data["session_id"] == sample_session.id
        assert data["day_number"] == 1

    def test_get_session_day_not_found(self, client: TestClient):
        """Test retrieving non-existent session day."""
        response = client.get("/api/v1/sessions/session-days/99999")
        
        assert response.status_code == 404
        assert "Session day not found" in response.json()["detail"]

    def test_update_session_day(self, client: TestClient, sample_session, sample_location):
        """Test updating a session day."""
        # Create a session day
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-10-01",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        create_response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        created_day = create_response.json()
        
        # Update the session day
        update_data = {
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "session_type": "half_day"
        }
        
        response = client.put(f"/api/v1/sessions/session-days/{created_day['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["start_time"] == "08:00:00"
        assert data["end_time"] == "16:00:00"
        assert data["session_type"] == "half_day"
        assert data["id"] == created_day["id"]

    def test_update_session_day_not_found(self, client: TestClient):
        """Test updating non-existent session day."""
        update_data = {
            "start_time": "08:00:00"
        }
        
        response = client.put("/api/v1/sessions/session-days/99999", json=update_data)
        
        assert response.status_code == 404
        assert "Session day not found" in response.json()["detail"]

    def test_update_session_day_invalid_location(self, client: TestClient, sample_session, sample_location):
        """Test updating session day with invalid location."""
        # Create a session day
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-10-05",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        create_response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        created_day = create_response.json()
        
        # Update with invalid location
        update_data = {
            "location_id": 99999
        }
        
        response = client.put(f"/api/v1/sessions/session-days/{created_day['id']}", json=update_data)
        
        assert response.status_code == 404
        assert "Location not found" in response.json()["detail"]

    def test_update_session_day_invalid_times(self, client: TestClient, sample_session, sample_location):
        """Test updating session day with invalid times."""
        # Create a session day
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-10-10",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        create_response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        created_day = create_response.json()
        
        # Update with invalid times
        update_data = {
            "start_time": "18:00:00",  # End time before start time
            "end_time": "09:00:00"
        }
        
        response = client.put(f"/api/v1/sessions/session-days/{created_day['id']}", json=update_data)
        
        assert response.status_code == 400
        assert "Invalid session times" in response.json()["detail"]

    def test_delete_session_day(self, client: TestClient, sample_session, sample_location):
        """Test deleting a session day."""
        # Create a session day
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2024-11-01",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        
        create_response = client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        created_day = create_response.json()
        
        # Delete the session day
        response = client.delete(f"/api/v1/sessions/session-days/{created_day['id']}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/sessions/session-days/{created_day['id']}")
        assert get_response.status_code == 404

    def test_delete_session_day_not_found(self, client: TestClient):
        """Test deleting non-existent session day."""
        response = client.delete("/api/v1/sessions/session-days/99999")
        
        assert response.status_code == 404
        assert "Session day not found" in response.json()["detail"]

    def test_list_all_session_days(self, client: TestClient, sample_session, sample_location):
        """Test listing all session days."""
        # Create multiple session days
        for i in range(3):
            session_day_data = {
                "session_id": sample_session.id,
                "day_number": i + 1,
                "date": f"2024-12-{10 + i:02d}",
                "location_id": sample_location.id,
                "start_time": f"{9 + i}:00:00",
                "end_time": f"{17 + i}:00:00",
                "session_type": "full_day"
            }
            client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        response = client.get("/api/v1/sessions/session-days")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_list_session_days_date_filter(self, client: TestClient, sample_session, sample_location):
        """Test listing session days with date range filter."""
        # Create session days in different dates
        dates = ["2024-12-15", "2024-12-20", "2024-12-25"]
        for i, date_str in enumerate(dates):
            session_day_data = {
                "session_id": sample_session.id,
                "day_number": i + 1,
                "date": date_str,
                "location_id": sample_location.id,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "session_type": "full_day"
            }
            client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        # Filter by date range
        response = client.get("/api/v1/sessions/session-days?start_date=2024-12-18&end_date=2024-12-30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only include days in the date range
        for session_day in data:
            if session_day["session_id"] == sample_session.id:
                assert session_day["date"] >= "2024-12-18"
                assert session_day["date"] <= "2024-12-30"

    def test_list_session_days_location_filter(self, client: TestClient, sample_session, sample_location):
        """Test listing session days with location filter."""
        # Create a session day first
        session_day_data = {
            "session_id": sample_session.id,
            "day_number": 1,
            "date": "2025-01-15",
            "location_id": sample_location.id,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "session_type": "full_day"
        }
        client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        response = client.get(f"/api/v1/sessions/session-days?location_id={sample_location.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned session days should be for the specified location
        for session_day in data:
            if session_day.get("session_id") == sample_session.id:
                assert session_day["location_id"] == sample_location.id

    def test_pagination(self, client: TestClient, sample_session, sample_location):
        """Test session day list pagination."""
        # Create multiple session days
        for i in range(5):
            session_day_data = {
                "session_id": sample_session.id,
                "day_number": i + 1,
                "date": f"2025-01-{10 + i:02d}",
                "location_id": sample_location.id,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "session_type": "full_day"
            }
            client.post(f"/api/v1/sessions/{sample_session.id}/days", json=session_day_data)
        
        # Test with limit
        response = client.get("/api/v1/sessions/session-days?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        
        # Test with skip
        response = client.get("/api/v1/sessions/session-days?skip=2&limit=3")
        
        assert response.status_code == 200