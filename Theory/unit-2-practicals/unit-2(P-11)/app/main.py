"""Student Management API (refactored, layered).

    uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.bootstrap import ensure_admin
from app.database import Base, SessionLocal, engine
from app.exceptions import AppError
from app.routers import auth, courses, enrollments, students

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("student_api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Fine for a lab project. In a real project use Alembic migrations instead of create_all.
    Base.metadata.create_all(engine)
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        with SessionLocal() as db:
            ensure_admin(db, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
    log.info("started in %s mode", settings.ENVIRONMENT)
    yield


app = FastAPI(
    title="Student Management API",
    description="Layered FastAPI project: routers, services, models, config, tests.\n\n"
                "Log in with `POST /api/v1/auth/login`, then use the **Authorize** button.",
    version="1.0.0",
    contact={"name": "Backend Development Lab", "email": "student@example.com"},
    lifespan=lifespan,
    openapi_tags=[{"name": "Auth"}, {"name": "Students"}, {"name": "Courses"}, {"name": "Enrollments"},
                  {"name": "Meta"}],
)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message}, headers=headers)


for router in (auth.router, students.router, courses.router, enrollments.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["Meta"], summary="Health check (used by the hosting platform)")
def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/", tags=["Meta"], include_in_schema=False)
def root():
    return {"name": "Student Management API", "docs": "/docs", "health": "/health"}
