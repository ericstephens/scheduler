from typing import List, Optional
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .models import (
    Instructor, Course, Location, InstructorCourseRating, 
    CourseSession, CourseSessionDay, InstructorAssignment,
    RatingType, SessionStatus, AssignmentStatus, SessionType
)

class InstructorRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, first_name: str, last_name: str, email: str, 
               phone_number: Optional[str] = None, notes: Optional[str] = None) -> Instructor:
        instructor = Instructor(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            notes=notes
        )
        self.db.add(instructor)
        self.db.commit()
        self.db.refresh(instructor)
        return instructor
    
    def get_by_id(self, instructor_id: int) -> Optional[Instructor]:
        return self.db.query(Instructor).filter(Instructor.id == instructor_id).first()
    
    def get_by_email(self, email: str) -> Optional[Instructor]:
        return self.db.query(Instructor).filter(Instructor.email == email).first()
    
    def get_all(self, active_only: bool = True) -> List[Instructor]:
        query = self.db.query(Instructor)
        if active_only:
            query = query.filter(Instructor.active_status == True)
        return query.all()
    
    def update(self, instructor: Instructor) -> Instructor:
        self.db.commit()
        self.db.refresh(instructor)
        return instructor
    
    def set_active_status(self, instructor_id: int, active: bool) -> Optional[Instructor]:
        instructor = self.get_by_id(instructor_id)
        if instructor:
            instructor.active_status = active
            return self.update(instructor)
        return None
    
    def search_by_name(self, name: str, active_only: bool = True) -> List[Instructor]:
        query = self.db.query(Instructor)
        if active_only:
            query = query.filter(Instructor.active_status == True)
        search_term = f"%{name}%"
        return query.filter(
            or_(
                Instructor.first_name.ilike(search_term),
                Instructor.last_name.ilike(search_term)
            )
        ).all()

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, course_name: str, course_code: str, description: Optional[str] = None,
               duration_days: int = 1) -> Course:
        course = Course(
            course_name=course_name,
            course_code=course_code,
            description=description,
            duration_days=duration_days
        )
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()
    
    def get_by_code(self, course_code: str) -> Optional[Course]:
        return self.db.query(Course).filter(Course.course_code == course_code).first()
    
    def get_all(self, active_only: bool = True) -> List[Course]:
        query = self.db.query(Course)
        if active_only:
            query = query.filter(Course.active_status == True)
        return query.all()
    
    def update(self, course: Course) -> Course:
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def set_active_status(self, course_id: int, active: bool) -> Optional[Course]:
        course = self.get_by_id(course_id)
        if course:
            course.active_status = active
            return self.update(course)
        return None

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, location_name: str, address: Optional[str] = None,
               city: Optional[str] = None, state_province: Optional[str] = None,
               postal_code: Optional[str] = None, notes: Optional[str] = None) -> Location:
        location = Location(
            location_name=location_name,
            address=address,
            city=city,
            state_province=state_province,
            postal_code=postal_code,
            notes=notes
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location
    
    def get_by_id(self, location_id: int) -> Optional[Location]:
        return self.db.query(Location).filter(Location.id == location_id).first()
    
    def get_all(self, active_only: bool = True) -> List[Location]:
        query = self.db.query(Location)
        if active_only:
            query = query.filter(Location.active_status == True)
        return query.all()
    
    def update(self, location: Location) -> Location:
        self.db.commit()
        self.db.refresh(location)
        return location
    
    def set_active_status(self, location_id: int, active: bool) -> Optional[Location]:
        location = self.get_by_id(location_id)
        if location:
            location.active_status = active
            return self.update(location)
        return None

class RatingRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update_rating(self, instructor_id: int, course_id: int, 
                               rating: RatingType, notes: Optional[str] = None) -> InstructorCourseRating:
        existing_rating = self.get_rating(instructor_id, course_id)
        if existing_rating:
            existing_rating.rating = rating
            existing_rating.notes = notes
            existing_rating.date_updated = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_rating)
            return existing_rating
        else:
            new_rating = InstructorCourseRating(
                instructor_id=instructor_id,
                course_id=course_id,
                rating=rating,
                notes=notes
            )
            self.db.add(new_rating)
            self.db.commit()
            self.db.refresh(new_rating)
            return new_rating
    
    def get_rating(self, instructor_id: int, course_id: int) -> Optional[InstructorCourseRating]:
        return self.db.query(InstructorCourseRating).filter(
            and_(
                InstructorCourseRating.instructor_id == instructor_id,
                InstructorCourseRating.course_id == course_id
            )
        ).first()
    
    def get_instructor_ratings(self, instructor_id: int) -> List[InstructorCourseRating]:
        return self.db.query(InstructorCourseRating).filter(
            InstructorCourseRating.instructor_id == instructor_id
        ).all()
    
    def get_course_ratings(self, course_id: int) -> List[InstructorCourseRating]:
        return self.db.query(InstructorCourseRating).filter(
            InstructorCourseRating.course_id == course_id
        ).all()
    
    def get_cleared_instructors_for_course(self, course_id: int) -> List[int]:
        ratings = self.db.query(InstructorCourseRating).filter(
            and_(
                InstructorCourseRating.course_id == course_id,
                InstructorCourseRating.rating == RatingType.CLEARED
            )
        ).all()
        return [rating.instructor_id for rating in ratings]

class SessionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, course_id: int, session_name: str, start_date: date,
                      end_date: date, notes: Optional[str] = None) -> CourseSession:
        session = CourseSession(
            course_id=course_id,
            session_name=session_name,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_by_id(self, session_id: int) -> Optional[CourseSession]:
        return self.db.query(CourseSession).filter(CourseSession.id == session_id).first()
    
    def get_all(self) -> List[CourseSession]:
        return self.db.query(CourseSession).all()
    
    def get_by_status(self, status: SessionStatus) -> List[CourseSession]:
        return self.db.query(CourseSession).filter(CourseSession.status == status).all()
    
    def update_status(self, session_id: int, status: SessionStatus) -> Optional[CourseSession]:
        session = self.get_by_id(session_id)
        if session:
            session.status = status
            self.db.commit()
            self.db.refresh(session)
        return session

class CourseSessionDayRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session_id: int, day_number: int, date: date, location_id: int,
               start_time: time, end_time: time, session_type: SessionType) -> CourseSessionDay:
        session_day = CourseSessionDay(
            session_id=session_id,
            day_number=day_number,
            date=date,
            location_id=location_id,
            start_time=start_time,
            end_time=end_time,
            session_type=session_type
        )
        self.db.add(session_day)
        self.db.commit()
        self.db.refresh(session_day)
        return session_day
    
    def get_by_id(self, session_day_id: int) -> Optional[CourseSessionDay]:
        return self.db.query(CourseSessionDay).filter(CourseSessionDay.id == session_day_id).first()
    
    def get_by_session_id(self, session_id: int) -> List[CourseSessionDay]:
        return self.db.query(CourseSessionDay).filter(
            CourseSessionDay.session_id == session_id
        ).order_by(CourseSessionDay.day_number).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[CourseSessionDay]:
        return self.db.query(CourseSessionDay).filter(
            and_(
                CourseSessionDay.date >= start_date,
                CourseSessionDay.date <= end_date
            )
        ).order_by(CourseSessionDay.date, CourseSessionDay.start_time).all()
    
    def get_by_location_and_date(self, location_id: int, date: date) -> List[CourseSessionDay]:
        return self.db.query(CourseSessionDay).filter(
            and_(
                CourseSessionDay.location_id == location_id,
                CourseSessionDay.date == date
            )
        ).order_by(CourseSessionDay.start_time).all()
    
    def update(self, session_day: CourseSessionDay) -> CourseSessionDay:
        self.db.commit()
        self.db.refresh(session_day)
        return session_day
    
    def delete(self, session_day_id: int) -> bool:
        session_day = self.get_by_id(session_day_id)
        if session_day:
            self.db.delete(session_day)
            self.db.commit()
            return True
        return False
    
    def get_all(self) -> List[CourseSessionDay]:
        return self.db.query(CourseSessionDay).order_by(
            CourseSessionDay.date, CourseSessionDay.start_time
        ).all()

class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_assignment(self, session_day_id: int, instructor_id: int,
                         assignment_type: str, notes: Optional[str] = None) -> InstructorAssignment:
        assignment = InstructorAssignment(
            session_day_id=session_day_id,
            instructor_id=instructor_id,
            assignment_type=assignment_type,
            notes=notes
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def get_by_id(self, assignment_id: int) -> Optional[InstructorAssignment]:
        return self.db.query(InstructorAssignment).filter(
            InstructorAssignment.id == assignment_id
        ).first()
    
    def get_instructor_assignments(self, instructor_id: int) -> List[InstructorAssignment]:
        return self.db.query(InstructorAssignment).filter(
            InstructorAssignment.instructor_id == instructor_id
        ).all()
    
    def get_assignments_by_date_range(self, start_date: date, end_date: date) -> List[InstructorAssignment]:
        return self.db.query(InstructorAssignment).join(CourseSessionDay).filter(
            and_(
                CourseSessionDay.date >= start_date,
                CourseSessionDay.date <= end_date
            )
        ).all()
    
    def update_status(self, assignment_id: int, status: AssignmentStatus) -> Optional[InstructorAssignment]:
        assignment = self.get_by_id(assignment_id)
        if assignment:
            assignment.assignment_status = status
            self.db.commit()
            self.db.refresh(assignment)
        return assignment
    
    def get_pay_eligible_assignments(self) -> List[InstructorAssignment]:
        # Pay eligibility is now determined by instructor being cleared for the course
        # This method would need to join with ratings to determine eligibility
        # For now, returning all assignments as a placeholder
        return self.db.query(InstructorAssignment).all()