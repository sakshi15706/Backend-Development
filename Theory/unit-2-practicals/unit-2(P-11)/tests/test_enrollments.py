import pytest

from tests.conftest import API


@pytest.fixture
def catalogue(client, admin):
    for cid in ("CS301", "CS302"):
        assert client.post(f"{API}/courses", json={"id": cid, "title": f"Course {cid}", "credits": 4}, headers=admin["h"]).status_code == 201


def enroll(client, who, student_id, course="CS301"):
    return client.post(f"{API}/students/{student_id}/enrollments", headers=who["h"],
                       json={"course_id": course, "semester": "Fall 2024"})


def test_student_enrols_and_lists_own_courses(client, alice, catalogue):
    r = enroll(client, alice, alice["id"])
    assert r.status_code == 201 and r.json()["course"]["title"] == "Course CS301"
    enroll(client, alice, alice["id"], "CS302")
    listing = client.get(f"{API}/students/{alice['id']}/enrollments", headers=alice["h"]).json()
    assert [e["course_id"] for e in listing] == ["CS301", "CS302"]


def test_enrolment_errors(client, alice, bob, admin, catalogue):
    assert enroll(client, alice, alice["id"]).status_code == 201
    assert enroll(client, alice, alice["id"]).status_code == 409                   # already enrolled
    assert enroll(client, alice, alice["id"], "NOPE999").status_code == 404        # unknown course
    assert enroll(client, admin, 99999).status_code == 404                         # unknown student
    assert enroll(client, bob, alice["id"]).status_code == 403                     # someone else's record
    assert client.post(f"{API}/students/{alice['id']}/enrollments", json={"course_id": "CS301", "semester": "x"},
                       headers=alice["h"]).status_code == 422                      # semester too short
    assert client.get(f"{API}/students/{alice['id']}/enrollments", headers=bob["h"]).status_code == 403


def test_only_admin_sets_grades(client, alice, admin, catalogue):
    enroll(client, alice, alice["id"])
    url = f"{API}/students/{alice['id']}/enrollments/CS301"
    assert client.patch(url, json={"grade": "A"}, headers=alice["h"]).status_code == 403   # no self-grading
    ok = client.patch(url, json={"grade": "A"}, headers=admin["h"])
    assert ok.status_code == 200 and ok.json()["grade"] == "A"
    assert client.patch(url, json={"grade": "Z"}, headers=admin["h"]).status_code == 422
    assert client.patch(f"{API}/students/{alice['id']}/enrollments/CS302", json={"grade": "A"}, headers=admin["h"]).status_code == 404


def test_drop_course(client, alice, bob, catalogue):
    enroll(client, alice, alice["id"])
    url = f"{API}/students/{alice['id']}/enrollments/CS301"
    assert client.delete(url, headers=bob["h"]).status_code == 403
    assert client.delete(url, headers=alice["h"]).status_code == 204
    assert client.delete(url, headers=alice["h"]).status_code == 404
