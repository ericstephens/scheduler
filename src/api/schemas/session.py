from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionType(str, Enum):
    HALF_DAY = "half_day"
    FULL_DAY = "full_day"

class ClassSessionBase(BaseModel):
    course_id: int
    session_name: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    total_students: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None

class ClassSessionCreate(ClassSessionBase):
    pass

class ClassSessionUpdate(BaseModel):
    session_name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SessionStatus] = None
    total_students: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None

class ClassSessionResponse(ClassSessionBase):
    id: int
    status: SessionStatus

    class Config:
        from_attributes = True

class SessionDayBase(BaseModel):
    session_id: int
    day_number: int = Field(..., ge=1)
    date: date
    location_id: int
    start_time: time
    end_time: time
    session_type: SessionType

class SessionDayCreate(SessionDayBase):
    pass

class SessionDayUpdate(BaseModel):
    day_number: Optional[int] = Field(None, ge=1)
    date: Optional[date] = None
    location_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    session_type: Optional[SessionType] = None

class SessionDayResponse(SessionDayBase):
    id: int

    class Config:
        from_attributes = True

class SessionSearchRequest(BaseModel):
    course_id: Optional[int] = None
    status: Optional[SessionStatus] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    location_id: Optional[int] = None