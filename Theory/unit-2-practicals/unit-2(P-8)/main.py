"""P-8: Student Management API with Role-Based Access Control (Admin / Faculty / Student).

    uvicorn main:app --reload     ->  http://127.0.0.1:8000/docs
"""
import logging
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
from auth import get_current_user
from database import Base, engine, get_db
from permissions import permissions_of, require_permission, require_permission_or_own

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Student Management API (RBAC)",
    description=("Roles: **admin**, **faculty**, **student**. Log in, then use the Authorize button.\n\n"
                 "`GET /me/permissions` shows what the current role may do."),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[{"name": "Auth"}, {"name": "Admin"}, {"name": "Students"}, {"name": "Courses"},
                  {"name": "Enrollments"}, {"name": "Departments"}],
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
          summary="Register (always creates a student)")
def register(payload: schemas.StudentRegister, db: Session = Depends(get_db)):
    check_department(db, payload.department_id)
    student = models.Student(**payload.model_dump(exclude={"password"}),
                             hashed_password=auth.hash_password(payload.password), role="student")
    db.add(student)
    commit_or_409(db, f"Email '{payload.email}' is already registered")
    db.refresh(student)
    return student


@app.post("/login", response_model=schemas.Token, tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Student).filter(models.Student.email == form.username.lower()).first()
    if user is None or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": auth.create_access_token(user), "token_type": "bearer",
            "expires_in": int(auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60)}


@app.get("/me", response_model=schemas.StudentOut, tags=["Auth"])
def me(current: models.Student = Depends(get_current_user)):
    return current


@app.get("/me/permissions", response_model=schemas.MyPermissions, tags=["Auth"],
         summary="List the permissions of my role")
def my_permissions(current: models.Student = Depends(get_current_user)):
    return {"user_id": current.id, "role": current.role, "permissions": sorted(permissions_of(current))}


# ============================= Admin =============================
@app.patch("/users/{user_id}/role", response_model=schemas.StudentOut, tags=["Admin"],
           summary="Change a user's role (admin only)")
def change_role(user_id: int, payload: schemas.RoleUpdate, db: Session = Depends(get_db),
                admin: models.Student = Depends(require_permission("roles:manage"))):
    if admin.id == user_id:
        raise HTTPException(409, "You cannot change your own role (prevents locking out the last admin)")
    user = get_or_404(db, models.Student, user_id, "User")
    logging.getLogger("authz").info("ROLE  admin=%s changed user=%s role %s -> %s",
                                    admin.id, user.id, user.role, payload.role)
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


# ============================= Departments =============================
@app.post("/departments", response_model=schemas.DepartmentOut, status_code=201, tags=["Departments"])
def create_department(payload: schemas.DepartmentCreate, db: Session = Depends(get_db),
                      _: models.Student = Depends(require_permission("courses:write"))):
    dept = models.Department(**payload.model_dump())
    db.add(dept)
    commit_or_409(db, "Department name already exists")
    return dept


@app.get("/departments", response_model=list[schemas.DepartmentOut], tags=["Departments"])
def list_departments(db: Session = Depends(get_db), _: models.Student = Depends(require_permission("courses:read"))):
    return db.query(models.Department).order_by(models.Department.name).all()


# ============================= Courses =============================
@app.post("/courses", response_model=schemas.CourseOut, status_code=201, tags=["Courses"])
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db),
                  _: models.Student = Depends(require_permission("courses:write"))):
    check_department(db, payload.department_id)
    db.add(models.Course(**payload.model_dump()))
    commit_or_409(db, f"Course '{payload.id}' already exists")
    return db.get(models.Course, payload.id)


@app.get("/courses", response_model=schemas.Page[schemas.CourseOut], tags=["Courses"])
def list_courses(department_id: Optional[int] = None, credits: Optional[int] = Query(None, ge=1, le=6),
                 page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db),
                 _: models.Student = Depends(require_permission("courses:read"))):
    query = db.query(models.Course)
    if department_id is not None:
        query = query.filter(models.Course.department_id == department_id)
    if credits is not None:
        query = query.filter(models.Course.credits == credits)
    return paginate(query.order_by(models.Course.id), page, limit)


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, tags=["Courses"])
def get_course(course_id: str, db: Session = Depends(get_db),
               _: models.Student = Depends(require_permission("courses:read"))):
    return get_or_404(db, models.Course, course_id, "Course")


@app.delete("/courses/{course_id}", status_code=204, tags=["Courses"])
def delete_course(course_id: str, db: Session = Depends(get_db),
                  _: models.Student = Depends(require_permission("courses:delete"))):
    db.delete(get_or_404(db, models.Course, course_id, "Course"))
    db.commit()
    return Response(status_code=204)


# ============================= Students =============================
@app.get("/students", response_model=schemas.Page[schemas.StudentOut], tags=["Students"],
         summary="List students (admin, faculty)")
def list_students(
    branch: Optional[schemas.Branch] = None,
    department_id: Optional[int] = None,
    search: Optional[str] = Query(None, min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.Student = Depends(require_permission("students:read")),
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


@app.get("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"],
         summary="Get a student (admin, faculty, or the student themselves)")
def get_student(student_id: int, db: Session = Depends(get_db),
                _: models.Student = Depends(require_permission_or_own("students:read", "students:read_own"))):
    return get_or_404(db, models.Student, student_id, "Student")


@app.patch("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"],
           summary="Update a student (admin, or the student themselves)")
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db),
                   _: models.Student = Depends(require_permission_or_own("students:write", "students:update_own"))):
    student = get_or_404(db, models.Student, student_id, "Student")
    changes = payload.model_dump(exclude_unset=True)
    check_department(db, changes.get("department_id"))
    for field, value in changes.items():
        setattr(student, field, value)
    commit_or_409(db, "Email already registered")
    db.refresh(student)
    return student


@app.delete("/students/{student_id}", status_code=204, tags=["Students"], summary="Delete a student (admin only)")
def delete_student(student_id: int, db: Session = Depends(get_db),
                   _: models.Student = Depends(require_permission("students:delete"))):
    db.delete(get_or_404(db, models.Student, student_id, "Student"))
    db.commit()
    return Response(status_code=204)


# ============================= Enrollments =============================
@app.get("/students/{student_id}/enrollments", response_model=list[schemas.EnrollmentOut], tags=["Enrollments"],
         summary="Enrollments and grades (admin, faculty, or the student themselves)")
def list_enrollments(student_id: int, db: Session = Depends(get_db),
                     _: models.Student = Depends(require_permission_or_own("grades:read", "grades:read_own"))):
    get_or_404(db, models.Student, student_id, "Student")
    return (db.query(models.Enrollment).options(joinedload(models.Enrollment.course))
            .filter_by(student_id=student_id).order_by(models.Enrollment.course_id).all())


@app.post("/students/{student_id}/enrollments", response_model=schemas.EnrollmentOut, status_code=201,
          tags=["Enrollments"], summary="Enrol (admin, or the student themselves)")
def enroll_student(student_id: int, payload: schemas.EnrollmentCreate, db: Session = Depends(get_db),
                   current: models.Student = Depends(
                       require_permission_or_own("students:write", "students:update_own"))):
    get_or_404(db, models.Student, student_id, "Student")
    get_or_404(db, models.Course, payload.course_id, "Course")
    # a student enrolling themselves must not be able to award themselves a grade
    if payload.grade is not None and "grades:write" not in permissions_of(current):
        raise HTTPException(403, "Permission denied: grades:write required to set a grade")
    db.add(models.Enrollment(student_id=student_id, **payload.model_dump()))
    commit_or_409(db, f"Student {student_id} is already enrolled in {payload.course_id}")
    return db.get(models.Enrollment, (student_id, payload.course_id))


@app.patch("/students/{student_id}/enrollments/{course_id}", response_model=schemas.EnrollmentOut,
           tags=["Enrollments"], summary="Set a grade (admin, faculty)")
def set_grade(student_id: int, course_id: str, payload: schemas.EnrollmentGrade, db: Session = Depends(get_db),
              _: models.Student = Depends(require_permission("grades:write"))):
    enrollment = get_or_404(db, models.Enrollment, (student_id, course_id), "Enrollment")
    enrollment.grade = payload.grade
    db.commit()
    return enrollment


@app.delete("/students/{student_id}/enrollments/{course_id}", status_code=204, tags=["Enrollments"],
            summary="Drop a course (admin, or the student themselves)")
def drop_course(student_id: int, course_id: str, db: Session = Depends(get_db),
                _: models.Student = Depends(require_permission_or_own("students:write", "students:update_own"))):
    db.delete(get_or_404(db, models.Enrollment, (student_id, course_id), "Enrollment"))
    db.commit()
    return Response(status_code=204)
