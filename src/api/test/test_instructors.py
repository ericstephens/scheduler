import pytest
from fastapi.testclient import TestClient

class TestInstructorEndpoints:
    def test_create_instructor(self, client: TestClient):
        """Test creating a new instructor."""
        instructor_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "555-9876",
            "notes": "New test instructor"
        }
        
        response = client.post("/api/v1/instructors/", json=instructor_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["email"] == "jane.smith@example.com"
        assert data["active_status"] == True
        assert "id" in data
        assert "created_date" in data

    def test_create_instructor_duplicate_email(self, client: TestClient, sample_instructor):
        """Test creating instructor with duplicate email fails."""
        instructor_data = {
            "first_name": "Another",
            "last_name": "Person",
            "email": sample_instructor.email,  # Duplicate email
            "phone_number": "555-0000"
        }
        
        response = client.post("/api/v1/instructors/", json=instructor_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_instructor_invalid_email(self, client: TestClient):
        """Test creating instructor with invalid email fails."""
        instructor_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "not-an-email",
            "phone_number": "555-0000"
        }
        
        response = client.post("/api/v1/instructors/", json=instructor_data)
        
        assert response.status_code == 422

    def test_list_instructors(self, client: TestClient, sample_instructor):
        """Test listing instructors."""
        response = client.get("/api/v1/instructors/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our sample instructor is in the list
        instructor_ids = [instructor["id"] for instructor in data]
        assert sample_instructor.id in instructor_ids

    def test_list_instructors_with_filters(self, client: TestClient, sample_instructor):
        """Test listing instructors with filters."""
        # Test active only filter
        response = client.get("/api/v1/instructors/?active_only=true")
        assert response.status_code == 200
        data = response.json()
        assert all(instructor["active_status"] for instructor in data)
        
        # Test name search
        response = client.get(f"/api/v1/instructors/?name={sample_instructor.first_name}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(instructor["first_name"] == sample_instructor.first_name for instructor in data)

    def test_get_instructor(self, client: TestClient, sample_instructor):
        """Test getting a specific instructor."""
        response = client.get(f"/api/v1/instructors/{sample_instructor.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_instructor.id
        assert data["email"] == sample_instructor.email
        assert "course_ratings" in data
        assert "assignments" in data

    def test_get_instructor_not_found(self, client: TestClient):
        """Test getting non-existent instructor returns 404."""
        response = client.get("/api/v1/instructors/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_instructor(self, client: TestClient, sample_instructor):
        """Test updating an instructor."""
        update_data = {
            "first_name": "UpdatedName",
            "notes": "Updated notes"
        }
        
        response = client.put(f"/api/v1/instructors/{sample_instructor.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "UpdatedName"
        assert data["notes"] == "Updated notes"
        # Verify unchanged fields remain the same
        assert data["last_name"] == sample_instructor.last_name
        assert data["email"] == sample_instructor.email

    def test_update_instructor_not_found(self, client: TestClient):
        """Test updating non-existent instructor returns 404."""
        update_data = {"first_name": "Test"}
        
        response = client.put("/api/v1/instructors/99999", json=update_data)
        
        assert response.status_code == 404

    def test_update_instructor_status(self, client: TestClient, sample_instructor):
        """Test updating instructor active status."""
        # Deactivate instructor
        response = client.patch(f"/api/v1/instructors/{sample_instructor.id}/status?active=false")
        
        assert response.status_code == 200
        assert "inactive" in response.json()["message"].lower()
        
        # Verify status was updated
        get_response = client.get(f"/api/v1/instructors/{sample_instructor.id}")
        assert get_response.json()["active_status"] == False
        
        # Reactivate instructor
        response = client.patch(f"/api/v1/instructors/{sample_instructor.id}/status?active=true")
        
        assert response.status_code == 200
        assert "active" in response.json()["message"].lower()

    def test_get_instructor_stats(self, client: TestClient, sample_instructor):
        """Test getting instructor statistics."""
        response = client.get(f"/api/v1/instructors/{sample_instructor.id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_assignments" in data
        assert "total_course_ratings" in data
        assert "cleared_courses" in data
        assert all(isinstance(value, int) for value in data.values())

    def test_search_instructors(self, client: TestClient, sample_instructor):
        """Test advanced instructor search."""
        search_data = {
            "name": sample_instructor.first_name,
            "active_only": True
        }
        
        response = client.post("/api/v1/instructors/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify search results contain expected instructor
        instructor_ids = [instructor["id"] for instructor in data]
        assert sample_instructor.id in instructor_ids

    def test_search_instructors_by_email(self, client: TestClient, sample_instructor):
        """Test searching instructors by email."""
        search_data = {
            "email": sample_instructor.email,
            "active_only": True
        }
        
        response = client.post("/api/v1/instructors/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == sample_instructor.email

    def test_pagination(self, client: TestClient, sample_instructor):
        """Test instructor list pagination."""
        # Test with limit
        response = client.get("/api/v1/instructors/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        
        # Test with skip
        response = client.get("/api/v1/instructors/?skip=1&limit=10")
        
        assert response.status_code == 200
        # Should still return valid response even if no data