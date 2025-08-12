import pytest
from datetime import date
from fastapi.testclient import TestClient

class TestSessionEndpoints:
    def test_create_course_session(self, client: TestClient, sample_course):
        """Test creating a new course session."""
        session_data = {
            "course_id": sample_course.id,
            "session_name": "JavaScript Fundamentals - Fall 2024",
            "start_date": "2025-09-15",
            "end_date": "2025-09-17",
            "notes": "Beginner-friendly introduction to JavaScript programming"
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_name"] == "JavaScript Fundamentals - Fall 2024"
        assert data["course_id"] == sample_course.id
        assert data["start_date"] == "2025-09-15"
        assert data["end_date"] == "2025-09-17"
        assert data["notes"] == "Beginner-friendly introduction to JavaScript programming"
        assert data["status"] == "scheduled"
        assert "id" in data

    def test_create_session_with_invalid_course(self, client: TestClient):
        """Test creating session with non-existent course fails."""
        session_data = {
            "course_id": 99999,  # Non-existent course
            "session_name": "Test Session",
            "start_date": "2025-09-15",
            "end_date": "2025-09-17"
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]

    def test_create_session_invalid_dates(self, client: TestClient, sample_course):
        """Test creating session with invalid date range fails."""
        session_data = {
            "course_id": sample_course.id,
            "session_name": "Invalid Date Session",
            "start_date": "2025-09-17",
            "end_date": "2025-09-15"  # End date before start date
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == 400
        assert "Invalid session dates" in response.json()["detail"]

    def test_create_session_minimal_data(self, client: TestClient, sample_course):
        """Test creating session with minimal required data."""
        session_data = {
            "course_id": sample_course.id,
            "session_name": "Minimal Session",
            "start_date": "2025-10-01",
            "end_date": "2025-10-01"
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_name"] == "Minimal Session"
        assert data["course_id"] == sample_course.id
        assert data["notes"] is None
        assert data["status"] == "scheduled"

    def test_list_sessions(self, client: TestClient, sample_session):
        """Test listing sessions."""
        response = client.get("/api/v1/sessions/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our sample session is in the list
        session_ids = [session["id"] for session in data]
        assert sample_session.id in session_ids

    def test_list_sessions_by_status(self, client: TestClient, sample_session):
        """Test listing sessions filtered by status."""
        response = client.get("/api/v1/sessions/?status=scheduled")
        
        assert response.status_code == 200
        data = response.json()
        assert all(session["status"] == "scheduled" for session in data)

    def test_list_sessions_by_course_id(self, client: TestClient, sample_course, sample_session):
        """Test listing sessions filtered by course ID."""
        response = client.get(f"/api/v1/sessions/?course_id={sample_course.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert all(session["course_id"] == sample_course.id for session in data)

    def test_get_session(self, client: TestClient, sample_session):
        """Test getting a specific session."""
        response = client.get(f"/api/v1/sessions/{sample_session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_session.id
        assert data["session_name"] == sample_session.session_name
        assert data["course_id"] == sample_session.course_id

    def test_get_session_not_found(self, client: TestClient):
        """Test getting non-existent session returns 404."""
        response = client.get("/api/v1/sessions/99999")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_update_session(self, client: TestClient, sample_session):
        """Test updating a session."""
        update_data = {
            "session_name": "Updated Session Name",
            "notes": "Updated session notes"
        }
        
        response = client.put(f"/api/v1/sessions/{sample_session.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_name"] == "Updated Session Name"
        assert data["notes"] == "Updated session notes"
        # Verify unchanged fields remain the same
        assert data["course_id"] == sample_session.course_id
        assert data["start_date"] == "2025-12-01"
        assert data["end_date"] == "2025-12-03"

    def test_update_session_not_found(self, client: TestClient):
        """Test updating non-existent session returns 404."""
        update_data = {"session_name": "Test"}
        
        response = client.put("/api/v1/sessions/99999", json=update_data)
        
        assert response.status_code == 404

    def test_update_session_status(self, client: TestClient, sample_session):
        """Test updating session status."""
        # Start session (scheduled -> in_progress)
        response = client.patch(f"/api/v1/sessions/{sample_session.id}/status?status=in_progress")
        
        assert response.status_code == 200
        assert "in_progress" in response.json()["message"]
        
        # Verify status was updated
        get_response = client.get(f"/api/v1/sessions/{sample_session.id}")
        assert get_response.json()["status"] == "in_progress"
        
        # Complete session (in_progress -> completed)
        response = client.patch(f"/api/v1/sessions/{sample_session.id}/status?status=completed")
        
        assert response.status_code == 200
        assert "completed" in response.json()["message"]

    def test_search_sessions(self, client: TestClient, sample_course, sample_session):
        """Test searching sessions."""
        search_data = {
            "course_id": sample_course.id,
            "status": "scheduled"
        }
        
        response = client.post("/api/v1/sessions/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify search results
        for session in data:
            assert session["course_id"] == sample_course.id
            assert session["status"] == "scheduled"

    def test_search_sessions_by_date_range(self, client: TestClient, sample_session):
        """Test searching sessions by date range."""
        search_data = {
            "start_date_from": "2025-01-01",
            "start_date_to": "2025-12-31"
        }
        
        response = client.post("/api/v1/sessions/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all sessions are within date range
        for session in data:
            session_start = session["start_date"]
            assert "2025-01-01" <= session_start <= "2025-12-31"

    def test_get_session_days_empty(self, client: TestClient, sample_session):
        """Test getting session days for a session with no days."""
        response = client.get(f"/api/v1/sessions/{sample_session.id}/days")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_session_days_not_found(self, client: TestClient):
        """Test getting session days for non-existent session."""
        response = client.get("/api/v1/sessions/99999/days")
        
        assert response.status_code == 404

    def test_pagination(self, client: TestClient, sample_session):
        """Test session list pagination."""
        # Test with limit
        response = client.get("/api/v1/sessions/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        
        # Test with skip
        response = client.get("/api/v1/sessions/?skip=1&limit=10")
        
        assert response.status_code == 200

    def test_create_session_with_same_dates(self, client: TestClient, sample_course):
        """Test creating session where start and end date are the same (single day)."""
        session_data = {
            "course_id": sample_course.id,
            "session_name": "Single Day Workshop",
            "start_date": "2025-11-15",
            "end_date": "2025-11-15"
        }
        
        response = client.post("/api/v1/sessions/", json=session_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["start_date"] == "2025-11-15"
        assert data["end_date"] == "2025-11-15"

    def test_update_session_dates_validation(self, client: TestClient, sample_session):
        """Test updating session with invalid date range fails."""
        update_data = {
            "start_date": "2025-12-31",
            "end_date": "2025-01-01"  # End before start
        }
        
        response = client.put(f"/api/v1/sessions/{sample_session.id}", json=update_data)
        
        assert response.status_code == 400
        assert "Invalid session dates" in response.json()["detail"]