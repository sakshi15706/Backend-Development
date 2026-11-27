from tests.conftest import API


def course(id="CS301", **over):
    return {"id": id, "title": "Database Systems", "credits": 4, **over}


def test_only_admin_creates_courses(client, admin, alice):
    assert client.post(f"{API}/courses", json=course()).status_code == 401
    assert client.post(f"{API}/courses", json=course(), headers=alice["h"]).status_code == 403
    r = client.post(f"{API}/courses", json=course(), headers=admin["h"])
    assert r.status_code == 201 and r.json()["id"] == "CS301"


def test_duplicate_and_invalid_courses(client, admin):
    assert client.post(f"{API}/courses", json=course(), headers=admin["h"]).status_code == 201
    assert client.post(f"{API}/courses", json=course(), headers=admin["h"]).status_code == 409
    for bad in (course("cs3"), course("CS302", credits=0), course("CS303", credits=7), course("CS304", title="DB")):
        assert client.post(f"{API}/courses", json=bad, headers=admin["h"]).status_code == 422, bad


def test_list_filter_and_get(client, admin, alice):
    for i, credits in enumerate([3, 3, 4, 4, 4, 2]):
        client.post(f"{API}/courses", json=course(f"CS30{i}", credits=credits), headers=admin["h"])
    everyone = client.get(f"{API}/courses", headers=alice["h"]).json()          # students may read the catalogue
    assert everyone["total"] == 6
    assert client.get(f"{API}/courses?credits=4", headers=alice["h"]).json()["total"] == 3
    assert client.get(f"{API}/courses?limit=2&page=3", headers=alice["h"]).json()["items"][0]["id"] == "CS304"
    assert client.get(f"{API}/courses/CS301", headers=alice["h"]).json()["credits"] == 3
    assert client.get(f"{API}/courses/NOPE999", headers=alice["h"]).status_code == 404
    assert client.get(f"{API}/courses").status_code == 401


def test_delete_course(client, admin, alice):
    client.post(f"{API}/courses", json=course(), headers=admin["h"])
    assert client.delete(f"{API}/courses/CS301", headers=alice["h"]).status_code == 403
    assert client.delete(f"{API}/courses/CS301", headers=admin["h"]).status_code == 204
    assert client.delete(f"{API}/courses/CS301", headers=admin["h"]).status_code == 404
