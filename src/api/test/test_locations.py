import pytest
from fastapi.testclient import TestClient

class TestLocationEndpoints:
    def test_create_location(self, client: TestClient):
        """Test creating a new location."""
        location_data = {
            "location_name": "Main Training Center",
            "address": "123 Main Street",
            "city": "Springfield",
            "state_province": "IL",
            "postal_code": "62701",
            "notes": "Primary training facility with full conference room setup"
        }
        
        response = client.post("/api/v1/locations/", json=location_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["location_name"] == "Main Training Center"
        assert data["address"] == "123 Main Street"
        assert data["city"] == "Springfield"
        assert data["state_province"] == "IL"
        assert data["postal_code"] == "62701"
        assert data["notes"] == "Primary training facility with full conference room setup"
        assert data["active_status"] == True
        assert "id" in data

    def test_create_location_minimal_data(self, client: TestClient):
        """Test creating location with only required fields."""
        location_data = {
            "location_name": "Minimal Location"
        }
        
        response = client.post("/api/v1/locations/", json=location_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["location_name"] == "Minimal Location"
        assert data["address"] is None
        assert data["city"] is None
        assert data["state_province"] is None
        assert data["postal_code"] is None
        assert data["notes"] is None
        assert data["active_status"] == True
        assert "id" in data

    def test_create_location_missing_name(self, client: TestClient):
        """Test creating location without required name fails."""
        location_data = {
            "address": "123 Test St"
        }
        
        response = client.post("/api/v1/locations/", json=location_data)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("location_name" in str(error) for error in error_detail)

    def test_list_locations(self, client: TestClient, sample_location):
        """Test listing all locations."""
        response = client.get("/api/v1/locations/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that our sample location is in the list
        location_names = [loc["location_name"] for loc in data]
        assert sample_location.location_name in location_names

    def test_list_locations_with_filters(self, client: TestClient, sample_location):
        """Test listing locations with active_only filter."""
        # Test active only (default)
        response = client.get("/api/v1/locations/?active_only=true")
        assert response.status_code == 200
        active_locations = response.json()
        assert all(loc["active_status"] for loc in active_locations)
        
        # Test all locations
        response = client.get("/api/v1/locations/?active_only=false")
        assert response.status_code == 200
        all_locations = response.json()
        assert len(all_locations) >= len(active_locations)

    def test_list_locations_pagination(self, client: TestClient):
        """Test location list pagination."""
        # Test skip and limit
        response = client.get("/api/v1/locations/?skip=0&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1

    def test_get_location_by_id(self, client: TestClient, sample_location):
        """Test retrieving a specific location by ID."""
        response = client.get(f"/api/v1/locations/{sample_location.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_location.id
        assert data["location_name"] == sample_location.location_name
        assert data["address"] == sample_location.address
        assert data["active_status"] == sample_location.active_status

    def test_get_nonexistent_location(self, client: TestClient):
        """Test retrieving non-existent location returns 404."""
        response = client.get("/api/v1/locations/99999")
        
        assert response.status_code == 404
        assert "Location not found" in response.json()["detail"]

    def test_update_location(self, client: TestClient, sample_location):
        """Test updating a location."""
        update_data = {
            "location_name": "Updated Training Center",
            "address": "456 Updated Street",
            "city": "New Springfield",
            "state_province": "OH",
            "postal_code": "45503",
            "notes": "Updated facility with enhanced capabilities"
        }
        
        response = client.put(f"/api/v1/locations/{sample_location.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_location.id
        assert data["location_name"] == "Updated Training Center"
        assert data["address"] == "456 Updated Street"
        assert data["city"] == "New Springfield"
        assert data["state_province"] == "OH"
        assert data["postal_code"] == "45503"
        assert data["notes"] == "Updated facility with enhanced capabilities"

    def test_update_location_partial(self, client: TestClient, sample_location):
        """Test partial update of location."""
        update_data = {
            "location_name": "Partially Updated Location"
        }
        
        response = client.put(f"/api/v1/locations/{sample_location.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_location.id
        assert data["location_name"] == "Partially Updated Location"
        # Other fields should remain unchanged
        assert data["address"] == sample_location.address
        assert data["city"] == sample_location.city

    def test_update_nonexistent_location(self, client: TestClient):
        """Test updating non-existent location returns 404."""
        update_data = {
            "location_name": "Non-existent Location"
        }
        
        response = client.put("/api/v1/locations/99999", json=update_data)
        
        assert response.status_code == 404
        assert "Location not found" in response.json()["detail"]

    def test_update_location_status(self, client: TestClient, sample_location):
        """Test updating location active status."""
        # Deactivate location
        response = client.patch(f"/api/v1/locations/{sample_location.id}/status?active=false")
        
        assert response.status_code == 200
        data = response.json()
        assert "status updated to inactive" in data["message"]
        
        # Verify location is deactivated
        response = client.get(f"/api/v1/locations/{sample_location.id}")
        assert response.status_code == 200
        location_data = response.json()
        assert location_data["active_status"] == False
        
        # Reactivate location
        response = client.patch(f"/api/v1/locations/{sample_location.id}/status?active=true")
        
        assert response.status_code == 200
        data = response.json()
        assert "status updated to active" in data["message"]
        
        # Verify location is reactivated
        response = client.get(f"/api/v1/locations/{sample_location.id}")
        assert response.status_code == 200
        location_data = response.json()
        assert location_data["active_status"] == True

    def test_update_status_nonexistent_location(self, client: TestClient):
        """Test updating status of non-existent location returns 404."""
        response = client.patch("/api/v1/locations/99999/status?active=false")
        
        assert response.status_code == 404
        assert "Location not found" in response.json()["detail"]

    def test_search_locations_by_name(self, client: TestClient, sample_location):
        """Test searching locations by name."""
        search_data = {
            "name": "Training",
            "active_only": True
        }
        
        response = client.post("/api/v1/locations/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned locations should contain "Training" in the name
        for location in data:
            assert "training" in location["location_name"].lower()

    def test_search_locations_by_city(self, client: TestClient):
        """Test searching locations by city."""
        # First create a location with a specific city
        location_data = {
            "location_name": "City Test Location",
            "city": "TestCity"
        }
        create_response = client.post("/api/v1/locations/", json=location_data)
        assert create_response.status_code == 201
        
        # Search for locations in that city
        search_data = {
            "city": "TestCity",
            "active_only": True
        }
        
        response = client.post("/api/v1/locations/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # All returned locations should be in TestCity
        for location in data:
            assert location["city"] and "testcity" in location["city"].lower()

    def test_search_locations_empty_results(self, client: TestClient):
        """Test search with no matching results."""
        search_data = {
            "name": "NonExistentLocationName12345",
            "active_only": True
        }
        
        response = client.post("/api/v1/locations/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_locations_inactive_only(self, client: TestClient, sample_location):
        """Test searching inactive locations only."""
        # First deactivate the sample location
        client.patch(f"/api/v1/locations/{sample_location.id}/status?active=false")
        
        # Search for inactive locations
        search_data = {
            "active_only": False
        }
        
        response = client.post("/api/v1/locations/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include both active and inactive locations
        active_statuses = [loc["active_status"] for loc in data]
        assert True in active_statuses or False in active_statuses