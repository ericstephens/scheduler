import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from datetime import date, time, datetime
from src.database.utils import (
    is_instructor_cleared_for_course, check_instructor_availability,
    get_instructor_conflicts, calculate_pay_eligibility,
    get_instructor_full_name, get_session_duration_hours,
    format_session_time_range, validate_session_dates,
    validate_session_times, get_upcoming_assignments,
    get_instructor_stats
)
from src.database.models import (
    SessionDay, InstructorAssignment, InstructorCourseRating,
    RatingType, SessionType
)

class TestInstructorUtils:
    def test_get_instructor_full_name(self, sample_instructor):
        full_name = get_instructor_full_name(sample_instructor)
        expected = f"{sample_instructor.first_name} {sample_instructor.last_name}"
        assert full_name == expected

    def test_is_instructor_cleared_for_course(self, db_session, instructor_with_rating):
        instructor, course, rating = instructor_with_rating
        
        # Test with cleared rating
        assert is_instructor_cleared_for_course(db_session, instructor.id, course.id) == True
        
        # Update rating to non-cleared
        rating.rating = RatingType.OBSERVE
        db_session.commit()
        
        assert is_instructor_cleared_for_course(db_session, instructor.id, course.id) == False

    def test_calculate_pay_eligibility(self, db_session, instructor_with_rating):
        instructor, course, rating = instructor_with_rating
        
        # Test with cleared instructor
        assert calculate_pay_eligibility(db_session, instructor.id, course.id) == True
        
        # Test with non-cleared instructor
        rating.rating = RatingType.CO_TEACH
        db_session.commit()
        
        assert calculate_pay_eligibility(db_session, instructor.id, course.id) == False

class TestAvailabilityUtils:
    def test_check_instructor_availability_no_conflicts(self, db_session, sample_instructor):
        # Test availability when no existing assignments
        is_available = check_instructor_availability(
            db_session, 
            sample_instructor.id, 
            date(2024, 8, 1),
            time(9, 0),
            time(17, 0)
        )
        assert is_available == True

    def test_check_instructor_availability_with_conflict(self, db_session, sample_instructor, sample_course, sample_location):
        # Create existing assignment
        from src.database.repository import SessionRepository
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Existing Session", date(2024, 8, 15), date(2024, 8, 15)
        )
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 8, 15),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        assignment = InstructorAssignment(
            session_day_id=session_day.id,
            instructor_id=sample_instructor.id,
            assignment_type=SessionType.FULL_DAY,
            pay_eligible=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Test overlap - should return False
        is_available = check_instructor_availability(
            db_session,
            sample_instructor.id,
            date(2024, 8, 15),
            time(8, 0),  # Starts earlier but overlaps
            time(10, 0)
        )
        assert is_available == False
        
        # Test no overlap - should return True
        is_available = check_instructor_availability(
            db_session,
            sample_instructor.id,
            date(2024, 8, 15),
            time(18, 0),  # After existing assignment
            time(20, 0)
        )
        assert is_available == True

    def test_get_instructor_conflicts(self, db_session, sample_instructor, sample_course, sample_location):
        # Create conflicting assignment
        from src.database.repository import SessionRepository
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Conflicting Session", date(2024, 9, 1), date(2024, 9, 1)
        )
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 9, 1),
            location_id=sample_location.id,
            start_time=time(10, 0),
            end_time=time(16, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        assignment = InstructorAssignment(
            session_day_id=session_day.id,
            instructor_id=sample_instructor.id,
            assignment_type=SessionType.FULL_DAY,
            pay_eligible=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Test getting conflicts
        conflicts = get_instructor_conflicts(
            db_session,
            sample_instructor.id,
            date(2024, 9, 1),
            time(9, 0),
            time(12, 0)  # Overlaps with existing 10-16 assignment
        )
        
        assert len(conflicts) == 1
        assert conflicts[0].id == assignment.id

class TestSessionUtils:
    def test_get_session_duration_hours(self, sample_location, sample_course, db_session):
        from src.database.repository import SessionRepository
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Duration Test", date(2024, 10, 1), date(2024, 10, 1)
        )
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 10, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        duration = get_session_duration_hours(session_day)
        assert duration == 8.0  # 9 AM to 5 PM = 8 hours

    def test_format_session_time_range(self, sample_location, sample_course, db_session):
        from src.database.repository import SessionRepository
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Format Test", date(2024, 11, 1), date(2024, 11, 1)
        )
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 11, 1),
            location_id=sample_location.id,
            start_time=time(9, 30),
            end_time=time(16, 45),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        formatted = format_session_time_range(session_day)
        assert formatted == "09:30 - 16:45"

class TestValidationUtils:
    def test_validate_session_dates(self):
        from datetime import date
        today = date.today()
        
        # Valid dates - future dates
        future_start = date(today.year + 1, 1, 1)
        future_end = date(today.year + 1, 1, 3)
        assert validate_session_dates(future_start, future_end) == True
        
        # Invalid - end before start
        assert validate_session_dates(future_end, future_start) == False
        
        # Invalid - start in past
        past_date = date(2020, 1, 1)
        assert validate_session_dates(past_date, future_end) == False

    def test_validate_session_times(self):
        # Valid times
        assert validate_session_times(time(9, 0), time(17, 0)) == True
        
        # Invalid - end before start
        assert validate_session_times(time(17, 0), time(9, 0)) == False
        
        # Invalid - same time
        assert validate_session_times(time(12, 0), time(12, 0)) == False

class TestReportingUtils:
    def test_get_upcoming_assignments(self, db_session, sample_instructor, sample_course, sample_location):
        # Create future assignment with a date relative to today
        from src.database.repository import SessionRepository
        from datetime import date, timedelta
        
        future_date = date.today() + timedelta(days=10)
        session_repo = SessionRepository(db_session)
        future_session = session_repo.create_session(
            sample_course.id, "Future Session", future_date, future_date
        )
        
        session_day = SessionDay(
            session_id=future_session.id,
            day_number=1,
            date=future_date,
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        assignment = InstructorAssignment(
            session_day_id=session_day.id,
            instructor_id=sample_instructor.id,
            assignment_type=SessionType.FULL_DAY,
            pay_eligible=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Get upcoming assignments
        upcoming = get_upcoming_assignments(db_session, sample_instructor.id, 365)
        assert len(upcoming) >= 1
        
        assignment_ids = [a.id for a in upcoming]
        assert assignment.id in assignment_ids

    def test_get_instructor_stats(self, db_session, sample_instructor, sample_course, sample_location):
        # Create rating
        from src.database.repository import RatingRepository
        rating_repo = RatingRepository(db_session)
        rating_repo.create_or_update_rating(
            sample_instructor.id, sample_course.id, RatingType.CLEARED
        )
        
        # Create assignment
        from src.database.repository import SessionRepository
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Stats Test", date(2024, 12, 1), date(2024, 12, 1)
        )
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 12, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        assignment = InstructorAssignment(
            session_day_id=session_day.id,
            instructor_id=sample_instructor.id,
            assignment_type=SessionType.FULL_DAY,
            pay_eligible=True
        )
        db_session.add(assignment)
        db_session.commit()
        
        stats = get_instructor_stats(db_session, sample_instructor.id)
        
        assert stats["total_assignments"] >= 1
        assert stats["pay_eligible_assignments"] >= 1
        assert stats["total_course_ratings"] >= 1
        assert stats["cleared_courses"] >= 1
        assert isinstance(stats, dict)
        assert all(key in stats for key in [
            "total_assignments", "pay_eligible_assignments", 
            "total_course_ratings", "cleared_courses"
        ])