import pytest

from app.config import DEV_SECRET, Settings


def test_postgres_url_is_normalised_for_sqlalchemy():
    s = Settings(DATABASE_URL="postgres://user:pw@host:5432/db", SECRET_KEY="x" * 40)
    assert s.DATABASE_URL.startswith("postgresql://") and not s.is_sqlite


def test_production_refuses_the_public_development_secret():
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT="production", SECRET_KEY=DEV_SECRET)
    assert Settings(ENVIRONMENT="production", SECRET_KEY="a-private-value-" * 3).ENVIRONMENT == "production"


def test_settings_read_environment_variables(monkeypatch):
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5")
    assert Settings().ACCESS_TOKEN_EXPIRE_MINUTES == 5


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_swagger_documents_errors_and_tags(client):
    assert client.get("/docs").status_code == 200 and client.get("/redoc").status_code == 200
    spec = client.get("/openapi.json").json()
    assert {"Auth", "Students", "Courses", "Enrollments"} <= {t["name"] for t in spec["tags"]}
    assert "409" in spec["paths"]["/api/v1/courses"]["post"]["responses"]
    assert "404" in spec["paths"]["/api/v1/students/{student_id}"]["get"]["responses"]
    assert spec["info"]["title"] == "Student Management API"


def test_ensure_admin_creates_once_and_never_overwrites(client):
    from app import models
    from app.bootstrap import ensure_admin
    from app.database import SessionLocal
    from tests.conftest import API, PASSWORD

    with SessionLocal() as db:
        assert ensure_admin(db, "Boss@upes.ac.in", PASSWORD) is True
        assert ensure_admin(db, "boss@upes.ac.in", "different-Password-9") is False   # second run: no change
        assert db.query(models.Student).filter_by(role="admin").count() == 1
    ok = client.post(f"{API}/auth/login", data={"username": "boss@upes.ac.in", "password": PASSWORD})
    assert ok.status_code == 200                                                       # original password still works
    token = {"Authorization": f"Bearer {ok.json()['access_token']}"}
    assert client.get(f"{API}/students", headers=token).status_code == 200            # and it really is an admin
