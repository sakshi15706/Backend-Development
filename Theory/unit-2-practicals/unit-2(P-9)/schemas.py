"""All validation lives here: field rules, custom validators and cross-field rules."""
import re
from datetime import date
from typing import List, Optional

from pydantic import (BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator)

COURSE_CODE = re.compile(r"^[A-Z]{2,4}\d{3}$")


class StrictModel(BaseModel):
    """Reject unknown fields instead of silently ignoring them (blocks mass-assignment attacks)."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# =============================== Course ===============================
class CourseCreate(StrictModel):
    # required
    title: str = Field(..., max_length=100, examples=["Database Systems"])
    credits: int = Field(..., examples=[4])
    # optional
    description: Optional[str] = Field(None, max_length=500)
    prerequisites: Optional[List[str]] = Field(None, examples=[["CS101", "MA102"]])

    @field_validator("title")
    @classmethod
    def title_min_length(cls, v: str) -> str:                  # custom validator 1
        if len(v) < 3:
            raise ValueError("title must be at least 3 characters")
        if v.isdigit():
            raise ValueError("title cannot be only numbers")
        return v

    @field_validator("credits", mode="before")
    @classmethod
    def credits_range(cls, v):                                 # custom validator 2
        if isinstance(v, bool):
            raise ValueError("credits must be a number")
        try:
            number = int(v)
        except (TypeError, ValueError):
            raise ValueError("credits must be a whole number")
        if not 1 <= number <= 6:
            raise ValueError("credits must be between 1 and 6")
        return number

    @field_validator("prerequisites")
    @classmethod
    def valid_prerequisites(cls, v):                            # custom validator 3
        if v is None:
            return v
        if len(v) > 5:
            raise ValueError("at most 5 prerequisites are allowed")
        bad = [code for code in v if not COURSE_CODE.match(code)]
        if bad:
            raise ValueError(f"invalid course code(s): {', '.join(bad)} (expected e.g. CS101)")
        if len(set(v)) != len(v):
            raise ValueError("prerequisites must not contain duplicates")
        return v


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    credits: int
    description: Optional[str] = None
    prerequisites: List[str] = []


# =============================== Student ===============================
def check_dates(enrollment: Optional[date], graduation: Optional[date]):
    """Cross-field rules, shared by create and update."""
    if enrollment and enrollment > date.today():
        raise ValueError("enrollment_date cannot be in the future")
    if enrollment and graduation and graduation <= enrollment:
        raise ValueError("graduation_date must be after enrollment_date")


class StudentCreate(StrictModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    enrollment_date: date
    graduation_date: Optional[date] = None

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if not (re.search(r"[A-Za-z]", v) and re.search(r"\d", v)):
            raise ValueError("password must contain at least one letter and one digit")
        if len(v.encode()) > 72:
            raise ValueError("password must be at most 72 bytes")
        return v

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode="after")                              # cross-field validation
    def dates_are_consistent(self):
        check_dates(self.enrollment_date, self.graduation_date)
        return self


class StudentUpdate(StrictModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    enrollment_date: Optional[date] = None
    graduation_date: Optional[date] = None

    @model_validator(mode="after")
    def dates_are_consistent(self):
        check_dates(self.enrollment_date, self.graduation_date)
        return self


class StudentOut(BaseModel):
    """RESPONSE MODEL: lists only the safe fields.
    hashed_password and internal_notes exist on the database model but are NOT here,
    so FastAPI strips them from every response automatically."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    enrollment_date: date
    graduation_date: Optional[date] = None
    has_photo: bool = False

    @model_validator(mode="before")
    @classmethod
    def add_has_photo(cls, data):
        if hasattr(data, "photo_filename"):
            return {"id": data.id, "name": data.name, "email": data.email,
                    "enrollment_date": data.enrollment_date, "graduation_date": data.graduation_date,
                    "has_photo": bool(data.photo_filename)}
        return data


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
