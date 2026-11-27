"""Tests every CRUD, filter and pagination requirement.   Run:  pytest -q"""
import os
import tempfile

# use a throw-away database file so tests never touch school.db
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def depts(client):
    cse = client.post("/departments", json={"name": "Computer Science"}).json()
    ece = client.post("/departments", json={"name": "Electronics"}).json()
    return cse["id"], ece["id"]


def test_create_course(client, depts):
    r = client.post("/courses", json={"code": "CS301", "title": "Database Systems", "credits": 4, "department_id": depts[0]})
    assert r.status_code == 201
    assert r.json()["code"] == "CS301"


def test_duplicate_code_conflict(client, depts):
    r = client.post("/courses", json={"code": "CS301", "title": "Dup", "credits": 3})
    assert r.status_code == 409


def test_validation_errors(client):
    assert client.post("/courses", json={"code": "CS999", "title": "Bad", "credits": 9}).status_code == 422
    assert client.post("/courses", json={"code": "CS999", "title": "", "credits": 3}).status_code == 422


def test_unknown_department(client):
    r = client.post("/courses", json={"code": "XX100", "title": "X", "credits": 3, "department_id": 999})
    assert r.status_code == 404


def test_read_update_delete(client, depts):
    cid = client.post("/courses", json={"code": "CS302", "title": "Operating Systems", "credits": 4, "department_id": depts[0]}).json()["id"]
    assert client.get(f"/courses/{cid}").json()["title"] == "Operating Systems"
    r = client.put(f"/courses/{cid}", json={"credits": 3})
    assert r.status_code == 200 and r.json()["credits"] == 3
    assert client.delete(f"/courses/{cid}").status_code == 204
    assert client.get(f"/courses/{cid}").status_code == 404


def test_filter_and_pagination(client, depts):
    cse, ece = depts
    for i in range(25):  # 25 more courses: 15 in CSE with 4 credits, 10 in ECE with 3 credits
        client.post("/courses", json={
            "code": f"PG{i:03}", "title": f"Course {i}",
            "credits": 4 if i < 15 else 3, "department_id": cse if i < 15 else ece})

    page1 = client.get("/courses").json()
    assert page1["limit"] == 10 and len(page1["items"]) == 10          # 10 per page
    assert page1["total"] >= 26 and page1["total_pages"] == -(-page1["total"] // 10)
    assert client.get("/courses?page=2").json()["items"][0]["code"] != page1["items"][0]["code"]

    by_dept = client.get(f"/courses?department_id={ece}").json()
    assert by_dept["total"] == 10 and all(c["department_id"] == ece for c in by_dept["items"])

    by_credits = client.get("/courses?credits=3").json()
    assert all(c["credits"] == 3 for c in by_credits["items"])

    both = client.get(f"/courses?department_id={cse}&credits=4").json()
    assert both["total"] >= 15 and all(c["credits"] == 4 and c["department_id"] == cse for c in both["items"])

    assert client.get("/courses?page=0").status_code == 422
    assert client.get("/courses?limit=500").status_code == 422


def test_student_with_department(client, depts):
    r = client.post("/students", json={"name": "Aarav", "email": "aarav@upes.ac.in", "branch": "CSE",
                                       "enrollment_date": "2024-08-01", "department_id": depts[0]})
    assert r.status_code == 201
    sid = r.json()["id"]
    body = client.get(f"/students/{sid}").json()
    assert body["department"]["name"] == "Computer Science"            # related data included

    assert client.post("/students", json={"name": "Dup", "email": "aarav@upes.ac.in", "branch": "CSE"}).status_code == 409
    assert client.post("/students", json={"name": "Bad", "email": "not-an-email", "branch": "XYZ"}).status_code == 422

    assert client.put(f"/students/{sid}", json={"branch": "ECE"}).json()["branch"] == "ECE"
    listing = client.get(f"/students?department_id={depts[0]}").json()
    assert listing["total"] == 1 and listing["items"][0]["department"]["name"] == "Computer Science"
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404
