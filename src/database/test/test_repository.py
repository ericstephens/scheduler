import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from datetime import date, datetime, time
from src.database.repository import (
    InstructorRepository, CourseRepository, LocationRepository,
    RatingRepository, SessionRepository, AssignmentRepository, CourseSessionDayRepository
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

    def test_create_half_day_course(self, db_session):
        """Test creating a course with half-day duration."""
        repo = CourseRepository(db_session)
        course = repo.create(
            course_name="Morning Safety Brief",
            course_code="MSB-HALF",
            description="Half-day morning safety briefing",
            duration_days=0.5
        )
        
        assert course.id is not None
        assert course.course_name == "Morning Safety Brief"
        assert course.course_code == "MSB-HALF"
        assert course.duration_days == 0.5
        assert course.active_status == True

    def test_create_one_and_half_day_course(self, db_session):
        """Test creating a course with 1.5 day duration."""
        repo = CourseRepository(db_session)
        course = repo.create(
            course_name="Extended Firearms Training",
            course_code="EFT-1.5",
            description="One and half day firearms training",
            duration_days=1.5
        )
        
        assert course.id is not None
        assert course.duration_days == 1.5

    def test_create_multiple_decimal_day_course(self, db_session):
        """Test creating courses with various decimal day durations."""
        repo = CourseRepository(db_session)
        
        # Test 0.5 days
        course_half = repo.create(
            course_name="Half Day Course",
            course_code="HALF-01",
            duration_days=0.5
        )
        assert course_half.duration_days == 0.5
        
        # Test 1.5 days
        course_one_half = repo.create(
            course_name="One and Half Day Course",
            course_code="ONE-HALF-01",
            duration_days=1.5
        )
        assert course_one_half.duration_days == 1.5
        
        # Test 2.5 days
        course_two_half = repo.create(
            course_name="Two and Half Day Course",
            course_code="TWO-HALF-01",
            duration_days=2.5
        )
        assert course_two_half.duration_days == 2.5

    def test_update_course_to_half_day(self, db_session, sample_course):
        """Test updating an existing course to have half-day duration."""
        repo = CourseRepository(db_session)
        
        # Update the duration to half day
        sample_course.duration_days = 0.5
        updated_course = repo.update(sample_course)
        
        assert updated_course.duration_days == 0.5
        assert updated_course.id == sample_course.id

class TestLocationRepository:
    def test_create_location(self, db_session):
        repo = LocationRepository(db_session)
        location = repo.create(
            location_name="Indoor Range",
            address="789 Indoor Ave",
            city="Indoor City",
            state_province="TX",
            postal_code="12345",
            notes="Professional training facility"
        )
        
        assert location.id is not None
        assert location.location_name == "Indoor Range"
        assert location.address == "789 Indoor Ave"
        assert location.city == "Indoor City"
        assert location.state_province == "TX"
        assert location.postal_code == "12345"
        assert location.notes == "Professional training facility"
        assert location.active_status == True

    def test_create_location_minimal_data(self, db_session):
        repo = LocationRepository(db_session)
        location = repo.create(location_name="Minimal Location")
        
        assert location.id is not None
        assert location.location_name == "Minimal Location"
        assert location.address is None
        assert location.city is None
        assert location.state_province is None
        assert location.postal_code is None
        assert location.notes is None
        assert location.active_status == True

    def test_get_by_id(self, db_session, sample_location):
        repo = LocationRepository(db_session)
        retrieved = repo.get_by_id(sample_location.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_location.id
        assert retrieved.location_name == sample_location.location_name

    def test_get_by_id_nonexistent(self, db_session):
        repo = LocationRepository(db_session)
        retrieved = repo.get_by_id(99999)
        
        assert retrieved is None

    def test_get_all_locations(self, db_session, sample_location):
        repo = LocationRepository(db_session)
        locations = repo.get_all()
        
        assert len(locations) >= 1
        location_ids = [l.id for l in locations]
        assert sample_location.id in location_ids

    def test_get_all_active_only(self, db_session):
        repo = LocationRepository(db_session)
        
        # Create active and inactive locations
        active = repo.create("Active Location", address="123 Active St")
        inactive = repo.create("Inactive Location", address="456 Inactive St")
        repo.set_active_status(inactive.id, False)
        
        # Test active only (default)
        active_locations = repo.get_all(active_only=True)
        active_ids = [l.id for l in active_locations]
        assert active.id in active_ids
        assert inactive.id not in active_ids
        
        # Test all locations
        all_locations = repo.get_all(active_only=False)
        all_ids = [l.id for l in all_locations]
        assert active.id in all_ids
        assert inactive.id in all_ids

    def test_update_location(self, db_session, sample_location):
        repo = LocationRepository(db_session)
        
        # Update location attributes
        sample_location.location_name = "Updated Location"
        sample_location.address = "456 Updated St"
        sample_location.city = "Updated City"
        sample_location.state_province = "CA"
        sample_location.postal_code = "54321"
        sample_location.notes = "Updated facility"
        
        updated = repo.update(sample_location)
        
        assert updated.id == sample_location.id
        assert updated.location_name == "Updated Location"
        assert updated.address == "456 Updated St"
        assert updated.city == "Updated City"
        assert updated.state_province == "CA"
        assert updated.postal_code == "54321"
        assert updated.notes == "Updated facility"

    def test_set_active_status(self, db_session, sample_location):
        repo = LocationRepository(db_session)
        
        # Deactivate location
        deactivated = repo.set_active_status(sample_location.id, False)
        assert deactivated is not None
        assert deactivated.active_status == False
        
        # Reactivate location
        reactivated = repo.set_active_status(sample_location.id, True)
        assert reactivated is not None
        assert reactivated.active_status == True

    def test_set_active_status_nonexistent(self, db_session):
        repo = LocationRepository(db_session)
        result = repo.set_active_status(99999, False)
        assert result is None

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

class TestCourseSessionDayRepository:
    def test_create_session_day(self, db_session, sample_course, sample_location):
        """Test creating a new course session day."""
        # First create a session
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 8, 15), date(2024, 8, 17)
        )
        
        repo = CourseSessionDayRepository(db_session)
        session_day = repo.create(
            session_id=session.id,
            day_number=1,
            date=date(2024, 8, 15),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(17, 0),
            session_type=SessionType.FULL_DAY
        )
        
        assert session_day.id is not None
        assert session_day.session_id == session.id
        assert session_day.day_number == 1
        assert session_day.date == date(2024, 8, 15)
        assert session_day.location_id == sample_location.id
        assert session_day.start_time == time(9, 0)
        assert session_day.end_time == time(17, 0)
        assert session_day.session_type == SessionType.FULL_DAY

    def test_create_half_day_session(self, db_session, sample_course, sample_location):
        """Test creating a half-day session."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Morning Session", date(2024, 8, 20), date(2024, 8, 20)
        )
        
        repo = CourseSessionDayRepository(db_session)
        session_day = repo.create(
            session_id=session.id,
            day_number=1,
            date=date(2024, 8, 20),
            location_id=sample_location.id,
            start_time=time(9, 0),
            end_time=time(13, 0),
            session_type=SessionType.HALF_DAY
        )
        
        assert session_day.session_type == SessionType.HALF_DAY
        assert session_day.start_time == time(9, 0)
        assert session_day.end_time == time(13, 0)

    def test_get_by_id(self, db_session, sample_course, sample_location):
        """Test retrieving a session day by ID."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Test Session", date(2024, 9, 1), date(2024, 9, 1)
        )
        
        repo = CourseSessionDayRepository(db_session)
        session_day = repo.create(
            session.id, 1, date(2024, 9, 1), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        retrieved = repo.get_by_id(session_day.id)
        assert retrieved is not None
        assert retrieved.id == session_day.id
        assert retrieved.session_id == session.id

    def test_get_by_id_nonexistent(self, db_session):
        """Test retrieving a non-existent session day."""
        repo = CourseSessionDayRepository(db_session)
        retrieved = repo.get_by_id(99999)
        assert retrieved is None

    def test_get_by_session_id(self, db_session, sample_course, sample_location):
        """Test retrieving all session days for a session."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Multi-Day Session", date(2024, 9, 5), date(2024, 9, 7)
        )
        
        repo = CourseSessionDayRepository(db_session)
        
        # Create multiple session days
        day1 = repo.create(
            session.id, 1, date(2024, 9, 5), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        day2 = repo.create(
            session.id, 2, date(2024, 9, 6), sample_location.id,
            time(9, 0), time(13, 0), SessionType.HALF_DAY
        )
        day3 = repo.create(
            session.id, 3, date(2024, 9, 7), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        session_days = repo.get_by_session_id(session.id)
        assert len(session_days) == 3
        
        # Should be ordered by day_number
        assert session_days[0].day_number == 1
        assert session_days[1].day_number == 2
        assert session_days[2].day_number == 3

    def test_get_by_date_range(self, db_session, sample_course, sample_location):
        """Test retrieving session days within a date range."""
        session_repo = SessionRepository(db_session)
        session1 = session_repo.create_session(
            sample_course.id, "August Session", date(2024, 8, 25), date(2024, 8, 25)
        )
        session2 = session_repo.create_session(
            sample_course.id, "September Session", date(2024, 9, 10), date(2024, 9, 12)
        )
        
        repo = CourseSessionDayRepository(db_session)
        
        # Create session days in different dates
        day1 = repo.create(
            session1.id, 1, date(2024, 8, 25), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        day2 = repo.create(
            session2.id, 1, date(2024, 9, 10), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        day3 = repo.create(
            session2.id, 2, date(2024, 9, 11), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        # Test date range that includes only September sessions
        session_days = repo.get_by_date_range(date(2024, 9, 1), date(2024, 9, 30))
        assert len(session_days) == 2
        session_day_ids = [sd.id for sd in session_days]
        assert day2.id in session_day_ids
        assert day3.id in session_day_ids
        assert day1.id not in session_day_ids

    def test_get_by_location_and_date(self, db_session, sample_course):
        """Test retrieving session days by location and date."""
        location_repo = LocationRepository(db_session)
        location1 = location_repo.create("Location A")
        location2 = location_repo.create("Location B")
        
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Busy Day", date(2024, 10, 15), date(2024, 10, 15)
        )
        
        repo = CourseSessionDayRepository(db_session)
        
        # Create multiple sessions on same date but different locations
        day1 = repo.create(
            session.id, 1, date(2024, 10, 15), location1.id,
            time(9, 0), time(12, 0), SessionType.HALF_DAY
        )
        day2 = repo.create(
            session.id, 2, date(2024, 10, 15), location1.id,
            time(13, 0), time(17, 0), SessionType.HALF_DAY
        )
        day3 = repo.create(
            session.id, 3, date(2024, 10, 15), location2.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        # Get sessions for location1 on that date
        location1_days = repo.get_by_location_and_date(location1.id, date(2024, 10, 15))
        assert len(location1_days) == 2
        
        # Should be ordered by start_time
        assert location1_days[0].start_time == time(9, 0)
        assert location1_days[1].start_time == time(13, 0)
        
        # Get sessions for location2
        location2_days = repo.get_by_location_and_date(location2.id, date(2024, 10, 15))
        assert len(location2_days) == 1
        assert location2_days[0].id == day3.id

    def test_update_session_day(self, db_session, sample_course, sample_location):
        """Test updating a session day."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Update Test", date(2024, 11, 1), date(2024, 11, 1)
        )
        
        repo = CourseSessionDayRepository(db_session)
        session_day = repo.create(
            session.id, 1, date(2024, 11, 1), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        # Update the session day
        session_day.start_time = time(8, 0)
        session_day.end_time = time(16, 0)
        session_day.session_type = SessionType.HALF_DAY
        
        updated = repo.update(session_day)
        
        assert updated.start_time == time(8, 0)
        assert updated.end_time == time(16, 0)
        assert updated.session_type == SessionType.HALF_DAY
        assert updated.id == session_day.id

    def test_delete_session_day(self, db_session, sample_course, sample_location):
        """Test deleting a session day."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "Delete Test", date(2024, 12, 1), date(2024, 12, 1)
        )
        
        repo = CourseSessionDayRepository(db_session)
        session_day = repo.create(
            session.id, 1, date(2024, 12, 1), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        
        session_day_id = session_day.id
        
        # Delete the session day
        result = repo.delete(session_day_id)
        assert result == True
        
        # Verify it's deleted
        retrieved = repo.get_by_id(session_day_id)
        assert retrieved is None

    def test_delete_nonexistent_session_day(self, db_session):
        """Test deleting a non-existent session day."""
        repo = CourseSessionDayRepository(db_session)
        result = repo.delete(99999)
        assert result == False

    def test_get_all_session_days(self, db_session, sample_course, sample_location):
        """Test retrieving all session days."""
        session_repo = SessionRepository(db_session)
        session = session_repo.create_session(
            sample_course.id, "All Days Test", date(2024, 12, 10), date(2024, 12, 12)
        )
        
        repo = CourseSessionDayRepository(db_session)
        
        # Create session days with different dates and times
        day1 = repo.create(
            session.id, 1, date(2024, 12, 10), sample_location.id,
            time(14, 0), time(18, 0), SessionType.HALF_DAY
        )
        day2 = repo.create(
            session.id, 2, date(2024, 12, 11), sample_location.id,
            time(9, 0), time(17, 0), SessionType.FULL_DAY
        )
        day3 = repo.create(
            session.id, 3, date(2024, 12, 10), sample_location.id,
            time(9, 0), time(13, 0), SessionType.HALF_DAY
        )
        
        all_days = repo.get_all()
        assert len(all_days) >= 3
        
        # Should be ordered by date, then start_time
        # Find our created session days in the results
        our_days = [day for day in all_days if day.session_id == session.id]
        assert len(our_days) == 3
        
        # Verify ordering (date first, then start_time)
        assert our_days[0].date <= our_days[1].date <= our_days[2].date
        
        # For same date, should be ordered by start_time
        same_date_days = [day for day in our_days if day.date == date(2024, 12, 10)]
        if len(same_date_days) > 1:
            assert same_date_days[0].start_time <= same_date_days[1].start_time