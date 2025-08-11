from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import InstructorRepository
from src.database.utils import get_instructor_stats
from ..schemas.instructor import (
    InstructorCreate, InstructorUpdate, InstructorResponse, 
    InstructorDetailResponse, InstructorSearchRequest
)

router = APIRouter()

def get_instructor_repo(db: Session = Depends(get_db_session)) -> InstructorRepository:
    return InstructorRepository(db)

@router.post("/", response_model=InstructorResponse, status_code=201)
async def create_instructor(
    instructor: InstructorCreate,
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """Create a new instructor."""
    try:
        db_instructor = repo.create(
            first_name=instructor.first_name,
            last_name=instructor.last_name,
            email=instructor.email,
            phone_number=instructor.phone_number,
            notes=instructor.notes
        )
        return db_instructor
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[InstructorResponse])
async def list_instructors(
    active_only: bool = Query(True, description="Filter active instructors only"),
    name: Optional[str] = Query(None, description="Search by name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """List all instructors with optional filtering."""
    if name:
        instructors = repo.search_by_name(name, active_only)
    else:
        instructors = repo.get_all(active_only)
    
    # Apply pagination
    return instructors[skip:skip + limit]

@router.get("/{instructor_id}", response_model=InstructorDetailResponse)
async def get_instructor(
    instructor_id: int,
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """Get a specific instructor by ID."""
    instructor = repo.get_by_id(instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return instructor

@router.put("/{instructor_id}", response_model=InstructorResponse)
async def update_instructor(
    instructor_id: int,
    instructor_update: InstructorUpdate,
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """Update an instructor."""
    db_instructor = repo.get_by_id(instructor_id)
    if not db_instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Update fields that are provided
    update_data = instructor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_instructor, field, value)
    
    try:
        return repo.update(db_instructor)
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{instructor_id}/status")
async def update_instructor_status(
    instructor_id: int,
    active: bool,
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """Update instructor active status."""
    instructor = repo.set_active_status(instructor_id, active)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    return {"message": f"Instructor status updated to {'active' if active else 'inactive'}"}

@router.get("/{instructor_id}/stats")
async def get_instructor_statistics(
    instructor_id: int,
    db: Session = Depends(get_db_session)
):
    """Get instructor statistics."""
    # Check if instructor exists
    repo = InstructorRepository(db)
    instructor = repo.get_by_id(instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    stats = get_instructor_stats(db, instructor_id)
    return stats

@router.post("/search", response_model=List[InstructorResponse])
async def search_instructors(
    search_request: InstructorSearchRequest,
    repo: InstructorRepository = Depends(get_instructor_repo)
):
    """Advanced search for instructors."""
    if search_request.name:
        return repo.search_by_name(search_request.name, search_request.active_only)
    elif search_request.email:
        instructor = repo.get_by_email(search_request.email)
        return [instructor] if instructor else []
    else:
        return repo.get_all(search_request.active_only)