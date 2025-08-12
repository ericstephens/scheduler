from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Time, Date
from sqlalchemy.orm import relationship
from .connection import Base

class RatingType(PyEnum):
    OBSERVE = "observe"
    CO_TEACH = "co_teach"
    CLEARED = "cleared"

class SessionStatus(PyEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionType(PyEnum):
    HALF_DAY = "half_day"
    FULL_DAY = "full_day"

class AssignmentStatus(PyEnum):
    ASSIGNED = "assigned"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Instructor(Base):
    __tablename__ = "instructors"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    call_sign = Column(String(50))
    active_status = Column(Boolean, default=True, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)
    
    # Relationships
    course_ratings = relationship("InstructorCourseRating", back_populates="instructor")
    assignments = relationship("InstructorAssignment", back_populates="instructor")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(200), nullable=False)
    course_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    duration_days = Column(Integer, nullable=False)
    active_status = Column(Boolean, default=True, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    instructor_ratings = relationship("InstructorCourseRating", back_populates="course")
    course_sessions = relationship("CourseSession", back_populates="course")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(200), nullable=False)
    address = Column(String(255))
    city = Column(String(100))
    state_province = Column(String(50))
    postal_code = Column(String(20))
    active_status = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)
    
    # Relationships
    session_days = relationship("SessionDay", back_populates="location")

class InstructorCourseRating(Base):
    __tablename__ = "instructor_course_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Enum(RatingType), nullable=False)
    date_assigned = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text)
    
    # Relationships
    instructor = relationship("Instructor", back_populates="course_ratings")
    course = relationship("Course", back_populates="instructor_ratings")

class CourseSession(Base):
    __tablename__ = "course_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    session_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)
    notes = Column(Text)
    
    # Relationships
    course = relationship("Course", back_populates="course_sessions")
    session_days = relationship("SessionDay", back_populates="session")

class SessionDay(Base):
    __tablename__ = "session_days"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("course_sessions.id"), nullable=False)
    day_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    session_type = Column(Enum(SessionType), nullable=False)
    
    # Relationships
    session = relationship("CourseSession", back_populates="session_days")
    location = relationship("Location", back_populates="session_days")
    instructor_assignments = relationship("InstructorAssignment", back_populates="session_day")

class InstructorAssignment(Base):
    __tablename__ = "instructor_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_day_id = Column(Integer, ForeignKey("session_days.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=False)
    assignment_type = Column(Enum(SessionType), nullable=False)
    assignment_status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)
    
    # Relationships
    session_day = relationship("SessionDay", back_populates="instructor_assignments")
    instructor = relationship("Instructor", back_populates="assignments")