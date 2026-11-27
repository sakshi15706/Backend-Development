"""API version 2: current. Pagination, filtering, richer student objects."""
import math
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, Request
from sqlalchemy.orm import Session

import schemas
import services
from database import get_db


router = APIRouter(prefix="/api/v2", tags=["v2"])

NOT_FOUND = {404: {"model": schemas.ErrorOut, "description": "Student not found"}}


def page_url(request: Request, page: int, limit: int) -> str:
    return str(request.url.include_query_params(page=page, limit=limit))


@router.get("/students", response_model=schemas.PageV2[schemas.StudentV2],
            summary="List students (paginated, filterable)")
def list_students(
    request: Request,
    branch: Optional[schemas.Branch] = Query(None, description="CSE, ECE, IT, ME or CE"),
    department_id: Optional[int] = Query(None, description="filter by department"),
    search: Optional[str] = Query(None, min_length=1, description="matches name or email"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = services.student_query(db, branch, department_id, search)
    total = query.order_by(None).count()
    total_pages = math.ceil(total / limit) if total else 0
    rows = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "items": [services.to_v2(s) for s in rows],
        "page": page, "limit": limit, "total": total, "total_pages": total_pages,
        "links": {
            "self": page_url(request, page, limit),
            "next": page_url(request, page + 1, limit) if page < total_pages else None,
            "prev": page_url(request, page - 1, limit) if page > 1 else None,
        },
    }


@router.get("/students/{student_id}", response_model=schemas.StudentV2, responses=NOT_FOUND)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return services.to_v2(services.get_student_or_404(db, student_id))


@router.post("/students", response_model=schemas.StudentV2, status_code=201,
             responses={409: {"model": schemas.ErrorOut, "description": "Email already registered"}})
def create_student(
    db: Session = Depends(get_db),
    payload: schemas.StudentCreate = Body(..., openapi_examples={        # several named examples in Swagger UI
        "full": {"summary": "All fields", "value": {
            "name": "Aarav Sharma", "email": "aarav@upes.ac.in", "branch": "CSE", "enrollment_date": "2024-08-01"}},
        "minimal": {"summary": "Required fields only", "value": {
            "name": "Diya Verma", "email": "diya@upes.ac.in", "branch": "ECE"}},
        "invalid": {"summary": "Invalid (returns 422)", "value": {
            "name": "", "email": "not-an-email", "branch": "BCA"}},
    }),
):
    return services.to_v2(services.create_student(db, payload))
