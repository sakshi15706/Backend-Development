from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.exceptions import ConflictError, NotFoundError


class EnrollmentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _student(self, student_id: int) -> models.Student:
        student = self.db.get(models.Student, student_id)
        if student is None:
            raise NotFoundError(f"Student {student_id} not found")
        return student

    def list_for_student(self, student_id: int) -> list[models.Enrollment]:
        self._student(student_id)
        return (self.db.query(models.Enrollment).options(joinedload(models.Enrollment.course))
                .filter_by(student_id=student_id).order_by(models.Enrollment.course_id).all())

    def enroll(self, student_id: int, data: schemas.EnrollmentCreate) -> models.Enrollment:
        self._student(student_id)
        if self.db.get(models.Course, data.course_id) is None:
            raise NotFoundError(f"Course '{data.course_id}' not found")
        self.db.add(models.Enrollment(student_id=student_id, **data.model_dump()))
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(f"Student {student_id} is already enrolled in {data.course_id}")
        return self.db.get(models.Enrollment, (student_id, data.course_id))

    def _get(self, student_id: int, course_id: str) -> models.Enrollment:
        enrollment = self.db.get(models.Enrollment, (student_id, course_id))
        if enrollment is None:
            raise NotFoundError(f"Student {student_id} is not enrolled in '{course_id}'")
        return enrollment

    def set_grade(self, student_id: int, course_id: str, grade: str) -> models.Enrollment:
        enrollment = self._get(student_id, course_id)
        enrollment.grade = grade
        self.db.commit()
        return enrollment

    def drop(self, student_id: int, course_id: str) -> None:
        self.db.delete(self._get(student_id, course_id))
        self.db.commit()
