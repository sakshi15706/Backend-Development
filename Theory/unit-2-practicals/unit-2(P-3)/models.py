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
    department_id = Column(Integer, ForeignKey("departments.id"))  # FK to Department

    department = relationship("Department", back_populates="students")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 6", name="ck_credits"),)

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="courses")
