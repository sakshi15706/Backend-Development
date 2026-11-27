from sqlalchemy import JSON, CheckConstraint, Column, Date, Integer, String, Text

from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)       # SENSITIVE: never in a response
    internal_notes = Column(Text, default="")                    # SENSITIVE: staff-only notes
    enrollment_date = Column(Date, nullable=False)
    graduation_date = Column(Date)
    photo_filename = Column(String(100))


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("credits BETWEEN 1 AND 6", name="ck_credits"),)

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(String(500))
    prerequisites = Column(JSON, default=list)                   # list of course codes
