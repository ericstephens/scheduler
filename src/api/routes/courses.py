from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import CourseRepository
from ..schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseSearchRequest
)

router = APIRouter()

def get_course_repo(db: Session = Depends(get_db_session)) -> CourseRepository:
    return CourseRepository(db)

@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(
    course: CourseCreate,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Create a new course."""
    try:
        db_course = repo.create(
            course_name=course.course_name,
            course_code=course.course_code,
            description=course.description,
            duration_days=course.duration_days
        )
        return db_course
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Course code already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    active_only: bool = Query(True, description="Filter active courses only"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    repo: CourseRepository = Depends(get_course_repo)
):
    """List all courses with optional filtering."""
    courses = repo.get_all(active_only)
    
    # Apply pagination
    return courses[skip:skip + limit]

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Get a specific course by ID."""
    course = repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/code/{course_code}", response_model=CourseResponse)
async def get_course_by_code(
    course_code: str,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Get a specific course by code."""
    course = repo.get_by_code(course_code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Update a course."""
    db_course = repo.get_by_id(course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update fields that are provided
    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    try:
        return repo.update(db_course)
    except Exception as e:
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Course code already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{course_id}/status")
async def update_course_status(
    course_id: int,
    active: bool,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Update course active status."""
    course = repo.set_active_status(course_id, active)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {"message": f"Course status updated to {'active' if active else 'inactive'}"}

@router.post("/search", response_model=List[CourseResponse])
async def search_courses(
    search_request: CourseSearchRequest,
    repo: CourseRepository = Depends(get_course_repo)
):
    """Advanced search for courses."""
    courses = repo.get_all(search_request.active_only)
    
    # Filter by name if provided
    if search_request.name:
        name_lower = search_request.name.lower()
        courses = [c for c in courses if name_lower in c.course_name.lower()]
    
    # Filter by code if provided
    if search_request.code:
        code_lower = search_request.code.lower()
        courses = [c for c in courses if code_lower in c.course_code.lower()]
    
    return courses