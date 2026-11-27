from datetime import date
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Pagination envelope used by every list endpoint."""
    items: List[T]
    page: int
    limit: int
    total: int
    total_pages: int


# ---------- Department ----------
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class DepartmentOut(DepartmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Course ----------
class CourseBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=10, examples=["CS301"])
    title: str = Field(..., min_length=1, max_length=100)
    credits: int = Field(..., ge=1, le=6)
    department_id: Optional[int] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=10)
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    credits: Optional[int] = Field(None, ge=1, le=6)
    department_id: Optional[int] = None


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Student ----------
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    branch: str = Field(..., pattern=r"^(CSE|ECE|IT|ME|CE)$")
    enrollment_date: Optional[date] = None
    department_id: Optional[int] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    branch: Optional[str] = Field(None, pattern=r"^(CSE|ECE|IT|ME|CE)$")
    enrollment_date: Optional[date] = None
    department_id: Optional[int] = None


class StudentOut(StudentBase):
    """Student together with the related Department (related-data requirement)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    department: Optional[DepartmentOut] = None
