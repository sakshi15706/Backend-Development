import logging
from typing import Optional

from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.exceptions import ConflictError, NotFoundError
from app.services.base import paginate

log = logging.getLogger(__name__)


class StudentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def register(self, data: schemas.StudentRegister) -> models.Student:
        student = models.Student(**data.model_dump(exclude={"password"}),
                                 hashed_password=auth.hash_password(data.password), role="student")
        self.db.add(student)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError(f"Email '{data.email}' is already registered")
        self.db.refresh(student)
        log.info("registered student id=%s", student.id)
        return student

    def authenticate(self, email: str, password: str) -> Optional[models.Student]:
        user = self.db.query(models.Student).filter_by(email=email.lower()).first()
        if user and auth.verify_password(password, user.hashed_password):
            return user
        return None

    def get(self, student_id: int) -> models.Student:
        student = self.db.get(models.Student, student_id)
        if student is None:
            raise NotFoundError(f"Student {student_id} not found")
        return student

    def list(self, branch: Optional[str], search: Optional[str], page: int, limit: int) -> dict:
        query = self.db.query(models.Student)
        if branch:
            query = query.filter(models.Student.branch == branch)
        if search:
            like = f"%{search}%"
            query = query.filter(or_(models.Student.name.ilike(like), models.Student.email.ilike(like)))
        return paginate(query.order_by(models.Student.name, models.Student.id), page, limit)

    def update(self, student_id: int, data: schemas.StudentUpdate) -> models.Student:
        student = self.get(student_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id: int) -> None:
        self.db.delete(self.get(student_id))
        self.db.commit()
        log.info("deleted student id=%s", student_id)
