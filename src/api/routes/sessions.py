from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import SessionRepository, CourseRepository, LocationRepository
from src.database.models import SessionStatus, SessionDay
from src.database.utils import validate_session_dates, validate_session_times
from ..schemas.session import (
    CourseSessionCreate, CourseSessionUpdate, CourseSessionResponse,
    SessionDayCreate, SessionDayUpdate, SessionDayResponse,
    SessionSearchRequest, SessionStatus as APISessionStatus
)

router = APIRouter()

def get_session_repo(db: Session = Depends(get_db_session)) -> SessionRepository:
    return SessionRepository(db)

@router.post("/", response_model=CourseSessionResponse, status_code=201)
async def create_session(
    session: CourseSessionCreate,
    repo: SessionRepository = Depends(get_session_repo),
    db: Session = Depends(get_db_session)
):
    """Create a new class session."""
    
    # Verify course exists
    course_repo = CourseRepository(db)
    if not course_repo.get_by_id(session.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Validate dates
    if not validate_session_dates(session.start_date, session.end_date):
        raise HTTPException(status_code=400, detail="Invalid session dates")
    
    try:
        db_session_obj = repo.create_session(
            course_id=session.course_id,
            session_name=session.session_name,
            start_date=session.start_date,
            end_date=session.end_date,
            total_students=session.total_students,
            notes=session.notes
        )
        return db_session_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CourseSessionResponse])
async def list_sessions(
    status: APISessionStatus = Query(None, description="Filter by session status"),
    course_id: int = Query(None, description="Filter by course ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    repo: SessionRepository = Depends(get_session_repo)
):
    """List all sessions with optional filtering."""
    if status:
        # Convert API enum to database enum
        db_status = SessionStatus(status.value)
        sessions = repo.get_by_status(db_status)
    else:
        sessions = repo.get_all()
    
    # Filter by course if provided
    if course_id:
        sessions = [s for s in sessions if s.course_id == course_id]
    
    # Apply pagination
    return sessions[skip:skip + limit]

@router.get("/{session_id}", response_model=CourseSessionResponse)
async def get_session(
    session_id: int,
    repo: SessionRepository = Depends(get_session_repo)
):
    """Get a specific session by ID."""
    session = repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{session_id}", response_model=CourseSessionResponse)
async def update_session(
    session_id: int,
    session_update: CourseSessionUpdate,
    repo: SessionRepository = Depends(get_session_repo),
    db: Session = Depends(get_db_session)
):
    """Update a session."""
    db_session = repo.get_by_id(session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate dates if provided
    start_date = session_update.start_date or db_session.start_date
    end_date = session_update.end_date or db_session.end_date
    if not validate_session_dates(start_date, end_date):
        raise HTTPException(status_code=400, detail="Invalid session dates")
    
    # Update fields that are provided
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            # Convert API enum to database enum
            setattr(db_session, field, SessionStatus(value.value))
        else:
            setattr(db_session, field, value)
    
    try:
        # Note: SessionRepository doesn't have an update method, so we'll use the session directly
        # In a real implementation, you'd add this method to the repository
        db.merge(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{session_id}/status")
async def update_session_status(
    session_id: int,
    status: APISessionStatus,
    repo: SessionRepository = Depends(get_session_repo)
):
    """Update session status."""
    # Convert API enum to database enum
    db_status = SessionStatus(status.value)
    session = repo.update_status(session_id, db_status)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": f"Session status updated to {status.value}"}

@router.post("/{session_id}/days", response_model=SessionDayResponse, status_code=201)
async def create_session_day(
    session_id: int,
    session_day: SessionDayCreate,
    db: Session = Depends(get_db_session)
):
    """Create a new session day."""
    
    # Verify session exists
    session_repo = SessionRepository(db)
    if not session_repo.get_by_id(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify location exists
    location_repo = LocationRepository(db)
    if not location_repo.get_by_id(session_day.location_id):
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Validate times
    if not validate_session_times(session_day.start_time, session_day.end_time):
        raise HTTPException(status_code=400, detail="Invalid session times")
    
    try:
        from src.database.models import SessionDay, SessionType
        
        # Convert API enum to database enum
        session_type = SessionType(session_day.session_type.value)
        
        db_session_day = SessionDay(
            session_id=session_id,
            day_number=session_day.day_number,
            date=session_day.date,
            location_id=session_day.location_id,
            start_time=session_day.start_time,
            end_time=session_day.end_time,
            session_type=session_type
        )
        
        db.add(db_session_day)
        db.commit()
        db.refresh(db_session_day)
        
        return db_session_day
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/days", response_model=List[SessionDayResponse])
async def get_session_days(
    session_id: int,
    db: Session = Depends(get_db_session)
):
    """Get all days for a specific session."""
    
    # Verify session exists
    session_repo = SessionRepository(db)
    if not session_repo.get_by_id(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_days = db.query(SessionDay).filter(SessionDay.session_id == session_id).all()
    return session_days

@router.post("/search", response_model=List[CourseSessionResponse])
async def search_sessions(
    search_request: SessionSearchRequest,
    repo: SessionRepository = Depends(get_session_repo)
):
    """Advanced search for sessions."""
    if search_request.status:
        # Convert API enum to database enum
        db_status = SessionStatus(search_request.status.value)
        sessions = repo.get_by_status(db_status)
    else:
        sessions = repo.get_all()
    
    # Filter by course if provided
    if search_request.course_id:
        sessions = [s for s in sessions if s.course_id == search_request.course_id]
    
    # Filter by date range if provided
    if search_request.start_date_from:
        sessions = [s for s in sessions if s.start_date >= search_request.start_date_from]
    
    if search_request.start_date_to:
        sessions = [s for s in sessions if s.start_date <= search_request.start_date_to]
    
    return sessions