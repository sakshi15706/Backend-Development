"""Pydantic models: input validation (…Create / …Update) and response serialisation (…Out)."""
from datetime import date
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(..., examples=[1])
    limit: int = Field(..., examples=[10])
    total: int = Field(..., examples=[42])
    total_pages: int = Field(..., examples=[5])


class ErrorOut(BaseModel):
    detail: str


# ----------------------------- Book -----------------------------
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    authors: List[str] = Field(..., min_length=1, description="a book can have several authors")
    genre: str = Field(..., min_length=2, max_length=50)
    isbn: str = Field(..., pattern=r"^\d{10}(\d{3})?$", description="10 or 13 digits")
    copies_total: int = Field(1, ge=1, le=1000)


class BookCreate(BookBase):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "title": "Clean Code", "authors": ["Robert C. Martin"], "genre": "Programming",
        "isbn": "9780132350884", "copies_total": 3}]})


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    authors: Optional[List[str]] = Field(None, min_length=1)
    genre: Optional[str] = Field(None, min_length=2, max_length=50)
    copies_total: Optional[int] = Field(None, ge=1, le=1000)


class BookOut(BookBase):
    id: int
    copies_available: int
    available: bool


# ----------------------------- Member -----------------------------
class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    status: Literal["ACTIVE", "SUSPENDED"] = "ACTIVE"


class MemberCreate(MemberBase):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "name": "Aarav", "email": "aarav@upes.ac.in", "status": "ACTIVE"}]})


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    status: Optional[Literal["ACTIVE", "SUSPENDED"]] = None


class MemberOut(MemberBase):
    id: int
    joined_on: date


# ----------------------------- Loan -----------------------------
class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    model_config = ConfigDict(json_schema_extra={"examples": [{"book_id": 1, "member_id": 1}]})


class LoanOut(BaseModel):
    id: int
    book_id: int
    member_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    status: Literal["ACTIVE", "RETURNED"]
