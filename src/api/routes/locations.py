from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import LocationRepository
from ..schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse, LocationSearchRequest
)

router = APIRouter()

def get_location_repo(db: Session = Depends(get_db_session)) -> LocationRepository:
    return LocationRepository(db)

@router.post("/", response_model=LocationResponse, status_code=201)
async def create_location(
    location: LocationCreate,
    repo: LocationRepository = Depends(get_location_repo)
):
    """Create a new location."""
    try:
        db_location = repo.create(
            location_name=location.location_name,
            address=location.address,
            city=location.city,
            state_province=location.state_province,
            postal_code=location.postal_code,
            location_type=location.location_type,
            capacity=location.capacity,
            notes=location.notes
        )
        return db_location
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[LocationResponse])
async def list_locations(
    active_only: bool = Query(True, description="Filter active locations only"),
    location_type: Optional[str] = Query(None, description="Filter by location type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    repo: LocationRepository = Depends(get_location_repo)
):
    """List all locations with optional filtering."""
    locations = repo.get_all(active_only)
    
    # Filter by type if provided
    if location_type:
        locations = [loc for loc in locations 
                    if loc.location_type and location_type.lower() in loc.location_type.lower()]
    
    # Apply pagination
    return locations[skip:skip + limit]

@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    repo: LocationRepository = Depends(get_location_repo)
):
    """Get a specific location by ID."""
    location = repo.get_by_id(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location_update: LocationUpdate,
    repo: LocationRepository = Depends(get_location_repo)
):
    """Update a location."""
    db_location = repo.get_by_id(location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Update fields that are provided
    update_data = location_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    try:
        return repo.update(db_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{location_id}/status")
async def update_location_status(
    location_id: int,
    active: bool,
    repo: LocationRepository = Depends(get_location_repo)
):
    """Update location active status."""
    location = repo.set_active_status(location_id, active)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {"message": f"Location status updated to {'active' if active else 'inactive'}"}

@router.post("/search", response_model=List[LocationResponse])
async def search_locations(
    search_request: LocationSearchRequest,
    repo: LocationRepository = Depends(get_location_repo)
):
    """Advanced search for locations."""
    locations = repo.get_all(search_request.active_only)
    
    # Filter by name if provided
    if search_request.name:
        name_lower = search_request.name.lower()
        locations = [loc for loc in locations if name_lower in loc.location_name.lower()]
    
    # Filter by city if provided
    if search_request.city:
        city_lower = search_request.city.lower()
        locations = [loc for loc in locations 
                    if loc.city and city_lower in loc.city.lower()]
    
    # Filter by type if provided
    if search_request.location_type:
        type_lower = search_request.location_type.lower()
        locations = [loc for loc in locations 
                    if loc.location_type and type_lower in loc.location_type.lower()]
    
    return locations