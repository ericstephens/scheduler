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

class CourseSessionBase(BaseModel):
    course_id: int
    session_name: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    notes: Optional[str] = None

class CourseSessionCreate(CourseSessionBase):
    pass

class CourseSessionUpdate(BaseModel):
    session_name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SessionStatus] = None
    notes: Optional[str] = None

class CourseSessionResponse(CourseSessionBase):
    id: int
    status: SessionStatus

    class Config:
        from_attributes = True

class CourseSessionDayBase(BaseModel):
    session_id: int
    day_number: int = Field(..., ge=1)
    date: date
    location_id: int
    start_time: time
    end_time: time
    session_type: SessionType

class CourseSessionDayCreate(CourseSessionDayBase):
    pass

class CourseSessionDayUpdate(BaseModel):
    day_number: Optional[int] = Field(None, ge=1)
    date: Optional[date] = None
    location_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    session_type: Optional[SessionType] = None

class CourseSessionDayResponse(CourseSessionDayBase):
    id: int

    class Config:
        from_attributes = True

class SessionSearchRequest(BaseModel):
    course_id: Optional[int] = None
    status: Optional[SessionStatus] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    location_id: Optional[int] = None