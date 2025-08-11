from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import get_db_session
from src.database.repository import AssignmentRepository, InstructorRepository
from src.database.models import AssignmentStatus, SessionDay, SessionType
from src.database.utils import (
    check_instructor_availability, calculate_pay_eligibility,
    get_instructor_conflicts
)
from ..schemas.assignment import (
    InstructorAssignmentCreate, InstructorAssignmentUpdate, 
    InstructorAssignmentResponse, BulkAssignmentCreate,
    AssignmentConflictCheck, AssignmentStatus as APIAssignmentStatus
)

router = APIRouter()

def get_assignment_repo(db: Session = Depends(get_db_session)) -> AssignmentRepository:
    return AssignmentRepository(db)

@router.post("/", response_model=InstructorAssignmentResponse, status_code=201)
async def create_assignment(
    assignment: InstructorAssignmentCreate,
    repo: AssignmentRepository = Depends(get_assignment_repo),
    db: Session = Depends(get_db_session)
):
    """Create a new instructor assignment."""
    
    # Verify instructor exists
    instructor_repo = InstructorRepository(db)
    instructor = instructor_repo.get_by_id(assignment.instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Verify session day exists
    session_day = db.query(SessionDay).filter(
        SessionDay.id == assignment.session_day_id
    ).first()
    if not session_day:
        raise HTTPException(status_code=404, detail="Session day not found")
    
    # Check for conflicts
    is_available = check_instructor_availability(
        db, assignment.instructor_id, session_day.date,
        session_day.start_time, session_day.end_time
    )
    
    if not is_available:
        conflicts = get_instructor_conflicts(
            db, assignment.instructor_id, session_day.date,
            session_day.start_time, session_day.end_time
        )
        raise HTTPException(
            status_code=409, 
            detail=f"Instructor has {len(conflicts)} conflicting assignments on this date"
        )
    
    # Calculate pay eligibility
    session = db.query(SessionDay).join("session").filter(
        SessionDay.id == assignment.session_day_id
    ).first()
    pay_eligible = calculate_pay_eligibility(
        db, assignment.instructor_id, session.session.course_id
    ) if session else assignment.pay_eligible
    
    try:
        # Convert API enum to database enum
        assignment_type = SessionType(assignment.assignment_type.value)
        
        db_assignment = repo.create_assignment(
            session_day_id=assignment.session_day_id,
            instructor_id=assignment.instructor_id,
            assignment_type=assignment_type,
            pay_eligible=pay_eligible,
            notes=assignment.notes
        )
        return db_assignment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[InstructorAssignmentResponse])
async def list_assignments(
    instructor_id: int = Query(None, description="Filter by instructor ID"),
    status: APIAssignmentStatus = Query(None, description="Filter by assignment status"),
    pay_eligible_only: bool = Query(False, description="Filter pay eligible assignments only"),
    date_from: date = Query(None, description="Filter assignments from this date"),
    date_to: date = Query(None, description="Filter assignments to this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    repo: AssignmentRepository = Depends(get_assignment_repo)
):
    """List all assignments with optional filtering."""
    if pay_eligible_only:
        assignments = repo.get_pay_eligible_assignments()
    elif instructor_id:
        assignments = repo.get_instructor_assignments(instructor_id)
    elif date_from and date_to:
        assignments = repo.get_assignments_by_date_range(date_from, date_to)
    else:
        # Get all assignments - you'd need to implement this method
        assignments = []  # Placeholder
    
    # Filter by status if provided
    if status:
        db_status = AssignmentStatus(status.value)
        assignments = [a for a in assignments if a.assignment_status == db_status]
    
    # Apply pagination
    return assignments[skip:skip + limit]

@router.get("/{assignment_id}", response_model=InstructorAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    repo: AssignmentRepository = Depends(get_assignment_repo)
):
    """Get a specific assignment by ID."""
    assignment = repo.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.put("/{assignment_id}", response_model=InstructorAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: InstructorAssignmentUpdate,
    repo: AssignmentRepository = Depends(get_assignment_repo),
    db: Session = Depends(get_db_session)
):
    """Update an assignment."""
    
    db_assignment = repo.get_by_id(assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Update fields that are provided
    update_data = assignment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "assignment_status" and value:
            # Convert API enum to database enum
            setattr(db_assignment, field, AssignmentStatus(value.value))
        elif field == "assignment_type" and value:
            # Convert API enum to database enum
            setattr(db_assignment, field, SessionType(value.value))
        else:
            setattr(db_assignment, field, value)
    
    try:
        # Note: You'd need to implement an update method in AssignmentRepository
        # For now, we'll use the session directly
        db.merge(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{assignment_id}/status")
async def update_assignment_status(
    assignment_id: int,
    status: APIAssignmentStatus,
    repo: AssignmentRepository = Depends(get_assignment_repo)
):
    """Update assignment status."""
    # Convert API enum to database enum
    db_status = AssignmentStatus(status.value)
    assignment = repo.update_status(assignment_id, db_status)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return {"message": f"Assignment status updated to {status.value}"}

@router.post("/bulk", response_model=List[InstructorAssignmentResponse])
async def create_bulk_assignments(
    bulk_assignment: BulkAssignmentCreate,
    repo: AssignmentRepository = Depends(get_assignment_repo),
    db: Session = Depends(get_db_session)
):
    """Create multiple assignments for an instructor across multiple session days."""
    
    # Verify instructor exists
    instructor_repo = InstructorRepository(db)
    instructor = instructor_repo.get_by_id(bulk_assignment.instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Verify all session days exist
    session_days = db.query(SessionDay).filter(
        SessionDay.id.in_(bulk_assignment.session_day_ids)
    ).all()
    
    if len(session_days) != len(bulk_assignment.session_day_ids):
        raise HTTPException(status_code=404, detail="One or more session days not found")
    
    # Check for conflicts on each day
    conflicts = []
    for session_day in session_days:
        if not check_instructor_availability(
            db, bulk_assignment.instructor_id, session_day.date,
            session_day.start_time, session_day.end_time
        ):
            conflicts.append(session_day.id)
    
    if conflicts:
        raise HTTPException(
            status_code=409,
            detail=f"Instructor has conflicts on session days: {conflicts}"
        )
    
    try:
        # Convert API enum to database enum
        assignment_type = SessionType(bulk_assignment.assignment_type.value)
        
        created_assignments = []
        for session_day in session_days:
            # Calculate pay eligibility for each assignment
            pay_eligible = calculate_pay_eligibility(
                db, bulk_assignment.instructor_id, session_day.session.course_id
            )
            
            assignment = repo.create_assignment(
                session_day_id=session_day.id,
                instructor_id=bulk_assignment.instructor_id,
                assignment_type=assignment_type,
                pay_eligible=pay_eligible,
                notes=bulk_assignment.notes
            )
            created_assignments.append(assignment)
        
        return created_assignments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-conflicts", response_model=dict)
async def check_assignment_conflicts(
    conflict_check: AssignmentConflictCheck,
    db: Session = Depends(get_db_session)
):
    """Check if an instructor has conflicts for a specific session day."""
    
    # Verify instructor exists
    instructor_repo = InstructorRepository(db)
    if not instructor_repo.get_by_id(conflict_check.instructor_id):
        raise HTTPException(status_code=404, detail="Instructor not found")
    
    # Verify session day exists
    session_day = db.query(SessionDay).filter(
        SessionDay.id == conflict_check.session_day_id
    ).first()
    if not session_day:
        raise HTTPException(status_code=404, detail="Session day not found")
    
    # Check for conflicts
    conflicts = get_instructor_conflicts(
        db, conflict_check.instructor_id, session_day.date,
        session_day.start_time, session_day.end_time
    )
    
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicting_assignment_ids": [c.id for c in conflicts]
    }