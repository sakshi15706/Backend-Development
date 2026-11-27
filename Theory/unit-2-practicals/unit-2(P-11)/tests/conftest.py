import os
import tempfile

# Configure BEFORE the app is imported: tests use a throw-away database, never your real one.
_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_db.name}"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789abcdef"
os.environ["ENVIRONMENT"] = "test"

import bcrypt
import pytest
from fastapi.testclient import TestClient

from app import auth, models
from app.database import Base, SessionLocal, engine
from app.main import app

PASSWORD = "Str0ngPass!"
API = "/api/v1"


@pytest.fixture(autouse=True)
def fast_bcrypt(monkeypatch):
    """bcrypt is slow on purpose; a low cost factor keeps the test-suite fast."""
    monkeypatch.setattr(auth, "hash_password",
                        lambda pw: bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=4)).decode())


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def make_user(email: str, role: str = "student", name: str | None = None, branch: str = "CSE") -> int:
    """Inserts a user straight into the database (admins cannot self-register)."""
    with SessionLocal() as db:
        user = models.Student(name=name or email.split("@")[0].title(), email=email, branch=branch, role=role,
                              hashed_password=auth.hash_password(PASSWORD))
        db.add(user)
        db.commit()
        return user.id


def login_headers(client, email: str) -> dict:
    r = client.post(f"{API}/auth/login", data={"username": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin(client):
    uid = make_user("admin@upes.ac.in", "admin")
    return {"id": uid, "h": login_headers(client, "admin@upes.ac.in")}


@pytest.fixture
def alice(client):
    uid = make_user("alice@upes.ac.in")
    return {"id": uid, "h": login_headers(client, "alice@upes.ac.in")}


@pytest.fixture
def bob(client):
    uid = make_user("bob@upes.ac.in", branch="ECE")
    return {"id": uid, "h": login_headers(client, "bob@upes.ac.in")}
