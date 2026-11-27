"""pytest -q   (authorization matrix: who may do what)"""
import logging
import os
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789abcdef"

import pytest
from fastapi.testclient import TestClient

import auth
import models
from database import SessionLocal
from main import app
from permissions import ROLE_PERMISSIONS

PASSWORD = "Str0ngPass!"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def make_user(email, role, name=None):
    with SessionLocal() as db:
        u = models.Student(name=name or email.split("@")[0].title(), email=email, branch="CSE", role=role,
                           hashed_password=auth.hash_password(PASSWORD))
        db.add(u)
        db.commit()
        return u.id


@pytest.fixture(scope="module")
def world(client):
    ids = {"admin": make_user("admin@upes.ac.in", "admin"),
           "faculty": make_user("faculty@upes.ac.in", "faculty"),
           "alice": make_user("alice@upes.ac.in", "student"),
           "bob": make_user("bob@upes.ac.in", "student")}
    tokens = {}
    for key in ids:
        r = client.post("/login", data={"username": f"{key}@upes.ac.in", "password": PASSWORD})
        assert r.status_code == 200, r.text
        tokens[key] = {"Authorization": f"Bearer {r.json()['access_token']}"}
    # seed data created by the admin
    assert client.post("/departments", json={"name": "CS"}, headers=tokens["admin"]).status_code == 201
    assert client.post("/courses", json={"id": "CS301", "title": "DB", "credits": 4, "department_id": 1},
                       headers=tokens["admin"]).status_code == 201
    r = client.post(f"/students/{ids['alice']}/enrollments", json={"course_id": "CS301", "semester": "Fall 2024"},
                    headers=tokens["alice"])
    assert r.status_code == 201
    return {"ids": ids, "h": tokens}


def call(client, world, who, method, path, **kw):
    path = path.format(**{k: v for k, v in world["ids"].items()})
    return getattr(client, method)(path, headers=world["h"][who], **kw)


# (method, path, body, {who: expected status}) : the authorization matrix
MATRIX = [
    ("get",   "/students",                        None,                {"admin": 200, "faculty": 200, "alice": 403, "bob": 403}),
    ("get",   "/students/{alice}",                None,                {"admin": 200, "faculty": 200, "alice": 200, "bob": 403}),
    ("patch", "/students/{alice}",                {"name": "Alice A"}, {"admin": 200, "faculty": 403, "alice": 200, "bob": 403}),
    ("get",   "/courses",                         None,                {"admin": 200, "faculty": 200, "alice": 200, "bob": 200}),
    ("get",   "/courses/CS301",                   None,                {"admin": 200, "faculty": 200, "alice": 200, "bob": 200}),
    ("get",   "/departments",                     None,                {"admin": 200, "faculty": 200, "alice": 200, "bob": 200}),
    ("get",   "/students/{alice}/enrollments",    None,                {"admin": 200, "faculty": 200, "alice": 200, "bob": 403}),
    ("patch", "/students/{alice}/enrollments/CS301", {"grade": "A"},   {"admin": 200, "faculty": 200, "alice": 403, "bob": 403}),
    ("post",  "/departments",                     {"name": "X-dept"},  {"admin": 201, "faculty": 403, "alice": 403, "bob": 403}),
    ("patch", "/users/{bob}/role",                {"role": "student"}, {"admin": 200, "faculty": 403, "alice": 403, "bob": 403}),
    ("delete", "/courses/NOPE999",                None,                {"admin": 404, "faculty": 403, "alice": 403, "bob": 403}),
    ("delete", "/students/999999",                None,                {"admin": 404, "faculty": 403, "alice": 403, "bob": 403}),
]


@pytest.mark.parametrize("method,path,body,expected", MATRIX, ids=[f"{m.upper()} {p}" for m, p, _, _ in MATRIX])
def test_authorization_matrix(client, world, method, path, body, expected):
    for who, status in expected.items():
        r = call(client, world, who, method, path, **({"json": body} if body is not None else {}))
        assert r.status_code == status, f"{who}: {method.upper()} {path} -> {r.status_code} (expected {status}) {r.text}"


def test_unauthenticated_is_401_not_403(client, world):
    assert client.get("/students").status_code == 401
    assert client.delete("/students/1").status_code == 401


def test_create_course_admin_only(client, world):
    body = {"id": "CS302", "title": "OS", "credits": 4}
    assert call(client, world, "faculty", "post", "/courses", json=body).status_code == 403
    assert call(client, world, "alice", "post", "/courses", json=body).status_code == 403
    assert call(client, world, "admin", "post", "/courses", json=body).status_code == 201
    assert call(client, world, "faculty", "delete", "/courses/CS302").status_code == 403
    assert call(client, world, "admin", "delete", "/courses/CS302").status_code == 204


def test_only_admin_can_delete_students(client, world):
    victim = make_user("victim@upes.ac.in", "student")
    for who in ("faculty", "alice", "bob"):
        assert call(client, world, who, "delete", f"/students/{victim}").status_code == 403
    assert call(client, world, "admin", "delete", f"/students/{victim}").status_code == 204


def test_student_self_service(client, world):
    ids = world["ids"]
    # enrolling: own record only, and no self-awarded grades
    ok = call(client, world, "bob", "post", f"/students/{ids['bob']}/enrollments",
              json={"course_id": "CS301", "semester": "Fall 2024"})
    assert ok.status_code == 201
    assert call(client, world, "bob", "post", f"/students/{ids['alice']}/enrollments",
                json={"course_id": "CS301", "semester": "Fall 2025"}).status_code == 403
    cheat = call(client, world, "alice", "post", f"/students/{ids['alice']}/enrollments",
                 json={"course_id": "CS301", "semester": "Fall 2025", "grade": "A+"})
    assert cheat.status_code == 403 and "grades:write" in cheat.json()["detail"]
    assert call(client, world, "bob", "delete", f"/students/{ids['bob']}/enrollments/CS301").status_code == 204


def test_students_cannot_escalate_privileges(client, world):
    ids = world["ids"]
    # a role field in a profile update is ignored, the role never changes
    r = call(client, world, "alice", "patch", f"/students/{ids['alice']}", json={"role": "admin"})
    assert r.status_code == 200 and r.json()["role"] == "student"
    # registration cannot create an admin either
    reg = client.post("/register", json={"name": "Evil", "email": "evil@upes.ac.in", "branch": "CSE",
                                         "password": PASSWORD, "role": "admin"})
    assert reg.status_code == 201 and reg.json()["role"] == "student"
    assert call(client, world, "alice", "patch", f"/users/{ids['alice']}/role", json={"role": "admin"}).status_code == 403


def test_admin_role_management(client, world):
    ids = world["ids"]
    assert call(client, world, "admin", "patch", f"/users/{ids['admin']}/role", json={"role": "student"}).status_code == 409
    assert call(client, world, "admin", "patch", "/users/999999/role", json={"role": "faculty"}).status_code == 404
    assert call(client, world, "admin", "patch", f"/users/{ids['bob']}/role", json={"role": "superuser"}).status_code == 422


def test_role_change_applies_immediately_with_the_old_token(client, world):
    ids = world["ids"]
    assert call(client, world, "bob", "get", "/students").status_code == 403            # student: forbidden
    call(client, world, "admin", "patch", f"/users/{ids['bob']}/role", json={"role": "faculty"})
    assert call(client, world, "bob", "get", "/students").status_code == 200            # same token, now faculty
    call(client, world, "admin", "patch", f"/users/{ids['bob']}/role", json={"role": "student"})
    assert call(client, world, "bob", "get", "/students").status_code == 403            # demotion also immediate


def test_my_permissions_endpoint(client, world):
    for who, role in (("admin", "admin"), ("faculty", "faculty"), ("alice", "student")):
        body = call(client, world, who, "get", "/me/permissions").json()
        assert body["role"] == role and set(body["permissions"]) == ROLE_PERMISSIONS[role]


def test_least_privilege_and_deny_by_default():
    assert "students:delete" not in ROLE_PERMISSIONS["faculty"] | ROLE_PERMISSIONS["student"]
    assert "roles:manage" not in ROLE_PERMISSIONS["faculty"] | ROLE_PERMISSIONS["student"]
    assert "grades:write" not in ROLE_PERMISSIONS["student"]
    admin = ROLE_PERMISSIONS["admin"]
    assert ROLE_PERMISSIONS["faculty"] <= admin                                  # admin can do everything faculty can
    assert {p for p in ROLE_PERMISSIONS["student"] if not p.endswith("_own")} <= admin
    assert all(p.endswith("_own") or p == "courses:read" for p in ROLE_PERMISSIONS["student"])  # students: own data + catalogue


def test_unknown_role_gets_nothing(client, world):
    with SessionLocal() as db:
        u = db.get(models.Student, world["ids"]["bob"])
        u.role = "hacker"
        db.commit()
    assert call(client, world, "bob", "get", "/courses").status_code == 403
    with SessionLocal() as db:
        u = db.get(models.Student, world["ids"]["bob"])
        u.role = "student"
        db.commit()


def test_audit_log_records_decisions(client, world, caplog):
    with caplog.at_level(logging.INFO, logger="authz"):
        call(client, world, "alice", "get", "/students")
        call(client, world, "faculty", "get", "/students")
    text = caplog.text
    assert "DENY" in text and "ALLOW" in text and "students:read" in text
