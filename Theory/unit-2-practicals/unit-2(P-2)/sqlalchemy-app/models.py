"""P-2 Part 2: SQLAlchemy models for the Student Management System (with relationships)."""
from sqlalchemy import (
    CheckConstraint, Column, Date, ForeignKey, Integer, String, create_engine, event,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///students.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


# SQLite ignores foreign keys unless asked, so turn enforcement on for every connection.
@event.listens_for(engine, "connect")
def _enable_fk(dbapi_connection, _):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    building = Column(String(50))

    # 1:M  Department -> Students / Courses
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    branch = Column(String(50))
    enrollment_date = Column(Date)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="students")
    # cascade: deleting a student also deletes their enrollment rows
    enrollments = relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 6", name="ck_course_credits"),)

    id = Column(String(10), primary_key=True)
    title = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="courses")
    enrollments = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(Base):
    """Junction table for the M:N relationship Student <-> Course."""
    __tablename__ = "enrollments"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    course_id = Column(String(10), ForeignKey("courses.id"), primary_key=True)
    semester = Column(String(20))
    grade = Column(String(2))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


def init_db():
    Base.metadata.create_all(engine)
