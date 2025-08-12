from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from .session import SessionType

class AssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InstructorAssignmentBase(BaseModel):
    session_day_id: int
    instructor_id: int
    assignment_type: SessionType
    notes: Optional[str] = None

class InstructorAssignmentCreate(InstructorAssignmentBase):
    pass

class InstructorAssignmentUpdate(BaseModel):
    assignment_type: Optional[SessionType] = None
    assignment_status: Optional[AssignmentStatus] = None
    notes: Optional[str] = None

class InstructorAssignmentResponse(InstructorAssignmentBase):
    id: int
    assignment_status: AssignmentStatus
    created_date: datetime

    class Config:
        from_attributes = True

class BulkAssignmentCreate(BaseModel):
    session_day_ids: list[int]
    instructor_id: int
    assignment_type: SessionType
    notes: Optional[str] = None

class AssignmentConflictCheck(BaseModel):
    instructor_id: int
    session_day_id: int