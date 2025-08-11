from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import RatingRepository, InstructorRepository, CourseRepository
from src.database.models import RatingType
from ..schemas.rating import (
    InstructorCourseRatingCreate, InstructorCourseRatingUpdate, 
    InstructorCourseRatingResponse, BulkRatingUpdate
)

router = APIRouter()

def get_rating_repo(db: Session = Depends(get_db_session)) -> RatingRepository:
    return RatingRepository(db)

@router.post("/", response_model=InstructorCourseRatingResponse, status_code=201)
async def create_or_update_rating(
    rating: InstructorCourseRatingCreate,
    repo: RatingRepository = Depends(get_rating_repo)
):
    """Create or update an instructor course rating."""
    try:
        # Convert string enum to database enum
        rating_enum = RatingType(rating.rating.value)
        
        db_rating = repo.create_or_update_rating(
            instructor_id=rating.instructor_id,
            course_id=rating.course_id,
            rating=rating_enum,
            notes=rating.notes
        )
        return db_rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid rating value: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instructor/{instructor_id}", response_model=List[InstructorCourseRatingResponse])
async def get_instructor_ratings(
    instructor_id: int,
    repo: RatingRepository = Depends(get_rating_repo),
    db: Session = Depends(get_db_session)
):
    """Get all course ratings for a specific instructor."""
    # Verify instructor exists
    instructor_repo = InstructorRepository(db)
    if not instructor_repo.get_by_id(instructor_id):
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    ratings = repo.get_instructor_ratings(instructor_id)
    return ratings

@router.get("/course/{course_id}", response_model=List[InstructorCourseRatingResponse])
async def get_course_ratings(
    course_id: int,
    repo: RatingRepository = Depends(get_rating_repo),
    db: Session = Depends(get_db_session)
):
    """Get all instructor ratings for a specific course."""
    
    # Verify course exists
    course_repo = CourseRepository(db)
    if not course_repo.get_by_id(course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    
    ratings = repo.get_course_ratings(course_id)
    return ratings

@router.get("/instructor/{instructor_id}/course/{course_id}", response_model=InstructorCourseRatingResponse)
async def get_specific_rating(
    instructor_id: int,
    course_id: int,
    repo: RatingRepository = Depends(get_rating_repo)
):
    """Get rating for a specific instructor-course combination."""
    rating = repo.get_rating(instructor_id, course_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@router.put("/instructor/{instructor_id}/course/{course_id}", response_model=InstructorCourseRatingResponse)
async def update_rating(
    instructor_id: int,
    course_id: int,
    rating_update: InstructorCourseRatingUpdate,
    repo: RatingRepository = Depends(get_rating_repo)
):
    """Update a specific instructor course rating."""
    existing_rating = repo.get_rating(instructor_id, course_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    try:
        # Update rating if provided
        if rating_update.rating:
            rating_enum = RatingType(rating_update.rating.value)
        else:
            rating_enum = existing_rating.rating
            
        db_rating = repo.create_or_update_rating(
            instructor_id=instructor_id,
            course_id=course_id,
            rating=rating_enum,
            notes=rating_update.notes if rating_update.notes is not None else existing_rating.notes
        )
        return db_rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid rating value: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course/{course_id}/cleared", response_model=List[int])
async def get_cleared_instructors(
    course_id: int,
    repo: RatingRepository = Depends(get_rating_repo),
    db: Session = Depends(get_db_session)
):
    """Get all instructor IDs that are cleared for a specific course."""
    
    # Verify course exists
    course_repo = CourseRepository(db)
    if not course_repo.get_by_id(course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    
    cleared_instructor_ids = repo.get_cleared_instructors_for_course(course_id)
    return cleared_instructor_ids

@router.post("/bulk-update", response_model=List[InstructorCourseRatingResponse])
async def bulk_update_ratings(
    bulk_update: BulkRatingUpdate,
    repo: RatingRepository = Depends(get_rating_repo),
    db: Session = Depends(get_db_session)
):
    """Bulk update ratings for multiple instructors on a single course."""
    
    # Verify course exists
    course_repo = CourseRepository(db)
    if not course_repo.get_by_id(bulk_update.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify all instructors exist
    instructor_repo = InstructorRepository(db)
    for instructor_id in bulk_update.instructor_ids:
        if not instructor_repo.get_by_id(instructor_id):
            raise HTTPException(status_code=404, detail=f"Instructor {instructor_id} not found")
    
    try:
        rating_enum = RatingType(bulk_update.rating.value)
        updated_ratings = []
        
        for instructor_id in bulk_update.instructor_ids:
            rating = repo.create_or_update_rating(
                instructor_id=instructor_id,
                course_id=bulk_update.course_id,
                rating=rating_enum,
                notes=bulk_update.notes
            )
            updated_ratings.append(rating)
        
        return updated_ratings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid rating value: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))