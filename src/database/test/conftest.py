import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_postgresql.factories import postgresql_proc, postgresql
from src.database.connection import Base
from src.database.models import *

# PostgreSQL process and database fixtures
postgresql_proc = postgresql_proc(port=None, unixsocketdir='/tmp')
postgresql = postgresql('postgresql_proc')

@pytest.fixture(scope='function')
def db_engine(postgresql):
    """Create test database engine using PostgreSQL for testing."""
    engine = create_engine(
        f"postgresql+psycopg://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}",
        echo=False
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def db_session(db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_instructor(db_session):
    """Create sample instructor for testing."""
    instructor = Instructor(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="555-1234",
        notes="Test instructor"
    )
    db_session.add(instructor)
    db_session.commit()
    db_session.refresh(instructor)
    return instructor

@pytest.fixture
def sample_course(db_session):
    """Create sample course for testing."""
    course = Course(
        course_name="Basic Firearms Safety",
        course_code="BFS101",
        description="Introduction to firearm safety",
        duration_days=2
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

@pytest.fixture
def sample_location(db_session):
    """Create sample location for testing."""
    location = Location(
        location_name="Main Training Center",
        address="123 Training St",
        city="Training City",
        state_province="TX",
        postal_code="12345",
        notes="Primary training facility"
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location

@pytest.fixture
def instructor_with_rating(db_session, sample_instructor, sample_course):
    """Create instructor with course rating."""
    rating = InstructorCourseRating(
        instructor_id=sample_instructor.id,
        course_id=sample_course.id,
        rating=RatingType.CLEARED,
        notes="Fully qualified instructor"
    )
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return sample_instructor, sample_course, rating