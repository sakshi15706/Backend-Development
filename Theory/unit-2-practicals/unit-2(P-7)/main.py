"""P-7: Student Management API with JWT authentication.

    uvicorn main:app --reload     ->  http://127.0.0.1:8000/docs
"""
import math
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

import auth
import models
import schemas
from auth import get_current_user, require_admin_or_self
from database import Base, engine, get_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Student Management API (JWT)",
    description=("JWT authentication. `POST /register`, then `POST /login`, then send "
                 "`Authorization: Bearer <token>`. Use the **Authorize** button in Swagger UI."),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[{"name": "Auth"}, {"name": "Students"}, {"name": "Courses"}, {"name": "Enrollments"}, {"name": "Departments"}],
)


# ----------------------------- helpers -----------------------------
def paginate(query, page: int, limit: int) -> dict:
    total = query.order_by(None).count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"items": items, "page": page, "limit": limit, "total": total,
            "total_pages": math.ceil(total / limit) if total else 0}


def get_or_404(db: Session, model, key, label: str):
    obj = db.get(model, key)
    if obj is None:
        raise HTTPException(404, f"{label} '{key}' not found")
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


# ============================= Auth =============================
@app.post("/register", response_model=schemas.StudentOut, status_code=201, tags=["Auth"],
          summary="Register a new student (public)")
def register(payload: schemas.StudentRegister, db: Session = Depends(get_db)):
    check_department(db, payload.department_id)
    data = payload.model_dump(exclude={"password"})
    student = models.Student(**data, hashed_password=auth.hash_password(payload.password), role="student")
    db.add(student)
    commit_or_409(db, f"Email '{payload.email}' is already registered")
    db.refresh(student)
    return student


@app.post("/login", response_model=schemas.Token, tags=["Auth"],
          summary="Log in (form fields: username = email, password)")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Student).filter(models.Student.email == form.username.lower()).first()
    if user is None or not auth.verify_password(form.password, user.hashed_password):
        # same message for "unknown email" and "wrong password" so attackers learn nothing
        raise HTTPException(401, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": auth.create_access_token(user), "token_type": "bearer",
            "expires_in": int(auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60)}


@app.get("/me", response_model=schemas.StudentOut, tags=["Auth"], summary="Who am I? (needs a token)")
def me(current: models.Student = Depends(get_current_user)):
    return current


# ============================= Departments =============================
@app.post("/departments", response_model=schemas.DepartmentOut, status_code=201, tags=["Departments"])
def create_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db),
                      _: models.Student = Depends(get_current_user)):
    dept = models.Department(**payload.model_dump())
    db.add(dept)
    commit_or_409(db, "Department name already exists")
    return dept


@app.get("/departments", response_model=list[schemas.DepartmentOut], tags=["Departments"])
def list_departments(db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    return db.query(models.Department).order_by(models.Department.name).all()


# ============================= Courses =============================
@app.post("/courses", response_model=schemas.CourseOut, status_code=201, tags=["Courses"])
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db),
                  _: models.Student = Depends(get_current_user)):
    check_department(db, payload.department_id)
    db.add(models.Course(**payload.model_dump()))
    commit_or_409(db, f"Course '{payload.id}' already exists")
    return db.get(models.Course, payload.id)


@app.get("/courses", response_model=schemas.Page[schemas.CourseOut], tags=["Courses"])
def list_courses(department_id: Optional[int] = None, credits: Optional[int] = Query(None, ge=1, le=6),
                 page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db),
                 _: models.Student = Depends(get_current_user)):
    query = db.query(models.Course)
    if department_id is not None:
        query = query.filter(models.Course.department_id == department_id)
    if credits is not None:
        query = query.filter(models.Course.credits == credits)
    return paginate(query.order_by(models.Course.id), page, limit)


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, tags=["Courses"])
def get_course(course_id: str, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    return get_or_404(db, models.Course, course_id, "Course")


# ============================= Students =============================
@app.get("/students", response_model=schemas.Page[schemas.StudentOut], tags=["Students"])
def list_students(
    branch: Optional[schemas.Branch] = Query(None, description="CSE, ECE, IT, ME or CE"),
    department_id: Optional[int] = Query(None, description="filter by department id"),
    search: Optional[str] = Query(None, min_length=1, description="matches name or email"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.Student = Depends(get_current_user),
):
    query = db.query(models.Student).options(joinedload(models.Student.department))
    if branch:
        query = query.filter(models.Student.branch == branch)
    if department_id is not None:
        query = query.filter(models.Student.department_id == department_id)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(models.Student.name.ilike(pattern), models.Student.email.ilike(pattern)))
    return paginate(query.order_by(models.Student.name, models.Student.id), page, limit)


@app.get("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    return get_or_404(db, models.Student, student_id, "Student")


@app.put("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"],
         summary="Replace a student (all fields required)")
def replace_student(student_id: int, payload: schemas.StudentCreate, db: Session = Depends(get_db),
                    _: models.Student = Depends(require_admin_or_self)):
    student = get_or_404(db, models.Student, student_id, "Student")
    check_department(db, payload.department_id)
    for field, value in payload.model_dump().items():
        setattr(student, field, value)
    commit_or_409(db, "Email already registered")
    db.refresh(student)
    return student


@app.patch("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"],
           summary="Update some fields of a student")
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db),
                   _: models.Student = Depends(require_admin_or_self)):
    student = get_or_404(db, models.Student, student_id, "Student")
    changes = payload.model_dump(exclude_unset=True)
    check_department(db, changes.get("department_id"))
    for field, value in changes.items():
        setattr(student, field, value)
    commit_or_409(db, "Email already registered")
    db.refresh(student)
    return student


@app.delete("/students/{student_id}", status_code=204, tags=["Students"],
            summary="Delete a student (admin or the student themselves)")
def delete_student(student_id: int, db: Session = Depends(get_db),
                   _: models.Student = Depends(require_admin_or_self)):
    db.delete(get_or_404(db, models.Student, student_id, "Student"))   # enrollments are cascaded
    db.commit()
    return Response(status_code=204)


# ============================= Nested: student enrollments =============================
@app.get("/students/{student_id}/enrollments", response_model=list[schemas.EnrollmentOut], tags=["Enrollments"])
def list_enrollments(student_id: int, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    get_or_404(db, models.Student, student_id, "Student")
    return (db.query(models.Enrollment).options(joinedload(models.Enrollment.course))
            .filter_by(student_id=student_id).order_by(models.Enrollment.course_id).all())


@app.post("/students/{student_id}/enrollments", response_model=schemas.EnrollmentOut, status_code=201,
          tags=["Enrollments"])
def enroll_student(student_id: int, payload: schemas.EnrollmentCreate, db: Session = Depends(get_db),
                   _: models.Student = Depends(require_admin_or_self)):
    get_or_404(db, models.Student, student_id, "Student")
    get_or_404(db, models.Course, payload.course_id, "Course")
    db.add(models.Enrollment(student_id=student_id, **payload.model_dump()))
    commit_or_409(db, f"Student {student_id} is already enrolled in {payload.course_id}")
    return db.get(models.Enrollment, (student_id, payload.course_id))


@app.patch("/students/{student_id}/enrollments/{course_id}", response_model=schemas.EnrollmentOut,
           tags=["Enrollments"], summary="Set the grade")
def set_grade(student_id: int, course_id: str, payload: schemas.EnrollmentGrade, db: Session = Depends(get_db),
              _: models.Student = Depends(require_admin_or_self)):
    enrollment = get_or_404(db, models.Enrollment, (student_id, course_id), "Enrollment")
    enrollment.grade = payload.grade
    db.commit()
    return enrollment


@app.delete("/students/{student_id}/enrollments/{course_id}", status_code=204, tags=["Enrollments"])
def drop_course(student_id: int, course_id: str, db: Session = Depends(get_db),
                _: models.Student = Depends(require_admin_or_self)):
    db.delete(get_or_404(db, models.Enrollment, (student_id, course_id), "Enrollment"))
    db.commit()
    return Response(status_code=204)
