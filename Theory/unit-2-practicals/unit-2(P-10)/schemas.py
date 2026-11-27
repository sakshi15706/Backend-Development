from datetime import date
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

T = TypeVar("T")
Branch = Literal["CSE", "ECE", "IT", "ME", "CE"]


class ErrorOut(BaseModel):
    detail: str = Field(..., examples=["Student '42' not found"])


# ------------------------------ shared request body ------------------------------
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Aarav Sharma"])
    email: EmailStr = Field(..., examples=["aarav@upes.ac.in"])
    branch: Branch = Field(..., examples=["CSE"])
    enrollment_date: Optional[date] = Field(None, examples=["2024-08-01"])

    @field_validator("email")
    @classmethod
    def lower_email(cls, v):
        return v.lower()

    model_config = ConfigDict(json_schema_extra={
        "examples": [{"name": "Aarav Sharma", "email": "aarav@upes.ac.in", "branch": "CSE",
                      "enrollment_date": "2024-08-01"}]})


# ------------------------------ v1: basic response ------------------------------
class StudentV1(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "examples": [{"id": 1, "name": "Aarav Sharma", "email": "aarav@upes.ac.in", "branch": "CSE"}]})
    id: int
    name: str
    email: str
    branch: str


# ------------------------------ v2: enhanced response ------------------------------
class DepartmentV2(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class StudentV2(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "id": 1, "name": "Aarav Sharma", "email": "aarav@upes.ac.in", "branch": "CSE",
        "enrollment_date": "2024-08-01", "department": {"id": 1, "name": "Computer Science"},
        "enrollment_count": 2}]})
    id: int
    name: str
    email: str
    branch: str
    enrollment_date: Optional[date] = None
    department: Optional[DepartmentV2] = None
    enrollment_count: int = Field(0, description="number of courses the student is enrolled in")


class Links(BaseModel):
    self: str
    next: Optional[str] = None
    prev: Optional[str] = None


class PageV2(BaseModel, Generic[T]):
    items: List[T]
    page: int
    limit: int
    total: int
    total_pages: int
    links: Links
