from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from .rating import InstructorCourseRatingResponse
from .assignment import InstructorAssignmentResponse

class InstructorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None

class InstructorCreate(InstructorBase):
    pass

class InstructorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    active_status: Optional[bool] = None

class InstructorResponse(InstructorBase):
    id: int
    active_status: bool
    created_date: datetime

    class Config:
        from_attributes = True

class InstructorDetailResponse(InstructorResponse):
    course_ratings: List[InstructorCourseRatingResponse] = []
    assignments: List[InstructorAssignmentResponse] = []

    class Config:
        from_attributes = True

class InstructorSearchRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    active_only: bool = True
    course_id: Optional[int] = None
    rating_level: Optional[str] = None