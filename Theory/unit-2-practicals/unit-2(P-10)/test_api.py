"""pytest -q"""
import json
import os
import re
import tempfile
from email.utils import parsedate_to_datetime
from pathlib import Path

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest
from fastapi.testclient import TestClient

import generate_postman
from main import app



@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def make(client, i, branch="CSE", version="v2"):
    return client.post(f"/api/{version}/students", json={
        "name": f"Student {i:02}", "email": f"s{i}@upes.ac.in", "branch": branch, "enrollment_date": "2024-08-01"})


# =========================== versioned endpoints ===========================
def test_v1_returns_basic_plain_array(client):
    assert make(client, 1, version="v1").status_code == 201
    r = client.get("/api/v1/students")
    body = r.json()
    assert isinstance(body, list)                                       # no envelope
    assert set(body[0]) == {"id", "name", "email", "branch"}            # basic fields only


def test_v2_returns_paginated_enhanced_response(client):
    for i in range(2, 26):
        assert make(client, i, branch="CSE" if i % 2 else "ECE").status_code == 201
    page = client.get("/api/v2/students?limit=10").json()
    assert set(page) == {"items", "page", "limit", "total", "total_pages", "links"}
    assert (page["page"], page["limit"], page["total"], page["total_pages"]) == (1, 10, 25, 3)
    assert len(page["items"]) == 10
    assert page["links"]["prev"] is None and "page=2" in page["links"]["next"]
    last = client.get("/api/v2/students?limit=10&page=3").json()
    assert last["links"]["next"] is None and "page=2" in last["links"]["prev"] and len(last["items"]) == 5
    item = page["items"][0]
    assert {"enrollment_date", "department", "enrollment_count"} <= set(item)    # richer than v1
    assert client.get("/api/v2/students?branch=ECE").json()["total"] == 12
    assert client.get("/api/v2/students?search=student 07").json()["total"] == 1
    assert client.get("/api/v2/students?limit=1000").status_code == 422


def test_both_versions_share_the_same_data_and_rules(client):
    v1 = client.get("/api/v1/students/1").json()
    v2 = client.get("/api/v2/students/1").json()
    assert v1["email"] == v2["email"] and v1["id"] == v2["id"] == 1
    assert make(client, 1, version="v1").status_code == 409            # duplicate via v1
    assert make(client, 1, version="v2").status_code == 409            # and via v2
    assert client.get("/api/v1/students/999").status_code == 404
    assert client.get("/api/v2/students/999").status_code == 404
    bad = {"name": "", "email": "x", "branch": "BCA"}
    assert client.post("/api/v1/students", json=bad).status_code == 422
    assert client.post("/api/v2/students", json=bad).status_code == 422


# =========================== deprecation headers ===========================
def test_v1_has_deprecation_headers_everywhere(client):
    responses = [client.get("/api/v1/students"), client.get("/api/v1/students/1"),
                 client.get("/api/v1/students/999"),                                   # 404 error response
                 client.post("/api/v1/students", json={"name": ""}),                    # 422 error response
                 client.get("/api/v1/unknown")]                                         # route that does not exist
    for r in responses:
        assert re.fullmatch(r"@\d+", r.headers["deprecation"]), r.status_code          # RFC 9745 timestamp
        assert parsedate_to_datetime(r.headers["sunset"]).year == 2027                 # HTTP-date
        assert 'rel="successor-version"' in r.headers["link"] and "/api/v2/" in r.headers["link"]
        assert r.headers["x-api-version"] == "1"


def test_v2_is_not_deprecated(client):
    r = client.get("/api/v2/students")
    assert "deprecation" not in r.headers and "sunset" not in r.headers
    assert r.headers["x-api-version"] == "2"
    assert "deprecation" not in client.get("/health").headers


# =========================== Swagger / OpenAPI customisation ===========================
@pytest.fixture(scope="module")
def spec(client):
    return client.get("/openapi.json").json()


def test_title_description_contact_license(spec):
    info = spec["info"]
    assert info["title"] == "Student Management API" and info["version"] == "2.0.0"
    assert "two versions" in info["description"] and "deprecated" in info["description"]
    assert info["contact"]["email"] and info["contact"]["name"] and info["contact"]["url"]
    assert info["license"]["name"] == "MIT" and info["termsOfService"]
    assert {s["description"] for s in spec["servers"]} == {"Development", "Production (replace after deploying)"}


def test_tags_group_endpoints(spec):
    tags = {t["name"]: t["description"] for t in spec["tags"]}
    assert set(tags) == {"v1 (deprecated)", "v2", "meta"} and all(tags.values())
    for path, methods in spec["paths"].items():
        for op in methods.values():
            expected = "v1 (deprecated)" if path.startswith("/api/v1") else "v2" if path.startswith("/api/v2") else "meta"
            assert op["tags"] == [expected], path


def test_v1_operations_are_marked_deprecated(spec):
    for path, methods in spec["paths"].items():
        for op in methods.values():
            assert bool(op.get("deprecated")) == path.startswith("/api/v1"), path


def test_request_and_response_examples_exist(spec):
    schemas = spec["components"]["schemas"]
    assert schemas["StudentCreate"]["examples"][0]["email"] == "aarav@upes.ac.in"          # request example
    assert schemas["StudentV1"]["examples"] and schemas["StudentV2"]["examples"]             # response examples
    named = spec["paths"]["/api/v2/students"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    assert set(named) == {"full", "minimal", "invalid"}                                      # named examples in Swagger


def test_error_responses_are_documented(spec):
    for path in ("/api/v1/students/{student_id}", "/api/v2/students/{student_id}"):
        assert "404" in spec["paths"][path]["get"]["responses"]
    for path in ("/api/v1/students", "/api/v2/students"):
        assert {"201", "409", "422"} <= set(spec["paths"][path]["post"]["responses"])


def test_swagger_and_redoc_pages_load(client):
    swagger, redoc = client.get("/docs"), client.get("/redoc")
    assert swagger.status_code == 200 and "swagger-ui" in swagger.text
    assert redoc.status_code == 200 and "redoc" in redoc.text.lower()


# =========================== Postman export ===========================
OUT = Path(generate_postman.OUT)


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_postman_files_are_up_to_date_with_the_code():
    """If you change the API, run `python generate_postman.py` again; this test tells you when you forgot."""
    for filename, expected in generate_postman.generate().items():
        assert json.loads((OUT / filename).read_text(encoding="utf-8")) == expected, f"{filename} is stale"


def test_collection_covers_every_endpoint(spec):
    collection = load("Student_Management_API.postman_collection.json")
    assert collection["info"]["schema"].endswith("v2.1.0/collection.json")
    requests = [(r["request"]["method"], r["request"]["url"]["raw"]) for f in collection["item"] for r in f["item"]]
    assert len(requests) == sum(len(m) for m in spec["paths"].values()) == len(set(requests))
    assert all(raw.startswith("{{base_url}}/") for _, raw in requests)


def test_environments_define_base_url():
    dev, prod = load("Development.postman_environment.json"), load("Production.postman_environment.json")
    assert dev["name"] == "Development" and prod["name"] == "Production"
    assert dev["values"][0]["key"] == prod["values"][0]["key"] == "base_url"
    assert dev["values"][0]["value"].startswith("http://127.0.0.1") and prod["values"][0]["value"].startswith("https://")
    assert dev["id"] != prod["id"]


def test_collection_runs_green_like_newman(client):
    """Replays the exported collection against the app (a tiny Newman) and checks every status assertion."""
    collection = load("Student_Management_API.postman_collection.json")
    variables = {v["key"]: v["value"] for v in collection["variable"]}
    counter = iter(range(1000, 2000))
    ran = 0
    for folder in collection["item"]:
        for item in folder["item"]:
            req = item["request"]
            path = "/" + "/".join(req["url"]["path"])
            for var in req["url"].get("variable", []):
                path = path.replace(f":{var['key']}", variables.get(var["value"].strip("{}"), "1"))
            params = {q["key"]: q["value"] for q in req["url"].get("query", []) if not q.get("disabled")}
            body = None
            if "body" in req:
                body = json.loads(req["body"]["raw"].replace("{{$randomEmail}}", f"postman{next(counter)}@upes.ac.in"))
            response = client.request(req["method"], path, params=params, json=body)

            script = "\n".join(item["event"][0]["script"]["exec"])
            expected = int(re.search(r"to\.have\.status\((\d+)\)", script).group(1))
            assert response.status_code == expected, f"{req['method']} {path}: {response.status_code} != {expected}"
            if "Deprecation headers" in script:
                assert "deprecation" in response.headers and "sunset" in response.headers
            if "collectionVariables.set" in script:
                variables["student_id"] = str(response.json()["id"])
            ran += 1
    assert ran == 8
