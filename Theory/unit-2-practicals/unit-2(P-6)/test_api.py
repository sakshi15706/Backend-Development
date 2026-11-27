"""pytest -q"""
import os
import tempfile

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
def setup(client):
    cse = client.post("/departments", json={"name": "Computer Science"}).json()["id"]
    ece = client.post("/departments", json={"name": "Electronics"}).json()["id"]
    for cid, title in (("CS301", "Database Systems"), ("CS302", "Operating Systems")):
        assert client.post("/courses", json={"id": cid, "title": title, "credits": 4, "department_id": cse}).status_code == 201
    people = [("Aarav", "CSE", cse), ("Diya", "ECE", ece), ("Rohan", "IT", cse), ("Priya", "CSE", cse)]
    for i in range(1, 16):                      # 15 extra students so pagination has several pages
        people.append((f"Student{i:02}", "ME", ece))
    ids = {}
    for name, branch, dept in people:
        r = client.post("/students", json={"name": name, "email": f"{name.lower()}@upes.ac.in",
                                           "branch": branch, "department_id": dept, "enrollment_date": "2024-08-01"})
        assert r.status_code == 201, r.text
        ids[name] = r.json()["id"]
    return {"cse": cse, "ece": ece, "ids": ids}


def test_get_update_delete(client, setup):
    sid = setup["ids"]["Rohan"]
    assert client.get(f"/students/{sid}").json()["department"]["name"] == "Computer Science"
    assert client.patch(f"/students/{sid}", json={"branch": "ECE"}).json()["branch"] == "ECE"
    put = client.put(f"/students/{sid}", json={"name": "Rohan K", "email": "rohan@upes.ac.in", "branch": "IT"})
    assert put.status_code == 200 and put.json()["name"] == "Rohan K"
    assert client.put(f"/students/{sid}", json={"name": "Only name"}).status_code == 422   # PUT needs all fields


def test_filtering(client, setup):
    assert client.get("/students?branch=CSE").json()["total"] == 2
    assert client.get(f"/students?department_id={setup['ece']}").json()["total"] == 16     # Diya + 15 ME
    assert client.get("/students?search=priya").json()["total"] == 1
    assert client.get("/students?search=UPES.AC.IN&branch=ECE").json()["total"] == 1       # case-insensitive, combined
    assert client.get("/students?branch=XYZ").status_code == 422


def test_pagination(client, setup):
    p = client.get("/students?limit=5").json()
    assert set(p) == {"items", "page", "limit", "total", "total_pages"}
    assert p["total"] == 19 and p["total_pages"] == 4 and len(p["items"]) == 5
    last = client.get("/students?limit=5&page=4").json()
    assert len(last["items"]) == 4
    names = [s["name"] for pg in range(1, 5) for s in client.get(f"/students?limit=5&page={pg}").json()["items"]]
    assert len(names) == len(set(names)) == 19                                             # no overlaps
    assert client.get("/students?page=0").status_code == 422


def test_courses(client, setup):
    assert client.post("/courses", json={"id": "CS301", "title": "Dup", "credits": 3}).status_code == 409
    assert client.post("/courses", json={"id": "cs3", "title": "Bad id", "credits": 3}).status_code == 422
    assert client.post("/courses", json={"id": "CS399", "title": "X", "credits": 7}).status_code == 422
    assert client.post("/courses", json={"id": "CS398", "title": "X", "credits": 3, "department_id": 999}).status_code == 404
    assert client.get("/courses/CS301").json()["title"] == "Database Systems"
    assert client.get("/courses/NOPE1").status_code == 404
    assert client.get(f"/courses?department_id={setup['cse']}&credits=4").json()["total"] == 2


def test_nested_enrollments(client, setup):
    sid = setup["ids"]["Aarav"]
    r = client.post(f"/students/{sid}/enrollments", json={"course_id": "CS301", "semester": "Fall 2024"})
    assert r.status_code == 201 and r.json()["course"]["title"] == "Database Systems"
    assert client.post(f"/students/{sid}/enrollments", json={"course_id": "CS301", "semester": "Fall 2024"}).status_code == 409
    assert client.post(f"/students/{sid}/enrollments", json={"course_id": "NOPE1", "semester": "Fall 2024"}).status_code == 404
    assert client.post("/students/9999/enrollments", json={"course_id": "CS301", "semester": "Fall 2024"}).status_code == 404
    assert client.post(f"/students/{sid}/enrollments", json={"course_id": "CS302", "semester": "Fall 2024", "grade": "Z"}).status_code == 422
    client.post(f"/students/{sid}/enrollments", json={"course_id": "CS302", "semester": "Fall 2024"})
    assert len(client.get(f"/students/{sid}/enrollments").json()) == 2
    assert client.patch(f"/students/{sid}/enrollments/CS301", json={"grade": "A"}).json()["grade"] == "A"
    assert client.delete(f"/students/{sid}/enrollments/CS302").status_code == 204
    assert len(client.get(f"/students/{sid}/enrollments").json()) == 1


def test_error_handling(client, setup):
    assert client.get("/students/9999").status_code == 404
    assert client.get("/students/abc").status_code == 422
    assert client.post("/students", json={"name": "Dup", "email": "AARAV@upes.ac.in", "branch": "CSE"}).status_code == 409
    assert client.post("/students", json={"name": "", "email": "x", "branch": "BCA"}).status_code == 422
    assert client.post("/students", json={"name": "N", "email": "n@x.com", "branch": "CSE", "department_id": 999}).status_code == 404
    body = client.get("/students/9999").json()
    assert "detail" in body


def test_delete_cascades_to_enrollments(client, setup):
    sid = setup["ids"]["Aarav"]
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404
    assert client.get(f"/students/{sid}/enrollments").status_code == 404
    assert client.get("/courses/CS301").status_code == 200       # courses are untouched


def test_swagger_available(client):
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json").json()
    assert "/students/{student_id}/enrollments" in spec["paths"]
