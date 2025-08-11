import pytest
from fastapi.testclient import TestClient

class TestCourseEndpoints:
    def test_create_course(self, client: TestClient):
        """Test creating a new course."""
        course_data = {
            "course_name": "Advanced Training",
            "course_code": "ADV201",
            "description": "Advanced training course",
            "duration_days": 3
        }
        
        response = client.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_name"] == "Advanced Training"
        assert data["course_code"] == "ADV201"
        assert data["duration_days"] == 3
        assert data["active_status"] == True
        assert "id" in data
        assert "created_date" in data

    def test_create_course_duplicate_code(self, client: TestClient, sample_course):
        """Test creating course with duplicate code fails."""
        course_data = {
            "course_name": "Different Course",
            "course_code": sample_course.course_code,  # Duplicate code
            "duration_days": 1
        }
        
        response = client.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_course_invalid_duration(self, client: TestClient):
        """Test creating course with invalid duration fails."""
        course_data = {
            "course_name": "Test Course",
            "course_code": "TEST01",
            "duration_days": 0  # Invalid duration
        }
        
        response = client.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 422

    def test_list_courses(self, client: TestClient, sample_course):
        """Test listing courses."""
        response = client.get("/api/v1/courses/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our sample course is in the list
        course_codes = [course["course_code"] for course in data]
        assert sample_course.course_code in course_codes

    def test_list_courses_active_only(self, client: TestClient, sample_course):
        """Test listing only active courses."""
        response = client.get("/api/v1/courses/?active_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(course["active_status"] for course in data)

    def test_get_course(self, client: TestClient, sample_course):
        """Test getting a specific course."""
        response = client.get(f"/api/v1/courses/{sample_course.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_course.id
        assert data["course_code"] == sample_course.course_code
        assert data["course_name"] == sample_course.course_name

    def test_get_course_by_code(self, client: TestClient, sample_course):
        """Test getting a course by code."""
        response = client.get(f"/api/v1/courses/code/{sample_course.course_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_course.id
        assert data["course_code"] == sample_course.course_code

    def test_get_course_not_found(self, client: TestClient):
        """Test getting non-existent course returns 404."""
        response = client.get("/api/v1/courses/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_course_by_code_not_found(self, client: TestClient):
        """Test getting non-existent course by code returns 404."""
        response = client.get("/api/v1/courses/code/NOTFOUND")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_course(self, client: TestClient, sample_course):
        """Test updating a course."""
        update_data = {
            "course_name": "Updated Course Name",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/courses/{sample_course.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["course_name"] == "Updated Course Name"
        assert data["description"] == "Updated description"
        # Verify unchanged fields remain the same
        assert data["course_code"] == sample_course.course_code
        assert data["duration_days"] == sample_course.duration_days

    def test_update_course_not_found(self, client: TestClient):
        """Test updating non-existent course returns 404."""
        update_data = {"course_name": "Test"}
        
        response = client.put("/api/v1/courses/99999", json=update_data)
        
        assert response.status_code == 404

    def test_update_course_status(self, client: TestClient, sample_course):
        """Test updating course active status."""
        # Deactivate course
        response = client.patch(f"/api/v1/courses/{sample_course.id}/status?active=false")
        
        assert response.status_code == 200
        assert "inactive" in response.json()["message"].lower()
        
        # Verify status was updated
        get_response = client.get(f"/api/v1/courses/{sample_course.id}")
        assert get_response.json()["active_status"] == False
        
        # Reactivate course
        response = client.patch(f"/api/v1/courses/{sample_course.id}/status?active=true")
        
        assert response.status_code == 200
        assert "active" in response.json()["message"].lower()

    def test_search_courses(self, client: TestClient, sample_course):
        """Test searching courses by name."""
        search_data = {
            "name": "basic",  # Should match "Basic Firearms Safety"
            "active_only": True
        }
        
        response = client.post("/api/v1/courses/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify search results contain expected course
        course_ids = [course["id"] for course in data]
        assert sample_course.id in course_ids

    def test_search_courses_by_code(self, client: TestClient, sample_course):
        """Test searching courses by code."""
        search_data = {
            "code": "BFS",  # Should match "BFS101"
            "active_only": True
        }
        
        response = client.post("/api/v1/courses/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Verify search results contain expected course
        course_ids = [course["id"] for course in data]
        assert sample_course.id in course_ids

    def test_search_courses_no_results(self, client: TestClient):
        """Test searching courses with no matching results."""
        search_data = {
            "name": "NonexistentCourse",
            "active_only": True
        }
        
        response = client.post("/api/v1/courses/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_pagination(self, client: TestClient, sample_course):
        """Test course list pagination."""
        # Test with limit
        response = client.get("/api/v1/courses/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        
        # Test with skip
        response = client.get("/api/v1/courses/?skip=1&limit=10")
        
        assert response.status_code == 200

    def test_create_course_minimal_data(self, client: TestClient):
        """Test creating course with minimal required data."""
        course_data = {
            "course_name": "Minimal Course",
            "course_code": "MIN001",
            "duration_days": 1
        }
        
        response = client.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_name"] == "Minimal Course"
        assert data["course_code"] == "MIN001"
        assert data["duration_days"] == 1
        assert data["description"] is None