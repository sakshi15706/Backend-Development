"""Logic shared by v1 and v2, so a new API version never copies business rules."""
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

import models
import schemas


def student_query(db: Session, branch: Optional[str] = None, department_id: Optional[int] = None,
                  search: Optional[str] = None):
    query = db.query(models.Student).options(joinedload(models.Student.department),
                                              joinedload(models.Student.enrollments))
    if branch:
        query = query.filter(models.Student.branch == branch)
    if department_id is not None:
        query = query.filter(models.Student.department_id == department_id)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(models.Student.name.ilike(like), models.Student.email.ilike(like)))
    return query.order_by(models.Student.name, models.Student.id)


def get_student_or_404(db: Session, student_id: int) -> models.Student:
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(404, f"Student '{student_id}' not found")
    return student


def create_student(db: Session, payload: schemas.StudentCreate) -> models.Student:
    student = models.Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, f"Email '{payload.email}' is already registered")
    db.refresh(student)
    return student


def to_v2(student: models.Student) -> dict:
    return {"id": student.id, "name": student.name, "email": student.email, "branch": student.branch,
            "enrollment_date": student.enrollment_date, "department": student.department,
            "enrollment_count": len(student.enrollments)}
