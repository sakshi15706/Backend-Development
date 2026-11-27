"""P-9: validation, serialisation, file upload and rate limiting.

    uvicorn main:app --reload     ->  http://127.0.0.1:8000/docs
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import auth
import models
import schemas
from auth import get_current_user
from database import Base, engine, get_db
from rate_limit import login_rate_limit
from uploads_util import read_and_validate_photo

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Validation, Serialisation and Rate Limiting", version="1.0.0", lifespan=lifespan)


# ------------------------- one consistent shape for every 422 -------------------------
@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        location = [str(p) for p in err["loc"] if p != "body"]
        errors.append({
            "field": ".".join(location) or "body",
            "message": err["msg"].removeprefix("Value error, "),
            "type": err["type"],
        })
    return JSONResponse(status_code=422, content={"detail": "Validation failed", "errors": errors})


# ============================= Auth (needed for the rate-limit task) =============================
@app.post("/register", response_model=schemas.StudentOut, status_code=201, tags=["Students"])
def register(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**payload.model_dump(exclude={"password"}),
                             hashed_password=auth.hash_password(payload.password))
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email is already registered")
    db.refresh(student)
    return student


@app.post("/login", response_model=schemas.Token, tags=["Auth"],
          dependencies=[Depends(login_rate_limit)],
          summary="Login (max 5 attempts per minute per IP, then 429)")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Student).filter_by(email=form.username.lower()).first()
    if user is None or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": auth.create_access_token(user), "token_type": "bearer"}


# ============================= Students =============================
@app.get("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"],
         summary="Get a student (response model hides password and internal notes)")
def get_student(student_id: int, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(404, f"Student {student_id} not found")
    return student


@app.patch("/students/{student_id}", response_model=schemas.StudentOut, tags=["Students"])
def update_student(student_id: int, payload: schemas.StudentUpdate, db: Session = Depends(get_db),
                   current: models.Student = Depends(get_current_user)):
    if current.id != student_id:
        raise HTTPException(403, "You can only update your own profile")
    changes = payload.model_dump(exclude_unset=True)
    # cross-field rule against the values already stored (payload may contain only one of the two dates)
    enrollment = changes.get("enrollment_date", current.enrollment_date)
    graduation = changes.get("graduation_date", current.graduation_date)
    try:
        schemas.check_dates(enrollment, graduation)
    except ValueError as e:                     # same error shape as every other 422
        return JSONResponse(status_code=422, content={
            "detail": "Validation failed",
            "errors": [{"field": "graduation_date", "message": str(e), "type": "value_error"}]})
    for field, value in changes.items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


# ============================= Profile photo upload =============================
@app.post("/students/{student_id}/photo", response_model=schemas.StudentOut, tags=["Photo"],
          summary="Upload a profile photo (JPEG or PNG, max 2 MB)")
async def upload_photo(student_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
                       current: models.Student = Depends(get_current_user)):
    if current.id != student_id:
        raise HTTPException(403, "You can only upload your own photo")
    content, extension = await read_and_validate_photo(file)

    # The stored name is generated by us. The client's filename is NEVER used
    # (this blocks path traversal such as "../../etc/passwd.png").
    filename = f"student_{student_id}.{extension}"
    for old in UPLOAD_DIR.glob(f"student_{student_id}.*"):
        old.unlink()
    (UPLOAD_DIR / filename).write_bytes(content)
    current.photo_filename = filename
    db.commit()
    db.refresh(current)
    return current


@app.get("/students/{student_id}/photo", tags=["Photo"])
def get_photo(student_id: int, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    student = db.get(models.Student, student_id)
    if student is None or not student.photo_filename:
        raise HTTPException(404, "No photo")
    return FileResponse(UPLOAD_DIR / student.photo_filename)


# ============================= Courses =============================
@app.post("/courses", response_model=schemas.CourseOut, status_code=201, tags=["Courses"],
          summary="Create a course (validated: title, credits, prerequisites)")
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db),
                  _: models.Student = Depends(get_current_user)):
    course = models.Course(**payload.model_dump())
    course.prerequisites = payload.prerequisites or []
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, tags=["Courses"])
def get_course(course_id: int, db: Session = Depends(get_db), _: models.Student = Depends(get_current_user)):
    course = db.get(models.Course, course_id)
    if course is None:
        raise HTTPException(404, f"Course {course_id} not found")
    return course
