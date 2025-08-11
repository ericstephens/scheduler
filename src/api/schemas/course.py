from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CourseBase(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=200)
    course_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    duration_days: int = Field(..., ge=1, le=365)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, min_length=1, max_length=200)
    course_code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    active_status: Optional[bool] = None

class CourseResponse(CourseBase):
    id: int
    active_status: bool
    created_date: datetime

    class Config:
        from_attributes = True

class CourseSearchRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    active_only: bool = True