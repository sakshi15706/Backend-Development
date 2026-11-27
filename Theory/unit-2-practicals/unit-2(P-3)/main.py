"""P-3: complete CRUD API for Course (and Student with a Department foreign key).

    uvicorn main:app --reload      ->  http://127.0.0.1:8000/docs
"""
import math
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import Base, engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Course and Student API", version="1.0.0", lifespan=lifespan)


def paginate(query, page: int, limit: int):
    """Returns the dict that matches schemas.Page."""
    total = query.order_by(None).count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": math.ceil(total / limit) if total else 0,
    }


def get_or_404(db: Session, model, obj_id: int, label: str):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(404, f"{label} {obj_id} not found")
    return obj


def check_department(db: Session, department_id: Optional[int]):
    if department_id is not None:
        get_or_404(db, models.Department, department_id, "Department")


def commit_or_409(db: Session, message: str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, message)


# ======================= Departments =======================
@app.post("/departments", response_model=schemas.DepartmentOut, status_code=201, tags=["Departments"])
def create_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    dept = models.Department(**payload.model_dump())
    db.add(dept)
    commit_or_409(db, "Department name already exists")
    return dept


@app.get("/departments", response_model=list[schemas.DepartmentOut], tags=["Departments"])
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).order_by(models.Department.name).all()


# ======================= Courses (main exercise) =======================
@app.post("/courses", response_model=schemas.CourseOut, status_code=201, tags=["Courses"])
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db)):          # CREATE
    check_department(db, payload.department_id)
    course = models.Course(**payload.model_dump())
    db.add(course)
    commit_or_409(db, f"Course code '{payload.code}' already exists")
    db.refresh(course)
    return course


@app.get("/courses", response_model=schemas.Page[schemas.CourseOut], tags=["Courses"])
def list_courses(                                                                          # READ (filter + paginate)
    department_id: Optional[int] = Query(None, description="filter by department"),
    credits: Optional[int] = Query(None, ge=1, le=6, description="filter by credits"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100, description="10 courses per page by default"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Course)
    if department_id is not None:
        query = query.filter(models.Course.department_id == department_id)
    if credits is not None:
        query = query.filter(models.Course.credits == credits)
    return paginate(query.order_by(models.Course.code), page, limit)


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, tags=["Courses"])
def get_course(course_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Course, course_id, "Course")


@app.put("/courses/{course_id}", response_model=schemas.CourseOut, tags=["Courses"])
def update_course(course_id: int, payload: schemas.CourseUpdate, db: Session = Depends(get_db)):  # UPDATE
    course = get_or_404(db, models.Course, course_id, "Course")
    changes = payload.model_dump(exclude_unset=True)
    check_department(db, changes.get("department_id"))
    for field, value in changes.items():
        setattr(course, field, value)
    commit_or_409(db, "Course code already exists")
    db.refresh(course)
    return course


@app.delete("/courses/{course_id}", status_code=204, tags=["Courses"])
def delete_course(course_id: int, db: Session = Depends(get_db)):                          # DELETE
    db.delete(get_or_404(db, models.Course, course_id, "Course"))
    db.commit()
    return Response(status_code=204)


# ======================= Students (FK to Department + related data) =======================
@app.post("/students", response_model=schemas.StudentOut, status_code=201, tags=["Students"])
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    check_department(db, payload.department_id)
    student = models.Student(**payload.model_dump())
    db.add(student)
    commit_or_409(db, f"Email '{payload.email}' is already registered")
    db.refresh(student)
    return student


@app.get("/students", response_model=schemas.Page[schemas.StudentOut], tags=["Students"])
def list_students(
    branch: Optional[str] = None,
    department_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Student).options(joinedload(models.Student.department))  # eager load
    if branch:
        query = query.filter(models.Student.branch == branch)
    if department_id is not None:
        query = query.filter(models.Student.department_id == department_id)
    return paginate(query.order_by(models.Student.name), page, limit)


@app.get("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Student, student_id, "Student")


@app.put("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"])
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = get_or_404(db, models.Student, student_id, "Student")
    changes = payload.model_dump(exclude_unset=True)
    check_department(db, changes.get("department_id"))
    for field, value in changes.items():
        setattr(student, field, value)
    commit_or_409(db, "Email already registered")
    db.refresh(student)
    return student


@app.delete("/students/{student_id}", status_code=204, tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, models.Student, student_id, "Student"))
    db.commit()
    return Response(status_code=204)
