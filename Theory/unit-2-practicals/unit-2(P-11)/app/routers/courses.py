from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app import models, schemas
from app.auth import get_current_user, require_admin
from app.config import settings
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("", response_model=schemas.CourseOut, status_code=201,
             responses={409: {"model": schemas.ErrorOut}, 403: {"model": schemas.ErrorOut}},
             summary="Create a course (admin only)")
def create_course(data: schemas.CourseCreate, service: CourseService = Depends(),
                  _: models.Student = Depends(require_admin)):
    return service.create(data)


@router.get("", response_model=schemas.Page[schemas.CourseOut], summary="List courses")
def list_courses(credits: Optional[int] = Query(None, ge=1, le=6), page: int = Query(1, ge=1),
                 limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
                 service: CourseService = Depends(), _: models.Student = Depends(get_current_user)):
    return service.list(credits, page, limit)


@router.get("/{course_id}", response_model=schemas.CourseOut, responses={404: {"model": schemas.ErrorOut}})
def get_course(course_id: str, service: CourseService = Depends(), _: models.Student = Depends(get_current_user)):
    return service.get(course_id)


@router.delete("/{course_id}", status_code=204, responses={404: {"model": schemas.ErrorOut}},
               summary="Delete a course (admin only)")
def delete_course(course_id: str, service: CourseService = Depends(), _: models.Student = Depends(require_admin)):
    service.delete(course_id)
    return Response(status_code=204)
