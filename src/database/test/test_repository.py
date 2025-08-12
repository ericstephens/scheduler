import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from datetime import date, datetime
from src.database.repository import (
    InstructorRepository, CourseRepository, LocationRepository,
    RatingRepository, SessionRepository, AssignmentRepository
)
from src.database.models import RatingType, SessionStatus, AssignmentStatus, SessionType

class TestInstructorRepository:
    def test_create_instructor(self, db_session):
        repo = InstructorRepository(db_session)
        instructor = repo.create(
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            phone_number="555-0123",
            notes="New instructor"
        )
        
        assert instructor.id is not None
        assert instructor.first_name == "Alice"
        assert instructor.last_name == "Johnson"
        assert instructor.email == "alice@example.com"
        assert instructor.phone_number == "555-0123"
        assert instructor.active_status == True

    def test_get_by_id(self, db_session, sample_instructor):
        repo = InstructorRepository(db_session)
        retrieved = repo.get_by_id(sample_instructor.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_instructor.id
        assert retrieved.email == sample_instructor.email

    def test_get_by_email(self, db_session, sample_instructor):
        repo = InstructorRepository(db_session)
        retrieved = repo.get_by_email(sample_instructor.email)
        
        assert retrieved is not None
        assert retrieved.id == sample_instructor.id

    def test_get_all_active_only(self, db_session):
        repo = InstructorRepository(db_session)
        
        # Create active and inactive instructors
        active = repo.create("Active", "User", "active@test.com")
        inactive = repo.create("Inactive", "User", "inactive@test.com")
        inactive.active_status = False
        db_session.commit()
        
        # Test active only (default)
        active_instructors = repo.get_all(active_only=True)
        active_ids = [i.id for i in active_instructors]
        assert active.id in active_ids
        assert inactive.id not in active_ids
        
        # Test all instructors
        all_instructors = repo.get_all(active_only=False)
        all_ids = [i.id for i in all_instructors]
        assert active.id in all_ids
        assert inactive.id in all_ids

    def test_set_active_status(self, db_session, sample_instructor):
        repo = InstructorRepository(db_session)
        
        # Deactivate instructor
        updated = repo.set_active_status(sample_instructor.id, False)
        assert updated.active_status == False
        
        # Reactivate instructor
        updated = repo.set_active_status(sample_instructor.id, True)
        assert updated.active_status == True

    def test_search_by_name(self, db_session):
        repo = InstructorRepository(db_session)
        
        # Create test instructors
        repo.create("John", "Smith", "john.smith@test.com")
        repo.create("Jane", "Johnson", "jane.johnson@test.com") 
        repo.create("Bob", "Jones", "bob.jones@test.com")
        
        # Search by first name - should find John Smith
        results = repo.search_by_name("John")
        john_results = [r for r in results if r.first_name == "John"]
        assert len(john_results) == 1
        assert john_results[0].first_name == "John"
        
        # Search by last name - should find Jane Johnson  
        results = repo.search_by_name("Johnson")
        johnson_results = [r for r in results if r.last_name == "Johnson"]
        assert len(johnson_results) == 1
        
        # Search partial match
        results = repo.search_by_name("Jo")
        assert len(results) >= 2

class TestCourseRepository:
    def test_create_course(self, db_session):
        repo = CourseRepository(db_session)
        course = repo.create(
            course_name="Tactical Training",
            course_code="TAC101",
            description="Tactical training course",
            duration_days=5
        )
        
        assert course.id is not None
        assert course.course_name == "Tactical Training"
        assert course.course_code == "TAC101"
        assert course.duration_days == 5

    def test_get_by_code(self, db_session, sample_course):
        repo = CourseRepository(db_session)
        retrieved = repo.get_by_code(sample_course.course_code)
        
        assert retrieved is not None
        assert retrieved.id == sample_course.id

    def test_set_active_status(self, db_session, sample_course):
        repo = CourseRepository(db_session)
        
        updated = repo.set_active_status(sample_course.id, False)
        assert updated.active_status == False

class TestLocationRepository:
    def test_create_location(self, db_session):
        repo = LocationRepository(db_session)
        location = repo.create(
            location_name="Indoor Range",
            address="789 Indoor Ave",
            city="Indoor City"
        )
        
        assert location.id is not None
        assert location.location_name == "Indoor Range"
        # Location type and capacity fields have been removed

    def test_get_all_locations(self, db_session, sample_location):
        repo = LocationRepository(db_session)
        locations = repo.get_all()
        
        assert len(locations) >= 1
        location_ids = [l.id for l in locations]
        assert sample_location.id in location_ids

class TestRatingRepository:
    def test_create_rating(self, db_session, sample_instructor, sample_course):
        repo = RatingRepository(db_session)
        rating = repo.create_or_update_rating(
            instructor_id=sample_instructor.id,
            course_id=sample_course.id,
            rating=RatingType.CLEARED,
            notes="Fully qualified"
        )
        
        assert rating.id is not None
        assert rating.rating == RatingType.CLEARED
        assert rating.notes == "Fully qualified"

    def test_update_existing_rating(self, db_session, instructor_with_rating):
        instructor, course, existing_rating = instructor_with_rating
        original_id = existing_rating.id
        
        repo = RatingRepository(db_session)
        updated_rating = repo.create_or_update_rating(
            instructor_id=instructor.id,
            course_id=course.id,
            rating=RatingType.CO_TEACH,
            notes="Updated rating"
        )
        
        # Should update existing record, not create new one
        assert updated_rating.id == original_id
        assert updated_rating.rating == RatingType.CO_TEACH
        assert updated_rating.notes == "Updated rating"

    def test_get_rating(self, db_session, instructor_with_rating):
        instructor, course, rating = instructor_with_rating
        
        repo = RatingRepository(db_session)
        retrieved = repo.get_rating(instructor.id, course.id)
        
        assert retrieved is not None
        assert retrieved.id == rating.id

    def test_get_instructor_ratings(self, db_session, sample_instructor):
        repo = RatingRepository(db_session)
        
        # Create multiple course ratings for instructor
        course1 = CourseRepository(db_session).create("Course 1", "C001", duration_days=1)
        course2 = CourseRepository(db_session).create("Course 2", "C002", duration_days=2)
        
        repo.create_or_update_rating(sample_instructor.id, course1.id, RatingType.CLEARED)
        repo.create_or_update_rating(sample_instructor.id, course2.id, RatingType.CO_TEACH)
        
        ratings = repo.get_instructor_ratings(sample_instructor.id)
        assert len(ratings) == 2

    def test_get_cleared_instructors_for_course(self, db_session, sample_course):
        repo = RatingRepository(db_session)
        instructor_repo = InstructorRepository(db_session)
        
        # Create instructors with different ratings
        instructor1 = instructor_repo.create("Cleared", "Instructor", "cleared@test.com")
        instructor2 = instructor_repo.create("Observer", "Instructor", "observer@test.com")
        
        repo.create_or_update_rating(instructor1.id, sample_course.id, RatingType.CLEARED)
        repo.create_or_update_rating(instructor2.id, sample_course.id, RatingType.OBSERVE)
        
        cleared_instructors = repo.get_cleared_instructors_for_course(sample_course.id)
        assert instructor1.id in cleared_instructors
        assert instructor2.id not in cleared_instructors

class TestSessionRepository:
    def test_create_session(self, db_session, sample_course):
        repo = SessionRepository(db_session)
        session = repo.create_session(
            course_id=sample_course.id,
            session_name="Winter 2024",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 17),
            notes="Winter session"
        )
        
        assert session.id is not None
        assert session.session_name == "Winter 2024"
        assert session.start_date == date(2024, 1, 15)
        # Total students field has been removed

    def test_get_by_status(self, db_session, sample_course):
        repo = SessionRepository(db_session)
        
        # Create sessions with different statuses
        scheduled_session = repo.create_session(
            sample_course.id, "Scheduled", date(2024, 2, 1), date(2024, 2, 3)
        )
        
        completed_session = repo.create_session(
            sample_course.id, "Completed", date(2024, 1, 1), date(2024, 1, 3)
        )
        completed_session.status = SessionStatus.COMPLETED
        db_session.commit()
        
        # Test filtering by status
        scheduled = repo.get_by_status(SessionStatus.SCHEDULED)
        completed = repo.get_by_status(SessionStatus.COMPLETED)
        
        scheduled_ids = [s.id for s in scheduled]
        completed_ids = [s.id for s in completed]
        
        assert scheduled_session.id in scheduled_ids
        assert completed_session.id in completed_ids
        assert completed_session.id not in scheduled_ids

    def test_update_status(self, db_session, sample_course):
        repo = SessionRepository(db_session)
        session = repo.create_session(
            sample_course.id, "Test", date(2024, 3, 1), date(2024, 3, 3)
        )
        
        updated = repo.update_status(session.id, SessionStatus.IN_PROGRESS)
        assert updated.status == SessionStatus.IN_PROGRESS

class TestAssignmentRepository:
    def test_create_assignment(self, db_session, sample_course, sample_location, sample_instructor):
        # Setup session and session day
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 4, 1), date(2024, 4, 1)
        )
        
        from src.database.models import CourseSessionDay
        from datetime import time
        session_day = CourseSessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 4, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        # Create assignment
        repo = AssignmentRepository(db_session)
        assignment = repo.create_assignment(
            session_day_id=session_day.id,
            instructor_id=sample_instructor.id,
            assignment_type=SessionType.FULL_DAY,
            notes="Test assignment"
        )
        
        assert assignment.id is not None
        # Pay eligible field has been removed
        assert assignment.notes == "Test assignment"

    def test_get_instructor_assignments(self, db_session, sample_course, sample_location, sample_instructor):
        # Setup
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 5, 1), date(2024, 5, 1)
        )
        
        from src.database.models import CourseSessionDay
        from datetime import time
        session_day = CourseSessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 5, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        # Create assignments
        repo = AssignmentRepository(db_session)
        assignment1 = repo.create_assignment(session_day.id, sample_instructor.id, SessionType.FULL_DAY, True)
        
        # Get assignments for instructor
        assignments = repo.get_instructor_assignments(sample_instructor.id)
        assert len(assignments) >= 1
        assignment_ids = [a.id for a in assignments]
        assert assignment1.id in assignment_ids

    def test_update_status(self, db_session, sample_course, sample_location, sample_instructor):
        # Setup assignment
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 6, 1), date(2024, 6, 1)
        )
        
        from src.database.models import CourseSessionDay
        from datetime import time
        session_day = CourseSessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 6, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        repo = AssignmentRepository(db_session)
        assignment = repo.create_assignment(session_day.id, sample_instructor.id, SessionType.FULL_DAY, True)
        
        # Update status
        updated = repo.update_status(assignment.id, AssignmentStatus.CONFIRMED)
        assert updated.assignment_status == AssignmentStatus.CONFIRMED

    def test_get_pay_eligible_assignments(self, db_session, sample_course, sample_location, sample_instructor):
        # Setup
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 7, 1), date(2024, 7, 1)
        )
        
        from src.database.models import CourseSessionDay
        from datetime import time
        session_day = CourseSessionDay(
            session_id=session.id,
            day_number=1,
            date=date(2024, 7, 1),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        db_session.add(session_day)
        db_session.commit()
        
        repo = AssignmentRepository(db_session)
        
        # Create assignments (pay eligibility now determined by instructor clearance)
        assignment1 = repo.create_assignment(session_day.id, sample_instructor.id, SessionType.FULL_DAY)
        assignment2 = repo.create_assignment(session_day.id, sample_instructor.id, SessionType.HALF_DAY)
        
        # Get all assignments (method now returns all, not just pay eligible)
        all_assignments = repo.get_pay_eligible_assignments()
        assignment_ids = [a.id for a in all_assignments]
        
        assert assignment1.id in assignment_ids
        assert assignment2.id in assignment_ids