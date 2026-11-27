"""pytest -q    (covers the whole authentication flow from the lab exercise)"""
import os
import tempfile
import time
from datetime import timedelta

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789abcdef"

import jwt
import pytest
from fastapi.testclient import TestClient

import auth
import models
from database import SessionLocal
from main import app

PASSWORD = "Str0ngPass!"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def register(client, name, email, **extra):
    return client.post("/register", json={"name": name, "email": email, "branch": "CSE",
                                           "password": PASSWORD, **extra})


def login(client, email, password=PASSWORD):
    return client.post("/login", data={"username": email, "password": password})


def headers(client, email):
    return {"Authorization": f"Bearer {login(client, email).json()['access_token']}"}


@pytest.fixture(scope="module")
def users(client):
    ids = {}
    for name in ("aarav", "diya"):
        r = register(client, name.title(), f"{name}@upes.ac.in")
        assert r.status_code == 201, r.text
        ids[name] = r.json()["id"]
    with SessionLocal() as db:                                   # admin created directly in the DB
        admin = models.Student(name="Admin", email="admin@upes.ac.in", branch="CSE", role="admin",
                               hashed_password=auth.hash_password("Admin@12345"))
        db.add(admin)
        db.commit()
        ids["admin"] = admin.id
    return ids


# ---------------------------- Step 1: register ----------------------------
def test_register(client, users):
    r = register(client, "Rohan", "rohan@upes.ac.in")
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "student"
    assert "password" not in body and "hashed_password" not in body        # never returned
    assert register(client, "Dup", "ROHAN@upes.ac.in").status_code == 409
    assert client.post("/register", json={"name": "W", "email": "w@x.com", "branch": "CSE", "password": "short"}).status_code == 422


def test_password_is_hashed_in_database(client, users):
    with SessionLocal() as db:
        stored = db.query(models.Student).filter_by(email="aarav@upes.ac.in").one().hashed_password
    assert stored != PASSWORD and stored.startswith("$2")                  # bcrypt hash


def test_cannot_register_as_admin(client, users):
    r = register(client, "Evil", "evil@upes.ac.in", role="admin")
    assert r.status_code == 201 and r.json()["role"] == "student"


# ---------------------------- Step 2: login ----------------------------
def test_login(client, users):
    r = login(client, "aarav@upes.ac.in")
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer" and r.json()["access_token"]
    payload = jwt.decode(r.json()["access_token"], auth.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == str(users["aarav"]) and payload["role"] == "student" and "exp" in payload
    assert login(client, "AARAV@upes.ac.in").status_code == 200            # email is case-insensitive


def test_login_failures(client, users):
    wrong = login(client, "aarav@upes.ac.in", "wrong-password")
    unknown = login(client, "nobody@upes.ac.in")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()                                  # no user-enumeration hint
    assert wrong.headers["www-authenticate"] == "Bearer"


# ---------------------------- Step 3 and 4: protected routes ----------------------------
PROTECTED = [("get", "/me"), ("get", "/students"), ("get", "/students/1"), ("put", "/students/1"),
             ("patch", "/students/1"), ("delete", "/students/1"), ("get", "/courses"), ("get", "/courses/CS301"),
             ("post", "/courses"), ("get", "/departments"), ("post", "/departments"),
             ("get", "/students/1/enrollments"), ("post", "/students/1/enrollments"),
             ("patch", "/students/1/enrollments/CS301"), ("delete", "/students/1/enrollments/CS301")]


@pytest.mark.parametrize("method,path", PROTECTED)
def test_no_token_gives_401(client, users, method, path):
    r = getattr(client, method)(path)
    assert r.status_code == 401, f"{method.upper()} {path} returned {r.status_code}"


def test_access_with_token(client, users):
    h = headers(client, "aarav@upes.ac.in")
    assert client.get("/me", headers=h).json()["email"] == "aarav@upes.ac.in"
    assert client.get("/students", headers=h).status_code == 200


def test_garbage_and_tampered_tokens(client, users):
    assert client.get("/me", headers={"Authorization": "Bearer not.a.token"}).status_code == 401
    token = login(client, "aarav@upes.ac.in").json()["access_token"]
    forged = jwt.encode({"sub": str(users["admin"]), "role": "admin", "exp": time.time() + 600},
                        "wrong-secret-key-wrong-secret-key-123", algorithm="HS256")
    assert client.get("/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
    assert client.get("/me", headers={"Authorization": f"Basic {token}"}).status_code == 401


# ---------------------------- Step 5: DELETE rule ----------------------------
def test_delete_rules(client, users):
    victim = register(client, "Victim", "victim@upes.ac.in").json()["id"]
    attacker_h = headers(client, "diya@upes.ac.in")
    assert client.delete(f"/students/{victim}", headers=attacker_h).status_code == 403    # another student
    assert client.delete("/students/999999", headers=attacker_h).status_code == 403        # no existence leak
    assert client.get(f"/students/{victim}", headers=attacker_h).status_code == 200        # still there

    own_h = headers(client, "victim@upes.ac.in")
    assert client.delete(f"/students/{victim}", headers=own_h).status_code == 204          # self
    assert client.get("/me", headers=own_h).status_code == 401                              # token of deleted user dies

    other = register(client, "Other", "other@upes.ac.in").json()["id"]
    admin_token = login(client, "admin@upes.ac.in", "Admin@12345").json()["access_token"]
    admin_h = {"Authorization": f"Bearer {admin_token}"}
    assert client.delete(f"/students/{other}", headers=admin_h).status_code == 204          # admin
    assert client.delete(f"/students/{other}", headers=admin_h).status_code == 404          # admin, already gone


def test_students_cannot_edit_others(client, users):
    h = headers(client, "diya@upes.ac.in")
    assert client.patch(f"/students/{users['aarav']}", json={"name": "Hacked"}, headers=h).status_code == 403
    assert client.patch(f"/students/{users['diya']}", json={"name": "Diya D"}, headers=h).status_code == 200


# ---------------------------- Step 6: token expiry ----------------------------
def test_expired_token_is_rejected(client, users):
    with SessionLocal() as db:
        user = db.get(models.Student, users["aarav"])
        expired = auth.create_access_token(user, expires_delta=timedelta(seconds=-5))
    r = client.get("/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401 and "expired" in r.json()["detail"].lower()


def test_token_really_expires_after_waiting(client, users):
    with SessionLocal() as db:
        short = auth.create_access_token(db.get(models.Student, users["aarav"]), expires_delta=timedelta(seconds=1))
    h = {"Authorization": f"Bearer {short}"}
    assert client.get("/me", headers=h).status_code == 200      # valid right now
    time.sleep(2.2)
    r = client.get("/me", headers=h)                            # same token, 2 seconds later
    assert r.status_code == 401 and "expired" in r.json()["detail"].lower()
