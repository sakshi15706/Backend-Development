from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    branch = Column(String(10), nullable=False)
    enrollment_date = Column(Date)
    department_id = Column(Integer, ForeignKey("departments.id"))
    hashed_password = Column(String(100), nullable=False)       # bcrypt hash, never the plain password
    role = Column(String(10), nullable=False, default="student")  # "student" or "admin"

    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 6", name="ck_credits"),)

    id = Column(String(10), primary_key=True)          # e.g. "CS301"
    title = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    course_id = Column(String(10), ForeignKey("courses.id"), primary_key=True)
    semester = Column(String(20), nullable=False)
    grade = Column(String(2))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
