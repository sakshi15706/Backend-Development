"""Password hashing and JWT helpers."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from database import get_db

# In production set these as environment variables and NEVER commit a real secret.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-please-0123456789")
ALGORITHM = "HS256"
# minutes; can be fractional, e.g. ACCESS_TOKEN_EXPIRE_MINUTES=0.5 for a 30 second token
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# reads "Authorization: Bearer <token>"; the Authorize button in Swagger UI uses tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user: models.Student, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(user.id), "role": user.role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"})


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Student:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired, please log in again")
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid token")
    user = db.get(models.Student, int(payload.get("sub", 0)))
    if user is None:
        raise _unauthorized("User no longer exists")
    return user
