from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class RatingLevel(str, Enum):
    OBSERVE = "observe"
    CO_TEACH = "co_teach" 
    CLEARED = "cleared"

class InstructorCourseRatingBase(BaseModel):
    instructor_id: int
    course_id: int
    rating: RatingLevel
    notes: Optional[str] = None

class InstructorCourseRatingCreate(InstructorCourseRatingBase):
    pass

class InstructorCourseRatingUpdate(BaseModel):
    rating: Optional[RatingLevel] = None
    notes: Optional[str] = None

class InstructorCourseRatingResponse(InstructorCourseRatingBase):
    id: int
    date_assigned: datetime
    date_updated: datetime

    class Config:
        from_attributes = True

class BulkRatingUpdate(BaseModel):
    instructor_ids: list[int]
    course_id: int
    rating: RatingLevel
    notes: Optional[str] = None