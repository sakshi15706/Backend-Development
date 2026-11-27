from datetime import date
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

T = TypeVar("T")
Branch = Literal["CSE", "ECE", "IT", "ME", "CE"]
Grade = Literal["A+", "A", "B+", "B", "C+", "C", "D", "F"]


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    limit: int
    total: int
    total_pages: int


class ErrorOut(BaseModel):
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ------------------------------- students -------------------------------
class StudentRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Aarav Sharma"])
    email: EmailStr = Field(..., examples=["aarav@upes.ac.in"])
    branch: Branch = Field(..., examples=["CSE"])
    enrollment_date: Optional[date] = None
    password: str = Field(..., min_length=8, max_length=72, examples=["Str0ngPass!"])

    @field_validator("email")
    @classmethod
    def lower_email(cls, v):
        return v.lower()

    @field_validator("password")
    @classmethod
    def bcrypt_limit(cls, v):
        if len(v.encode()) > 72:
            raise ValueError("password must be at most 72 bytes")
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    branch: Optional[Branch] = None
    enrollment_date: Optional[date] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    branch: str
    role: str
    enrollment_date: Optional[date] = None


# ------------------------------- courses -------------------------------
class CourseCreate(BaseModel):
    id: str = Field(..., pattern=r"^[A-Z]{2,4}\d{3}$", examples=["CS301"])
    title: str = Field(..., min_length=3, max_length=100, examples=["Database Systems"])
    credits: int = Field(..., ge=1, le=6)


class CourseOut(CourseCreate):
    model_config = ConfigDict(from_attributes=True)


# ------------------------------- enrollments -------------------------------
class EnrollmentCreate(BaseModel):
    course_id: str = Field(..., examples=["CS301"])
    semester: str = Field(..., min_length=3, max_length=20, examples=["Fall 2024"])


class EnrollmentGrade(BaseModel):
    grade: Grade


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: int
    course_id: str
    semester: str
    grade: Optional[str] = None
    course: Optional[CourseOut] = None
