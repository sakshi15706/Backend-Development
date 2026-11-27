from fastapi import APIRouter, Depends, Response

from app import models, schemas
from app.auth import require_admin, require_owner_or_admin
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/students/{student_id}/enrollments", tags=["Enrollments"])
ERRORS = {404: {"model": schemas.ErrorOut}, 403: {"model": schemas.ErrorOut}}


@router.get("", response_model=list[schemas.EnrollmentOut], responses=ERRORS)
def list_enrollments(student_id: int, service: EnrollmentService = Depends(),
                     _: models.Student = Depends(require_owner_or_admin)):
    return service.list_for_student(student_id)


@router.post("", response_model=schemas.EnrollmentOut, status_code=201,
             responses={**ERRORS, 409: {"model": schemas.ErrorOut}}, summary="Enrol in a course")
def enroll(student_id: int, data: schemas.EnrollmentCreate, service: EnrollmentService = Depends(),
           _: models.Student = Depends(require_owner_or_admin)):
    return service.enroll(student_id, data)


@router.patch("/{course_id}", response_model=schemas.EnrollmentOut, responses=ERRORS,
              summary="Set a grade (admin only)")
def set_grade(student_id: int, course_id: str, data: schemas.EnrollmentGrade,
              service: EnrollmentService = Depends(), _: models.Student = Depends(require_admin)):
    return service.set_grade(student_id, course_id, data.grade)


@router.delete("/{course_id}", status_code=204, responses=ERRORS, summary="Drop a course")
def drop(student_id: int, course_id: str, service: EnrollmentService = Depends(),
         _: models.Student = Depends(require_owner_or_admin)):
    service.drop(student_id, course_id)
    return Response(status_code=204)
