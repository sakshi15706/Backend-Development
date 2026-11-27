"""Authentication (who are you?) and authorization helpers (what may you do?)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db
from app.exceptions import AppError, ForbiddenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UnauthorizedError(AppError):
    status_code = 401


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(user: models.Student) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user.id), "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Student:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired, please log in again")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")
    user = db.get(models.Student, int(payload.get("sub", 0)))
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user                                     # role is read from the DB, not trusted from the token


def require_admin(user: models.Student = Depends(get_current_user)) -> models.Student:
    if user.role != "admin":
        raise ForbiddenError("Admin role required")
    return user


def require_owner_or_admin(student_id: int, user: models.Student = Depends(get_current_user)) -> models.Student:
    if user.role != "admin" and user.id != student_id:
        raise ForbiddenError("You can only access your own data")
    return user
