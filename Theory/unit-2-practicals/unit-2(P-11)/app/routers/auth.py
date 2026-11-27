from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, models, schemas
from app.auth import UnauthorizedError, get_current_user
from app.config import settings
from app.services.student_service import StudentService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=schemas.StudentOut, status_code=201,
             responses={409: {"model": schemas.ErrorOut}}, summary="Register a new student account")
def register(data: schemas.StudentRegister, service: StudentService = Depends()):
    return service.register(data)


@router.post("/login", response_model=schemas.Token, responses={401: {"model": schemas.ErrorOut}},
             summary="Log in (form fields: username = email, password)")
def login(form: OAuth2PasswordRequestForm = Depends(), service: StudentService = Depends()):
    user = service.authenticate(form.username, form.password)
    if user is None:
        raise UnauthorizedError("Incorrect email or password")
    return {"access_token": auth.create_access_token(user), "token_type": "bearer",
            "expires_in": int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)}


@router.get("/me", response_model=schemas.StudentOut, summary="The logged-in user")
def me(current: models.Student = Depends(get_current_user)):
    return current
