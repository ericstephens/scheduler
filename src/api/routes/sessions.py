from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import SessionRepository, CourseRepository, LocationRepository, CourseSessionDayRepository
from src.database.models import SessionStatus, CourseSessionDay
from src.database.utils import validate_session_dates, validate_session_times
from ..schemas.session import (
    CourseSessionCreate, CourseSessionUpdate, CourseSessionResponse,
    CourseSessionDayCreate, CourseSessionDayUpdate, CourseSessionDayResponse,
    SessionSearchRequest, SessionStatus as APISessionStatus
)

router = APIRouter()

def get_session_repo(db: Session = Depends(get_db_session)) -> SessionRepository:
    return SessionRepository(db)

def get_session_day_repo(db: Session = Depends(get_db_session)) -> CourseSessionDayRepository:
    return CourseSessionDayRepository(db)

# Session day routes (put before parameterized routes to avoid conflicts)
@router.get("/session-days", response_model=List[CourseSessionDayResponse])
async def list_all_session_days(
    start_date: date = Query(None, description="Filter by start date"),
    end_date: date = Query(None, description="Filter by end date"),
    location_id: int = Query(None, description="Filter by location ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo)
):
    """List all session days with optional filtering."""
    if start_date and end_date:
        session_days = session_day_repo.get_by_date_range(start_date, end_date)
    elif location_id and start_date:
        session_days = session_day_repo.get_by_location_and_date(location_id, start_date)
    else:
        session_days = session_day_repo.get_all()
    
    # Apply additional filters
    if location_id and not start_date:
        session_days = [sd for sd in session_days if sd.location_id == location_id]
    
    # Apply pagination
    return session_days[skip:skip + limit]

@router.get("/session-days/{session_day_id}", response_model=CourseSessionDayResponse)
async def get_session_day(
    session_day_id: int,
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo)
):
    """Get a specific session day by ID."""
    session_day = session_day_repo.get_by_id(session_day_id)
    if not session_day:
        raise HTTPException(status_code=404, detail="Session day not found")
    return session_day

@router.put("/session-days/{session_day_id}", response_model=CourseSessionDayResponse)
async def update_session_day(
    session_day_id: int,
    session_day_update: CourseSessionDayUpdate,
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo),
    db: Session = Depends(get_db_session)
):
    """Update a session day."""
    db_session_day = session_day_repo.get_by_id(session_day_id)
    if not db_session_day:
        raise HTTPException(status_code=404, detail="Session day not found")
    
    # Validate location if provided
    if session_day_update.location_id:
        location_repo = LocationRepository(db)
        if not location_repo.get_by_id(session_day_update.location_id):
            raise HTTPException(status_code=404, detail="Location not found")
    
    # Validate times if provided
    start_time = session_day_update.start_time or db_session_day.start_time
    end_time = session_day_update.end_time or db_session_day.end_time
    if not validate_session_times(start_time, end_time):
        raise HTTPException(status_code=400, detail="Invalid session times")
    
    # Update fields that are provided
    update_data = session_day_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "session_type" and value:
            # Convert API enum to database enum
            from src.database.models import SessionType
            setattr(db_session_day, field, SessionType(value.value))
        else:
            setattr(db_session_day, field, value)
    
    try:
        updated_session_day = session_day_repo.update(db_session_day)
        return updated_session_day
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session-days/{session_day_id}")
async def delete_session_day(
    session_day_id: int,
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo)
):
    """Delete a session day."""
    success = session_day_repo.delete(session_day_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session day not found")
    
    return {"message": "Session day deleted successfully"}

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

@router.post("/{session_id}/days", response_model=CourseSessionDayResponse, status_code=201)
async def create_session_day(
    session_id: int,
    session_day: CourseSessionDayCreate,
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo),
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
        from src.database.models import SessionType
        
        # Convert API enum to database enum
        session_type = SessionType(session_day.session_type.value)
        
        db_session_day = session_day_repo.create(
            session_id=session_id,
            day_number=session_day.day_number,
            date=session_day.date,
            location_id=session_day.location_id,
            start_time=session_day.start_time,
            end_time=session_day.end_time,
            session_type=session_type
        )
        
        return db_session_day
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/days", response_model=List[CourseSessionDayResponse])
async def get_session_days(
    session_id: int,
    session_day_repo: CourseSessionDayRepository = Depends(get_session_day_repo),
    db: Session = Depends(get_db_session)
):
    """Get all days for a specific session."""
    
    # Verify session exists
    session_repo = SessionRepository(db)
    if not session_repo.get_by_id(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_days = session_day_repo.get_by_session_id(session_id)
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