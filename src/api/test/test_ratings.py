import pytest
from fastapi.testclient import TestClient

class TestRatingEndpoints:
    def test_create_rating(self, client: TestClient, sample_instructor, sample_course):
        """Test creating a new instructor course rating."""
        rating_data = {
            "instructor_id": sample_instructor.id,
            "course_id": sample_course.id,
            "rating": "cleared",
            "notes": "Instructor is fully qualified"
        }
        
        response = client.post("/api/v1/ratings/", json=rating_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["instructor_id"] == sample_instructor.id
        assert data["course_id"] == sample_course.id
        assert data["rating"] == "cleared"
        assert data["notes"] == "Instructor is fully qualified"
        assert "id" in data
        assert "date_assigned" in data
        assert "date_updated" in data

    def test_create_rating_invalid_level(self, client: TestClient, sample_instructor, sample_course):
        """Test creating rating with invalid rating level fails."""
        rating_data = {
            "instructor_id": sample_instructor.id,
            "course_id": sample_course.id,
            "rating": "invalid_level",
            "notes": "Test"
        }
        
        response = client.post("/api/v1/ratings/", json=rating_data)
        
        assert response.status_code == 422

    def test_update_existing_rating(self, client: TestClient, sample_rating):
        """Test updating an existing rating."""
        # First create a rating, then update it
        update_data = {
            "instructor_id": sample_rating.instructor_id,
            "course_id": sample_rating.course_id,
            "rating": "co_teach",
            "notes": "Updated to co-teach level"
        }
        
        response = client.post("/api/v1/ratings/", json=update_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == "co_teach"
        assert data["notes"] == "Updated to co-teach level"

    def test_get_instructor_ratings(self, client: TestClient, sample_rating):
        """Test getting all ratings for an instructor."""
        response = client.get(f"/api/v1/ratings/instructor/{sample_rating.instructor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify our rating is in the results
        rating_ids = [rating["id"] for rating in data]
        assert sample_rating.id in rating_ids

    def test_get_instructor_ratings_not_found(self, client: TestClient):
        """Test getting ratings for non-existent instructor."""
        response = client.get("/api/v1/ratings/instructor/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_course_ratings(self, client: TestClient, sample_rating):
        """Test getting all ratings for a course."""
        response = client.get(f"/api/v1/ratings/course/{sample_rating.course_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify our rating is in the results
        rating_ids = [rating["id"] for rating in data]
        assert sample_rating.id in rating_ids

    def test_get_course_ratings_not_found(self, client: TestClient):
        """Test getting ratings for non-existent course."""
        response = client.get("/api/v1/ratings/course/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_specific_rating(self, client: TestClient, sample_rating):
        """Test getting a specific instructor-course rating."""
        response = client.get(
            f"/api/v1/ratings/instructor/{sample_rating.instructor_id}/course/{sample_rating.course_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_rating.id
        assert data["instructor_id"] == sample_rating.instructor_id
        assert data["course_id"] == sample_rating.course_id

    def test_get_specific_rating_not_found(self, client: TestClient, sample_instructor, sample_course):
        """Test getting non-existent rating returns 404."""
        # Create a course without ratings
        new_course_data = {
            "course_name": "No Ratings Course",
            "course_code": "NRC001",
            "duration_days": 1
        }
        course_response = client.post("/api/v1/courses/", json=new_course_data)
        new_course = course_response.json()
        
        response = client.get(
            f"/api/v1/ratings/instructor/{sample_instructor.id}/course/{new_course['id']}"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_rating(self, client: TestClient, sample_rating):
        """Test updating a specific rating."""
        update_data = {
            "rating": "observe",
            "notes": "Changed to observe level"
        }
        
        response = client.put(
            f"/api/v1/ratings/instructor/{sample_rating.instructor_id}/course/{sample_rating.course_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == "observe"
        assert data["notes"] == "Changed to observe level"

    def test_update_rating_not_found(self, client: TestClient):
        """Test updating non-existent rating returns 404."""
        update_data = {
            "rating": "cleared",
            "notes": "Test"
        }
        
        response = client.put("/api/v1/ratings/instructor/99999/course/99999", json=update_data)
        
        assert response.status_code == 404

    def test_get_cleared_instructors(self, client: TestClient, sample_rating):
        """Test getting cleared instructors for a course."""
        response = client.get(f"/api/v1/ratings/course/{sample_rating.course_id}/cleared")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If the sample rating is cleared, the instructor should be in the list
        if sample_rating.rating.value == "cleared":
            assert sample_rating.instructor_id in data

    def test_get_cleared_instructors_course_not_found(self, client: TestClient):
        """Test getting cleared instructors for non-existent course."""
        response = client.get("/api/v1/ratings/course/99999/cleared")
        
        assert response.status_code == 404

    def test_bulk_update_ratings(self, client: TestClient, sample_instructor, sample_course):
        """Test bulk updating ratings for multiple instructors."""
        # Create another instructor
        instructor_data = {
            "first_name": "Bulk",
            "last_name": "Test",
            "email": "bulk@example.com",
            "phone_number": "555-0000"
        }
        instructor_response = client.post("/api/v1/instructors/", json=instructor_data)
        new_instructor = instructor_response.json()
        
        bulk_update_data = {
            "instructor_ids": [sample_instructor.id, new_instructor["id"]],
            "course_id": sample_course.id,
            "rating": "co_teach",
            "notes": "Bulk updated to co-teach"
        }
        
        response = client.post("/api/v1/ratings/bulk-update", json=bulk_update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify both instructors got the same rating
        for rating in data:
            assert rating["rating"] == "co_teach"
            assert rating["notes"] == "Bulk updated to co-teach"
            assert rating["course_id"] == sample_course.id

    def test_bulk_update_ratings_course_not_found(self, client: TestClient, sample_instructor):
        """Test bulk update with non-existent course."""
        bulk_update_data = {
            "instructor_ids": [sample_instructor.id],
            "course_id": 99999,
            "rating": "cleared"
        }
        
        response = client.post("/api/v1/ratings/bulk-update", json=bulk_update_data)
        
        assert response.status_code == 404
        assert "course" in response.json()["detail"].lower()

    def test_bulk_update_ratings_instructor_not_found(self, client: TestClient, sample_course):
        """Test bulk update with non-existent instructor."""
        bulk_update_data = {
            "instructor_ids": [99999],
            "course_id": sample_course.id,
            "rating": "cleared"
        }
        
        response = client.post("/api/v1/ratings/bulk-update", json=bulk_update_data)
        
        assert response.status_code == 404
        assert "instructor" in response.json()["detail"].lower()

    def test_rating_enum_values(self, client: TestClient, sample_instructor, sample_course):
        """Test all valid rating enum values."""
        valid_ratings = ["observe", "co_teach", "cleared"]
        
        for rating in valid_ratings:
            rating_data = {
                "instructor_id": sample_instructor.id,
                "course_id": sample_course.id,
                "rating": rating,
                "notes": f"Test {rating} rating"
            }
            
            response = client.post("/api/v1/ratings/", json=rating_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["rating"] == rating