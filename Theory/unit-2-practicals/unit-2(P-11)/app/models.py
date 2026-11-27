from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (Index("ix_students_branch_name", "branch", "name"),)   # speeds up filter + sort

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    branch = Column(String(10), nullable=False, index=True)
    enrollment_date = Column(Date)
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(10), nullable=False, default="student")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 6", name="ck_course_credits"),)

    id = Column(String(10), primary_key=True)
    title = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(String(10), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)
    semester = Column(String(20), nullable=False)
    grade = Column(String(2))
    enrolled_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
