from app import models
from app.database import SessionLocal
from tests.conftest import API, make_user


def seed_students(n):
    with SessionLocal() as db:
        db.add_all(models.Student(name=f"Student {i:02}", email=f"s{i}@upes.ac.in", hashed_password="x",
                                  branch="CSE" if i % 2 else "ECE") for i in range(1, n + 1))
        db.commit()


def test_list_is_admin_only(client, admin, alice):
    assert client.get(f"{API}/students").status_code == 401
    assert client.get(f"{API}/students", headers=alice["h"]).status_code == 403
    assert client.get(f"{API}/students", headers=admin["h"]).status_code == 200


def test_pagination_filter_and_search(client, admin):
    seed_students(25)
    page = client.get(f"{API}/students?limit=10", headers=admin["h"]).json()
    assert (page["page"], page["limit"], page["total"], page["total_pages"], len(page["items"])) == (1, 10, 26, 3, 10)
    assert len(client.get(f"{API}/students?limit=10&page=3", headers=admin["h"]).json()["items"]) == 6
    assert client.get(f"{API}/students?branch=ECE", headers=admin["h"]).json()["total"] == 12
    assert client.get(f"{API}/students?search=student 07", headers=admin["h"]).json()["total"] == 1
    assert client.get(f"{API}/students?limit=1000", headers=admin["h"]).status_code == 422
    assert client.get(f"{API}/students?page=0", headers=admin["h"]).status_code == 422
    assert client.get(f"{API}/students?branch=XYZ", headers=admin["h"]).status_code == 422


def test_students_see_only_their_own_record(client, alice, bob, admin):
    assert client.get(f"{API}/students/{alice['id']}", headers=alice["h"]).status_code == 200
    assert client.get(f"{API}/students/{bob['id']}", headers=alice["h"]).status_code == 403
    assert client.get(f"{API}/students/{bob['id']}", headers=admin["h"]).status_code == 200
    assert client.get(f"{API}/students/99999", headers=admin["h"]).status_code == 404
    assert client.get(f"{API}/students/99999", headers=alice["h"]).status_code == 403   # no existence leak


def test_update_own_profile_only(client, alice, bob):
    ok = client.patch(f"{API}/students/{alice['id']}", json={"name": "Alice A", "branch": "IT"}, headers=alice["h"])
    assert ok.status_code == 200 and ok.json()["name"] == "Alice A" and ok.json()["branch"] == "IT"
    assert client.patch(f"{API}/students/{bob['id']}", json={"name": "Hacked"}, headers=alice["h"]).status_code == 403
    assert client.patch(f"{API}/students/{alice['id']}", json={"branch": "BCA"}, headers=alice["h"]).status_code == 422


def test_role_cannot_be_changed_through_update(client, alice):
    r = client.patch(f"{API}/students/{alice['id']}", json={"role": "admin"}, headers=alice["h"])
    assert r.status_code == 200 and r.json()["role"] == "student"


def test_delete_is_admin_only_and_cascades(client, admin, alice):
    assert client.post(f"{API}/courses", json={"id": "CS301", "title": "Databases", "credits": 4}, headers=admin["h"]).status_code == 201
    client.post(f"{API}/students/{alice['id']}/enrollments", json={"course_id": "CS301", "semester": "Fall 2024"}, headers=alice["h"])
    assert client.delete(f"{API}/students/{alice['id']}", headers=alice["h"]).status_code == 403
    assert client.delete(f"{API}/students/{alice['id']}", headers=admin["h"]).status_code == 204
    assert client.delete(f"{API}/students/{alice['id']}", headers=admin["h"]).status_code == 404
    with SessionLocal() as db:
        assert db.query(models.Enrollment).count() == 0                     # enrollments removed
        assert db.query(models.Course).count() == 1                         # course kept
