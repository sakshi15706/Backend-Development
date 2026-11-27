from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app import models, schemas
from app.auth import require_admin, require_owner_or_admin
from app.config import settings
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])
NOT_FOUND = {404: {"model": schemas.ErrorOut}}
FORBIDDEN = {403: {"model": schemas.ErrorOut}}


@router.get("", response_model=schemas.Page[schemas.StudentOut], responses=FORBIDDEN,
            summary="List students (admin only)")
def list_students(
    branch: Optional[schemas.Branch] = None,
    search: Optional[str] = Query(None, min_length=1, description="matches name or email"),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    service: StudentService = Depends(),
    _: models.Student = Depends(require_admin),
):
    return service.list(branch, search, page, limit)


@router.get("/{student_id}", response_model=schemas.StudentOut, responses={**NOT_FOUND, **FORBIDDEN},
            summary="Get a student (admin or the student themselves)")
def get_student(student_id: int, service: StudentService = Depends(),
                _: models.Student = Depends(require_owner_or_admin)):
    return service.get(student_id)


@router.patch("/{student_id}", response_model=schemas.StudentOut, responses={**NOT_FOUND, **FORBIDDEN},
              summary="Update a student (admin or the student themselves)")
def update_student(student_id: int, data: schemas.StudentUpdate, service: StudentService = Depends(),
                   _: models.Student = Depends(require_owner_or_admin)):
    return service.update(student_id, data)


@router.delete("/{student_id}", status_code=204, responses={**NOT_FOUND, **FORBIDDEN},
               summary="Delete a student (admin only)")
def delete_student(student_id: int, service: StudentService = Depends(), _: models.Student = Depends(require_admin)):
    service.delete(student_id)
    return Response(status_code=204)
