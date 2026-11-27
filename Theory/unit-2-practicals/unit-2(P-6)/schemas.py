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


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class DepartmentOut(DepartmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseCreate(BaseModel):
    id: str = Field(..., min_length=3, max_length=10, pattern=r"^[A-Z]{2,4}\d{3}$", examples=["CS301"])
    title: str = Field(..., min_length=1, max_length=100)
    credits: int = Field(..., ge=1, le=6)
    department_id: Optional[int] = None


class CourseOut(CourseCreate):
    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    branch: Branch
    enrollment_date: Optional[date] = None
    department_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class StudentUpdate(BaseModel):
    """PATCH body: every field optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    branch: Optional[Branch] = None
    enrollment_date: Optional[date] = None
    department_id: Optional[int] = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v):
        return v.lower() if v else v


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    branch: str
    enrollment_date: Optional[date] = None
    department_id: Optional[int] = None
    department: Optional[DepartmentOut] = None


class EnrollmentCreate(BaseModel):
    course_id: str = Field(..., examples=["CS301"])
    semester: str = Field(..., min_length=3, max_length=20, examples=["Fall 2024"])
    grade: Optional[Grade] = None


class EnrollmentGrade(BaseModel):
    grade: Grade


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: int
    course_id: str
    semester: str
    grade: Optional[str] = None
    course: Optional[CourseOut] = None
