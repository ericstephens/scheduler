from typing import Optional
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from .models import (
    Instructor, Course, InstructorCourseRating, SessionDay, 
    InstructorAssignment, RatingType
)
from .repository import RatingRepository

def is_instructor_cleared_for_course(db: Session, instructor_id: int, course_id: int) -> bool:
    """Check if an instructor is cleared for a specific course."""
    rating_repo = RatingRepository(db)
    rating = rating_repo.get_rating(instructor_id, course_id)
    return rating is not None and rating.rating == RatingType.CLEARED

def check_instructor_availability(db: Session, instructor_id: int, 
                                check_date: date, start_time: time, 
                                end_time: time) -> bool:
    """Check if an instructor is available on a specific date and time."""
    existing_assignments = db.query(InstructorAssignment).join(SessionDay).filter(
        InstructorAssignment.instructor_id == instructor_id,
        SessionDay.date == check_date
    ).all()
    
    for assignment in existing_assignments:
        session_day = assignment.session_day
        # Check for time overlap
        if (start_time < session_day.end_time and end_time > session_day.start_time):
            return False
    
    return True

def get_instructor_conflicts(db: Session, instructor_id: int, 
                           check_date: date, start_time: time, 
                           end_time: time) -> list[InstructorAssignment]:
    """Get all conflicting assignments for an instructor on a specific date and time."""
    existing_assignments = db.query(InstructorAssignment).join(SessionDay).filter(
        InstructorAssignment.instructor_id == instructor_id,
        SessionDay.date == check_date
    ).all()
    
    conflicts = []
    for assignment in existing_assignments:
        session_day = assignment.session_day
        # Check for time overlap
        if (start_time < session_day.end_time and end_time > session_day.start_time):
            conflicts.append(assignment)
    
    return conflicts

def calculate_pay_eligibility(db: Session, instructor_id: int, course_id: int) -> bool:
    """Calculate if an instructor assignment should be pay eligible."""
    return is_instructor_cleared_for_course(db, instructor_id, course_id)

def get_instructor_full_name(instructor: Instructor) -> str:
    """Get formatted full name for an instructor."""
    return f"{instructor.first_name} {instructor.last_name}"

def get_session_duration_hours(session_day: SessionDay) -> float:
    """Calculate the duration of a session day in hours."""
    start_datetime = datetime.combine(date.today(), session_day.start_time)
    end_datetime = datetime.combine(date.today(), session_day.end_time)
    duration = end_datetime - start_datetime
    return duration.total_seconds() / 3600

def format_session_time_range(session_day: SessionDay) -> str:
    """Format session time range as a string."""
    return f"{session_day.start_time.strftime('%H:%M')} - {session_day.end_time.strftime('%H:%M')}"

def validate_session_dates(start_date: date, end_date: date) -> bool:
    """Validate that session dates are logical."""
    if start_date > end_date:
        return False
    if start_date < date.today():
        return False
    return True

def validate_session_times(start_time: time, end_time: time) -> bool:
    """Validate that session times are logical."""
    return start_time < end_time

def soft_delete_instructor(db: Session, instructor_id: int) -> Optional[Instructor]:
    """Soft delete an instructor by setting active_status to False."""
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    if instructor:
        instructor.active_status = False
        db.commit()
        db.refresh(instructor)
    return instructor

def soft_delete_course(db: Session, course_id: int) -> Optional[Course]:
    """Soft delete a course by setting active_status to False."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        course.active_status = False
        db.commit()
        db.refresh(course)
    return course

def get_upcoming_assignments(db: Session, instructor_id: int, days_ahead: int = 30) -> list[InstructorAssignment]:
    """Get upcoming assignments for an instructor within the specified number of days."""
    cutoff_date = date.today()
    end_date = date.fromordinal(cutoff_date.toordinal() + days_ahead)
    
    return db.query(InstructorAssignment).join(SessionDay).filter(
        InstructorAssignment.instructor_id == instructor_id,
        SessionDay.date >= cutoff_date,
        SessionDay.date <= end_date
    ).order_by(SessionDay.date, SessionDay.start_time).all()

def get_instructor_stats(db: Session, instructor_id: int) -> dict:
    """Get statistics for an instructor."""
    total_assignments = db.query(InstructorAssignment).filter(
        InstructorAssignment.instructor_id == instructor_id
    ).count()
    
    total_ratings = db.query(InstructorCourseRating).filter(
        InstructorCourseRating.instructor_id == instructor_id
    ).count()
    
    cleared_ratings = db.query(InstructorCourseRating).filter(
        InstructorCourseRating.instructor_id == instructor_id,
        InstructorCourseRating.rating == RatingType.CLEARED
    ).count()
    
    return {
        "total_assignments": total_assignments,
        "total_course_ratings": total_ratings,
        "cleared_courses": cleared_ratings
    }