"""pytest -q"""
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path

_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_upload_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["UPLOAD_DIR"] = _upload_dir
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789abcdef"

import pytest
from fastapi.testclient import TestClient

import models
from database import SessionLocal
from main import app
from rate_limit import RateLimiter, login_limiter

PASSWORD = "Str0ngPass1"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64          # starts with the real PNG signature
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def fresh_limiter():
    login_limiter.reset()


def student_body(**over):
    body = {"name": "Aarav", "email": "aarav@upes.ac.in", "password": PASSWORD,
            "enrollment_date": "2022-08-01", "graduation_date": "2026-06-30"}
    body.update(over)
    return body


def fields(response):
    """Returns {field: message} from our standard 422 body."""
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["detail"] == "Validation failed"
    return {e["field"]: e["message"] for e in body["errors"]}


@pytest.fixture(scope="module")
def auth(client):
    out = {}
    for name in ("aarav", "diya"):
        r = client.post("/register", json=student_body(name=name.title(), email=f"{name}@upes.ac.in"))
        assert r.status_code == 201, r.text
        token = client.post("/login", data={"username": f"{name}@upes.ac.in", "password": PASSWORD}).json()["access_token"]
        out[name] = {"id": r.json()["id"], "h": {"Authorization": f"Bearer {token}"}}
    login_limiter.reset()
    return out


# ================= 1. Course validation: required, optional, custom validators =================
def test_valid_course_with_and_without_optional_fields(client, auth):
    h = auth["aarav"]["h"]
    minimal = client.post("/courses", json={"title": "Database Systems", "credits": 4}, headers=h)
    assert minimal.status_code == 201
    assert minimal.json()["description"] is None and minimal.json()["prerequisites"] == []
    full = client.post("/courses", headers=h, json={"title": "  Operating Systems  ", "credits": 4,
                                                    "description": "Processes and memory",
                                                    "prerequisites": ["CS101", "MA102"]})
    assert full.status_code == 201 and full.json()["title"] == "Operating Systems"    # whitespace trimmed
    assert client.get(f"/courses/{full.json()['id']}", headers=h).json()["prerequisites"] == ["CS101", "MA102"]


@pytest.mark.parametrize("body,field,fragment", [
    ({"credits": 4}, "title", "Field required"),
    ({"title": "Database"}, "credits", "Field required"),
    ({"title": "DB", "credits": 4}, "title", "at least 3 characters"),
    ({"title": "  ab  ", "credits": 4}, "title", "at least 3 characters"),
    ({"title": "12345", "credits": 4}, "title", "only numbers"),
    ({"title": "Database", "credits": 0}, "credits", "between 1 and 6"),
    ({"title": "Database", "credits": 7}, "credits", "between 1 and 6"),
    ({"title": "Database", "credits": "four"}, "credits", "whole number"),
    ({"title": "Database", "credits": True}, "credits", "must be a number"),
    ({"title": "Database", "credits": 4, "prerequisites": ["cs101"]}, "prerequisites", "invalid course code"),
    ({"title": "Database", "credits": 4, "prerequisites": ["CS101", "CS101"]}, "prerequisites", "duplicates"),
    ({"title": "Database", "credits": 4, "prerequisites": [f"CS10{i}" for i in range(6)]}, "prerequisites", "at most 5"),
    ({"title": "Database", "credits": 4, "description": "x" * 501}, "description", None),
    ({"title": "Database", "credits": 4, "internal": "x"}, "internal", "Extra inputs"),
])
def test_invalid_course_is_rejected(client, auth, body, field, fragment):
    errors = fields(client.post("/courses", json=body, headers=auth["aarav"]["h"]))
    matches = {f: m for f, m in errors.items() if f == field or f.startswith(field)}
    assert matches, f"expected an error on '{field}', got {errors}"
    if fragment:
        assert any(fragment.lower() in m.lower() for m in matches.values()), matches


def test_all_errors_are_reported_together(client, auth):
    errors = fields(client.post("/courses", json={"title": "x", "credits": 99, "prerequisites": ["bad"]},
                                headers=auth["aarav"]["h"]))
    assert {"title", "credits"} <= set(errors) and any(k.startswith("prerequisites") for k in errors)


def test_malformed_json_is_422_not_500(client, auth):
    r = client.post("/courses", content="{not json", headers={**auth["aarav"]["h"], "Content-Type": "application/json"})
    assert r.status_code == 422 and r.json()["detail"] == "Validation failed"


# ================= 2. Response model hides sensitive fields =================
def test_response_never_contains_sensitive_fields(client, auth):
    sid = auth["aarav"]["id"]
    with SessionLocal() as db:                                 # put a secret note on the database row
        db.get(models.Student, sid).internal_notes = "ON PROBATION - do not tell the student"
        db.commit()
    for response in (client.get(f"/students/{sid}", headers=auth["aarav"]["h"]),
                     client.patch(f"/students/{sid}", json={"name": "Aarav K"}, headers=auth["aarav"]["h"])):
        body = response.json()
        assert response.status_code == 200
        assert "hashed_password" not in body and "password" not in body and "internal_notes" not in body
        assert "PROBATION" not in response.text
        assert set(body) == {"id", "name", "email", "enrollment_date", "graduation_date", "has_photo"}
    reg = client.post("/register", json=student_body(email="new@upes.ac.in"))
    assert "password" not in reg.json() and "hashed_password" not in reg.json()


# ================= 3. Cross-field validation =================
def test_graduation_must_be_after_enrollment(client):
    msg = fields(client.post("/register", json=student_body(email="x1@upes.ac.in", graduation_date="2022-08-01")))
    assert "after enrollment_date" in msg["body"] or any("after enrollment_date" in m for m in msg.values())
    assert client.post("/register", json=student_body(email="x2@upes.ac.in", graduation_date="2021-01-01")).status_code == 422
    assert client.post("/register", json=student_body(email="x3@upes.ac.in", graduation_date="2022-08-02")).status_code == 201


def test_enrollment_date_cannot_be_in_the_future(client):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    errors = fields(client.post("/register", json=student_body(email="f@upes.ac.in", enrollment_date=tomorrow, graduation_date=None)))
    assert any("future" in m for m in errors.values())


def test_patch_checks_dates_against_stored_values(client, auth):
    h, sid = auth["diya"]["h"], auth["diya"]["id"]                 # stored: enrolled 2022-08-01, graduates 2026-06-30
    r = client.patch(f"/students/{sid}", json={"graduation_date": "2021-01-01"}, headers=h)   # only ONE date sent
    assert "after enrollment_date" in fields(r)["graduation_date"]
    ok = client.patch(f"/students/{sid}", json={"graduation_date": "2027-06-30"}, headers=h)
    assert ok.status_code == 200 and ok.json()["graduation_date"] == "2027-06-30"
    both = client.patch(f"/students/{sid}", json={"enrollment_date": "2030-01-01", "graduation_date": "2029-01-01"}, headers=h)
    assert both.status_code == 422


# ================= 4. Student input validation =================
@pytest.mark.parametrize("over,field", [
    ({"email": "not-an-email"}, "email"),
    ({"password": "short1"}, "password"),
    ({"password": "onlyletters"}, "password"),
    ({"password": "12345678"}, "password"),
    ({"name": ""}, "name"),
    ({"enrollment_date": "31-12-2022"}, "enrollment_date"),
    ({"role": "admin"}, "role"),                       # unknown field rejected, not ignored
    ({"internal_notes": "x"}, "internal_notes"),
])
def test_invalid_student_is_rejected(client, over, field):
    body = student_body(**{"email": "v@upes.ac.in", **over})
    assert field in fields(client.post("/register", json=body))


def test_duplicate_email_conflict(client, auth):
    assert client.post("/register", json=student_body(email="AARAV@upes.ac.in")).status_code == 409


# ================= 5. File upload with validation =================
def upload(client, who, content, name="me.png", ctype="image/png", sid=None):
    return client.post(f"/students/{sid or who['id']}/photo", headers=who["h"], files={"file": (name, content, ctype)})


def test_upload_png_and_jpeg(client, auth):
    who = auth["aarav"]
    r = upload(client, who, PNG)
    assert r.status_code == 200 and r.json()["has_photo"] is True
    assert (Path(_upload_dir) / f"student_{who['id']}.png").read_bytes() == PNG
    assert client.get(f"/students/{who['id']}/photo", headers=who["h"]).content == PNG
    r = upload(client, who, JPG, "me.jpg", "image/jpeg")                 # replaces the old photo
    assert r.status_code == 200
    assert not (Path(_upload_dir) / f"student_{who['id']}.png").exists()
    assert (Path(_upload_dir) / f"student_{who['id']}.jpg").exists()


def test_upload_rejections(client, auth):
    who = auth["aarav"]
    assert upload(client, who, b"%PDF-1.4 ...", "cv.pdf", "application/pdf").status_code == 415   # wrong type
    assert upload(client, who, b"GIF89a....", "a.gif", "image/gif").status_code == 415
    fake = upload(client, who, b"this is just text", "evil.png", "image/png")                     # lies about type
    assert fake.status_code == 400 and "not a valid PNG" in fake.json()["detail"]
    assert upload(client, who, JPG, "x.png", "image/png").status_code == 400                      # JPEG bytes, claims PNG
    assert upload(client, who, b"", "empty.png", "image/png").status_code == 400
    big = upload(client, who, PNG + b"\x00" * (2 * 1024 * 1024), "big.png", "image/png")
    assert big.status_code == 413 and "2 MB" in big.json()["detail"]
    just_ok = upload(client, who, PNG + b"\x00" * (2 * 1024 * 1024 - len(PNG)), "ok.png", "image/png")
    assert just_ok.status_code == 200                                                              # exactly 2 MB is allowed
    assert client.post(f"/students/{who['id']}/photo", headers=who["h"]).status_code == 422       # no file at all


def test_upload_permissions_and_safe_filenames(client, auth):
    a, b = auth["aarav"], auth["diya"]
    assert upload(client, a, PNG, sid=b["id"]).status_code == 403                  # cannot upload for someone else
    assert client.post(f"/students/{a['id']}/photo", files={"file": ("a.png", PNG, "image/png")}).status_code == 401
    r = upload(client, b, PNG, name="../../../../tmp/evil.png")                     # path traversal attempt
    assert r.status_code == 200
    assert sorted(p.name for p in Path(_upload_dir).iterdir() if p.name.startswith(f"student_{b['id']}"))
    assert not Path("/tmp/evil.png").exists()
    assert all(p.name.startswith("student_") for p in Path(_upload_dir).iterdir())


# ================= 6. Rate limiting on /login =================
def attempt(client, password="wrong-password-1"):
    return client.post("/login", data={"username": "aarav@upes.ac.in", "password": password})


def test_login_is_limited_to_5_attempts_per_minute(client, auth):
    codes = [attempt(client).status_code for _ in range(5)]
    assert codes == [401] * 5                                  # five normal (failed) attempts
    blocked = attempt(client)
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers["retry-after"]) <= 60
    assert "Too many login attempts" in blocked.json()["detail"]
    # even the CORRECT password is refused while blocked (otherwise the limit would be pointless)
    assert attempt(client, PASSWORD).status_code == 429


def test_successful_logins_count_too_and_headers_show_remaining(client, auth):
    first = attempt(client, PASSWORD)
    assert first.status_code == 200 and first.headers["x-ratelimit-remaining"] == "4"
    for _ in range(4):
        attempt(client, PASSWORD)
    assert attempt(client, PASSWORD).status_code == 429


def test_limit_does_not_affect_other_endpoints(client, auth):
    for _ in range(6):
        attempt(client)
    assert client.get(f"/students/{auth['aarav']['id']}", headers=auth["aarav"]["h"]).status_code == 200


def test_limiter_window_slides_with_a_fake_clock():
    now = [1000.0]
    limiter = RateLimiter(max_calls=5, window=60, clock=lambda: now[0])
    assert [limiter.check("ip")[0] for _ in range(5)] == [True] * 5
    allowed, remaining, retry = limiter.check("ip")
    assert (allowed, remaining) == (False, 0) and 1 <= retry <= 61
    assert limiter.check("other-ip")[0] is True                # separate counter per client
    now[0] += 59.9
    assert limiter.check("ip")[0] is False                      # still inside the minute
    now[0] += 0.2
    assert limiter.check("ip")[0] is True                       # the minute has passed, allowed again
