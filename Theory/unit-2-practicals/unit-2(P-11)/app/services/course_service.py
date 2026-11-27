from typing import Optional

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.exceptions import ConflictError, NotFoundError
from app.services.base import paginate


class CourseService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, data: schemas.CourseCreate) -> models.Course:
        course = models.Course(**data.model_dump())
        self.db.add(course)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(f"Course '{data.id}' already exists")
        return course

    def get(self, course_id: str) -> models.Course:
        course = self.db.get(models.Course, course_id)
        if course is None:
            raise NotFoundError(f"Course '{course_id}' not found")
        return course

    def list(self, credits: Optional[int], page: int, limit: int) -> dict:
        query = self.db.query(models.Course)
        if credits is not None:
            query = query.filter(models.Course.credits == credits)
        return paginate(query.order_by(models.Course.id), page, limit)

    def delete(self, course_id: str) -> None:
        self.db.delete(self.get(course_id))
        self.db.commit()
