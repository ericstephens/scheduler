import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_postgresql.factories import postgresql_proc, postgresql

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.database.connection import Base, get_db_session
from src.database.models import *
from src.api.main import app

# PostgreSQL process and database fixtures
postgresql_proc = postgresql_proc(port=None, unixsocketdir='/tmp')
postgresql = postgresql('postgresql_proc')

# Create test database engine
@pytest.fixture(scope="function")
def test_db_engine(postgresql):
    """Create test database engine using PostgreSQL."""
    engine = create_engine(
        f"postgresql+psycopg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}",
        echo=False
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(test_db_session):
    """Create test client with database dependency override."""
    def override_get_db():
        return test_db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Sample data fixtures
@pytest.fixture
def sample_instructor(test_db_session):
    """Create sample instructor for testing."""
    instructor = Instructor(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="555-1234",
        notes="Test instructor"
    )
    test_db_session.add(instructor)
    test_db_session.commit()
    test_db_session.refresh(instructor)
    return instructor

@pytest.fixture
def sample_course(test_db_session):
    """Create sample course for testing."""
    course = Course(
        course_name="Basic Firearms Safety",
        course_code="BFS101",
        description="Introduction to firearm safety",
        duration_days=2
    )
    test_db_session.add(course)
    test_db_session.commit()
    test_db_session.refresh(course)
    return course

@pytest.fixture
def sample_location(test_db_session):
    """Create sample location for testing."""
    location = Location(
        location_name="Main Training Center",
        address="123 Training St",
        city="Training City",
        state_province="TX",
        postal_code="12345",
        notes="Primary training facility"
    )
    test_db_session.add(location)
    test_db_session.commit()
    test_db_session.refresh(location)
    return location

@pytest.fixture
def sample_rating(test_db_session, sample_instructor, sample_course):
    """Create sample instructor course rating."""
    rating = InstructorCourseRating(
        instructor_id=sample_instructor.id,
        course_id=sample_course.id,
        rating=RatingType.CLEARED,
        notes="Fully qualified instructor"
    )
    test_db_session.add(rating)
    test_db_session.commit()
    test_db_session.refresh(rating)
    return rating

@pytest.fixture
def sample_session(test_db_session, sample_course):
    """Create sample class session."""
    from datetime import date
    session = CourseSession(
        course_id=sample_course.id,
        session_name="Test Session",
        start_date=date(2024, 12, 1),
        end_date=date(2024, 12, 3),
        status=SessionStatus.SCHEDULED
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    return session

@pytest.fixture
def sample_session_day(test_db_session, sample_session, sample_location):
    """Create sample session day."""
    from datetime import date, time
    session_day = CourseSessionDay(
        session_id=sample_session.id,
        day_number=1,
        date=date(2024, 12, 1),
        location_id=sample_location.id,
        start_time=time(9, 0),
        end_time=time(17, 0),
        session_type=SessionType.FULL_DAY
    )
    test_db_session.add(session_day)
    test_db_session.commit()
    test_db_session.refresh(session_day)
    return session_day

@pytest.fixture
def sample_assignment(test_db_session, sample_session_day, sample_instructor):
    """Create sample instructor assignment."""
    assignment = InstructorAssignment(
        session_day_id=sample_session_day.id,
        instructor_id=sample_instructor.id,
        assignment_type=SessionType.FULL_DAY,
        assignment_status=AssignmentStatus.ASSIGNED,
        notes="Test assignment"
    )
    test_db_session.add(assignment)
    test_db_session.commit()
    test_db_session.refresh(assignment)
    return assignment