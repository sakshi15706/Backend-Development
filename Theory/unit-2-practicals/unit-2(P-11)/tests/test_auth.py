from datetime import timedelta

import jwt

from app import models
from app.config import settings
from app.database import SessionLocal
from tests.conftest import API, PASSWORD, login_headers, make_user


def register(client, email="new@upes.ac.in", **over):
    body = {"name": "New Student", "email": email, "branch": "CSE", "password": PASSWORD, **over}
    return client.post(f"{API}/auth/register", json=body)


def test_register_creates_student_without_leaking_password(client):
    r = register(client)
    assert r.status_code == 201
    assert r.json()["role"] == "student"
    assert "password" not in r.json() and "hashed_password" not in r.json()


def test_register_cannot_create_admin(client):
    assert register(client, role="admin").json()["role"] == "student"


def test_register_rejects_duplicates_and_bad_input(client):
    assert register(client).status_code == 201
    assert register(client, email="NEW@upes.ac.in").status_code == 409
    assert register(client, email="x@y.com", password="short").status_code == 422
    assert register(client, email="not-an-email").status_code == 422
    assert register(client, email="z@y.com", branch="BCA").status_code == 422


def test_password_is_stored_hashed(client):
    register(client)
    with SessionLocal() as db:
        stored = db.query(models.Student).filter_by(email="new@upes.ac.in").one().hashed_password
    assert stored != PASSWORD and stored.startswith("$2")


def test_login_success_and_failure(client):
    make_user("a@upes.ac.in")
    ok = client.post(f"{API}/auth/login", data={"username": "a@upes.ac.in", "password": PASSWORD})
    assert ok.status_code == 200 and ok.json()["token_type"] == "bearer"
    wrong = client.post(f"{API}/auth/login", data={"username": "a@upes.ac.in", "password": "nope-nope-1"})
    unknown = client.post(f"{API}/auth/login", data={"username": "ghost@upes.ac.in", "password": PASSWORD})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()                       # does not reveal which emails exist


def test_me_requires_a_valid_token(client, alice):
    assert client.get(f"{API}/auth/me", headers=alice["h"]).json()["email"] == "alice@upes.ac.in"
    assert client.get(f"{API}/auth/me").status_code == 401
    assert client.get(f"{API}/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_expired_token_is_rejected(client, alice):
    expired = jwt.encode({"sub": str(alice["id"]), "exp": 1}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    r = client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401 and "expired" in r.json()["detail"]


def test_token_signed_with_another_secret_is_rejected(client, alice):
    forged = jwt.encode({"sub": str(alice["id"]), "exp": 9999999999}, "another-secret-another-secret-123456", algorithm="HS256")
    assert client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
