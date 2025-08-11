import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from datetime import date, time, datetime
from src.database.models import (
    Instructor, Course, Location, InstructorCourseRating, 
    ClassSession, SessionDay, InstructorAssignment,
    RatingType, SessionStatus, SessionType, AssignmentStatus
)

class TestInstructorModel:
    def test_create_instructor(self, db_session):
        instructor = Instructor(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="555-9876"
        )
        db_session.add(instructor)
        db_session.commit()
        
        assert instructor.id is not None
        assert instructor.first_name == "Jane"
        assert instructor.last_name == "Smith"
        assert instructor.email == "jane.smith@example.com"
        assert instructor.active_status == True
        assert instructor.created_date is not None

    def test_instructor_unique_email(self, db_session):
        instructor1 = Instructor(
            first_name="John",
            last_name="Doe",
            email="test@example.com"
        )
        instructor2 = Instructor(
            first_name="Jane",
            last_name="Smith", 
            email="test@example.com"
        )
        
        db_session.add(instructor1)
        db_session.commit()
        
        db_session.add(instructor2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_instructor_relationships(self, db_session, sample_instructor, sample_course):
        # Create rating relationship
        rating = InstructorCourseRating(
            instructor_id=sample_instructor.id,
            course_id=sample_course.id,
            rating=RatingType.CLEARED
        )
        db_session.add(rating)
        db_session.commit()
        
        # Test relationship
        db_session.refresh(sample_instructor)
        assert len(sample_instructor.course_ratings) == 1
        assert sample_instructor.course_ratings[0].rating == RatingType.CLEARED

class TestCourseModel:
    def test_create_course(self, db_session):
        course = Course(
            course_name="Advanced Training",
            course_code="ADV201",
            description="Advanced training course",
            duration_days=3
        )
        db_session.add(course)
        db_session.commit()
        
        assert course.id is not None
        assert course.course_name == "Advanced Training"
        assert course.course_code == "ADV201"
        assert course.duration_days == 3
        assert course.active_status == True

    def test_course_unique_code(self, db_session):
        course1 = Course(course_name="Course 1", course_code="TEST01", duration_days=1)
        course2 = Course(course_name="Course 2", course_code="TEST01", duration_days=2)
        
        db_session.add(course1)
        db_session.commit()
        
        db_session.add(course2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

class TestLocationModel:
    def test_create_location(self, db_session):
        location = Location(
            location_name="Outdoor Range",
            address="456 Range Rd",
            city="Range City",
            location_type="range",
            capacity=15
        )
        db_session.add(location)
        db_session.commit()
        
        assert location.id is not None
        assert location.location_name == "Outdoor Range"
        assert location.location_type == "range"
        assert location.capacity == 15
        assert location.active_status == True

class TestInstructorCourseRating:
    def test_create_rating(self, db_session, sample_instructor, sample_course):
        rating = InstructorCourseRating(
            instructor_id=sample_instructor.id,
            course_id=sample_course.id,
            rating=RatingType.CO_TEACH,
            notes="Can co-teach this course"
        )
        db_session.add(rating)
        db_session.commit()
        
        assert rating.id is not None
        assert rating.rating == RatingType.CO_TEACH
        assert rating.notes == "Can co-teach this course"
        assert rating.date_assigned is not None

    def test_rating_relationships(self, db_session, instructor_with_rating):
        instructor, course, rating = instructor_with_rating
        
        assert rating.instructor == instructor
        assert rating.course == course
        assert rating in instructor.course_ratings
        assert rating in course.instructor_ratings

class TestClassSession:
    def test_create_session(self, db_session, sample_course):
        session = ClassSession(
            course_id=sample_course.id,
            session_name="Spring 2024 Session",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 3, 3),
            total_students=15
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.session_name == "Spring 2024 Session"
        assert session.start_date == date(2024, 3, 1)
        assert session.status == SessionStatus.SCHEDULED

class TestSessionDay:
    def test_create_session_day(self, db_session, sample_course, sample_location):
        # First create a class session
        session = ClassSession(
            course_id=sample_course.id,
            session_name="Test Session",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 3, 1)
        )
        db_session.add(session)
        db_session.commit()
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 3, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        assert session_day.id is not None
        assert session_day.day_number == 1
        assert session_day.session_type == SessionType.FULL_DAY

class TestInstructorAssignment:
    def test_create_assignment(self, db_session, sample_course, sample_location, sample_instructor):
        # Create session and session day first
        session = ClassSession(
            course_id=sample_course.id,
            session_name="Test Session",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 3, 1)
        )
        db_session.add(session)
        db_session.commit()
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 3, 1),
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
            pay_eligible=True,
            notes="Lead instructor assignment"
        )
        db_session.add(assignment)
        db_session.commit()
        
        assert assignment.id is not None
        assert assignment.pay_eligible == True
        assert assignment.assignment_status == AssignmentStatus.ASSIGNED
        assert assignment.notes == "Lead instructor assignment"

    def test_assignment_relationships(self, db_session, sample_course, sample_location, sample_instructor):
        # Create full assignment chain
        session = ClassSession(
            course_id=sample_course.id,
            session_name="Test Session",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 3, 1)
        )
        db_session.add(session)
        db_session.commit()
        
        session_day = SessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 3, 1),
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
        
        # Test all relationships
        assert assignment.instructor == sample_instructor
        assert assignment.session_day == session_day
        assert assignment in sample_instructor.assignments
        assert assignment in session_day.instructor_assignments