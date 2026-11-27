"""API version 1: DEPRECATED. Kept for existing clients until the sunset date."""
from datetime import datetime, timezone
from email.utils import format_datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import schemas
import services
from database import get_db

DEPRECATED_SINCE = datetime(2026, 11, 1, tzinfo=timezone.utc)
SUNSET = datetime(2027, 5, 31, 23, 59, 59, tzinfo=timezone.utc)


def apply_deprecation_headers(response: Response):
    """Called by the middleware in main.py for EVERY /api/v1 response, including 404 and 422 errors
    (a router dependency would miss error responses)."""
    response.headers["Deprecation"] = f"@{int(DEPRECATED_SINCE.timestamp())}"      # RFC 9745
    response.headers["Sunset"] = format_datetime(SUNSET, usegmt=True)               # RFC 8594
    response.headers["Link"] = '</api/v2/students>; rel="successor-version"'
    response.headers["X-API-Version"] = "1"


router = APIRouter(
    prefix="/api/v1",
    tags=["v1 (deprecated)"],
    deprecated=True,                          # struck through in Swagger UI and ReDoc
)

NOT_FOUND = {404: {"model": schemas.ErrorOut, "description": "Student not found"}}


@router.get("/students", response_model=list[schemas.StudentV1], summary="List students (basic, unpaginated)")
def list_students(branch: schemas.Branch | None = None, db: Session = Depends(get_db)):
    """Returns a **plain JSON array** (first 100 rows). Use `/api/v2/students` for pagination."""
    return services.student_query(db, branch=branch).limit(100).all()


@router.get("/students/{student_id}", response_model=schemas.StudentV1, responses=NOT_FOUND)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return services.get_student_or_404(db, student_id)


@router.post("/students", response_model=schemas.StudentV1, status_code=201,
             responses={409: {"model": schemas.ErrorOut, "description": "Email already registered"}})
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    return services.create_student(db, payload)
