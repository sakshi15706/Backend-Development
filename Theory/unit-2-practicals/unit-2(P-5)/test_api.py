import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean():
    main.reset()


def make_book(i=1, **kw):
    body = {"title": f"Book {i:02}", "authors": ["Author A"], "genre": "Programming",
            "isbn": f"97801323{i:05}", "copies_total": 1}
    body.update(kw)
    return client.post("/books", json=body)


def test_book_crud_and_validation():
    r = make_book(1, title="Clean Code", authors=["Robert C. Martin"])
    assert r.status_code == 201 and r.json()["available"] is True
    bid = r.json()["id"]
    assert make_book(1).status_code == 409                                       # duplicate ISBN
    assert client.post("/books", json={"title": "", "authors": [], "genre": "x", "isbn": "12"}).status_code == 422
    assert client.get(f"/books/{bid}").json()["title"] == "Clean Code"
    assert client.put(f"/books/{bid}", json={"genre": "Software"}).json()["genre"] == "Software"
    assert client.delete(f"/books/{bid}").status_code == 204
    assert client.get(f"/books/{bid}").status_code == 404


def test_filter_by_genre_author_availability():
    make_book(1, genre="Programming", authors=["Robert C. Martin"])
    make_book(2, genre="Programming", authors=["Andrew Hunt", "David Thomas"])
    make_book(3, genre="Fiction", authors=["George Orwell"])
    assert client.get("/books?genre=programming").json()["total"] == 2
    assert client.get("/books?author=thomas").json()["total"] == 1          # second author of book 2
    assert client.get("/books?genre=Fiction&author=orwell").json()["total"] == 1
    assert client.get("/books?search=book 03").json()["total"] == 1

    client.post("/members", json={"name": "Aarav", "email": "a@upes.ac.in"})
    client.post("/loans", json={"book_id": 1, "member_id": 1})              # book 1 has a single copy
    assert client.get("/books?available=false").json()["total"] == 1
    assert client.get("/books?available=true").json()["total"] == 2


def test_pagination():
    for i in range(1, 26):
        make_book(i)
    p1 = client.get("/books?limit=10").json()
    assert (p1["page"], p1["limit"], p1["total"], p1["total_pages"], len(p1["items"])) == (1, 10, 25, 3, 10)
    p3 = client.get("/books?page=3&limit=10").json()
    assert len(p3["items"]) == 5
    assert client.get("/books?page=4&limit=10").json()["items"] == []
    assert client.get("/books?limit=1000").status_code == 422


def test_member_crud_and_conflicts():
    r = client.post("/members", json={"name": "Aarav", "email": "aarav@upes.ac.in"})
    assert r.status_code == 201
    assert client.post("/members", json={"name": "X", "email": "AARAV@upes.ac.in"}).status_code == 409
    assert client.post("/members", json={"name": "X", "email": "bad"}).status_code == 422
    assert client.put("/members/1", json={"status": "SUSPENDED"}).json()["status"] == "SUSPENDED"
    assert client.get("/members?status=SUSPENDED").json()["total"] == 1


def test_loan_flow():
    make_book(1, copies_total=1)
    client.post("/members", json={"name": "Aarav", "email": "a@upes.ac.in"})
    client.post("/members", json={"name": "Diya", "email": "d@upes.ac.in"})

    loan = client.post("/loans", json={"book_id": 1, "member_id": 1})
    assert loan.status_code == 201 and loan.json()["status"] == "ACTIVE"
    assert client.get("/books/1").json()["copies_available"] == 0
    assert client.post("/loans", json={"book_id": 1, "member_id": 2}).status_code == 409   # no copies
    assert client.delete("/members/1").status_code == 409                                   # still has a loan
    assert client.delete("/books/1").status_code == 409                                     # on loan
    assert client.get("/members/1/loans?active=true").json()["total"] == 1

    ret = client.post("/loans/1/return")
    assert ret.status_code == 200 and ret.json()["status"] == "RETURNED"
    assert client.post("/loans/1/return").status_code == 409
    assert client.get("/books/1").json()["copies_available"] == 1
    assert client.post("/loans", json={"book_id": 99, "member_id": 1}).status_code == 404


def test_suspended_member_cannot_borrow():
    make_book(1)
    client.post("/members", json={"name": "A", "email": "a@upes.ac.in", "status": "SUSPENDED"})
    assert client.post("/loans", json={"book_id": 1, "member_id": 1}).status_code == 409


def test_openapi_documentation():
    spec = client.get("/openapi.json").json()
    assert spec["info"]["title"] == "Library Management API"
    assert {"/books", "/books/{book_id}", "/members", "/loans", "/loans/{loan_id}/return"} <= set(spec["paths"])
    assert {t["name"] for t in spec["tags"]} == {"Books", "Members", "Loans"}
    assert client.get("/docs").status_code == 200 and client.get("/redoc").status_code == 200
