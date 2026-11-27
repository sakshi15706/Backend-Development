"""P-5: Library Management System API (Book, Member, Loan), in-memory storage.

    uvicorn main:app --reload
    Swagger UI: http://127.0.0.1:8000/docs      ReDoc: http://127.0.0.1:8000/redoc
    OpenAPI JSON: http://127.0.0.1:8000/openapi.json
"""
import math
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response

from schemas import (BookCreate, BookOut, BookUpdate, ErrorOut, LoanCreate, LoanOut,
                     MemberCreate, MemberOut, MemberUpdate, Page)

LOAN_DAYS = 14

tags = [
    {"name": "Books", "description": "Catalogue. Filter by **genre**, **author** and **availability**."},
    {"name": "Members", "description": "Library members."},
    {"name": "Loans", "description": "Borrowing and returning books."},
]

app = FastAPI(
    title="Library Management API",
    summary="Books, Members and Loans",
    description=(
        "Resource-oriented REST API.\n\n"
        "* Lists are paginated with `page` and `limit` and return `total` and `total_pages`.\n"
        "* Errors: `404` not found, `409` conflict (duplicate / business rule), `422` validation."
    ),
    version="1.0.0",
    openapi_tags=tags,
)

# ----------------------------- in-memory "tables" -----------------------------
books: dict[int, dict] = {}
members: dict[int, dict] = {}
loans: dict[int, dict] = {}
_seq = {"book": 0, "member": 0, "loan": 0}


def next_id(kind: str) -> int:
    _seq[kind] += 1
    return _seq[kind]


def reset():
    """Used by the tests."""
    for table in (books, members, loans):
        table.clear()
    for k in _seq:
        _seq[k] = 0


def paginate(rows: list, page: int, limit: int) -> dict:
    total = len(rows)
    start = (page - 1) * limit
    return {"items": rows[start:start + limit], "page": page, "limit": limit,
            "total": total, "total_pages": math.ceil(total / limit) if total else 0}


def book_out(b: dict) -> dict:
    return {**b, "available": b["copies_available"] > 0}


def loan_out(l: dict) -> dict:
    return {**l, "status": "RETURNED" if l["return_date"] else "ACTIVE"}


def get_or_404(table: dict, obj_id: int, label: str) -> dict:
    if obj_id not in table:
        raise HTTPException(404, f"{label} {obj_id} not found")
    return table[obj_id]


NOT_FOUND = {404: {"model": ErrorOut}}
CONFLICT = {409: {"model": ErrorOut}}


# ================================= BOOKS =================================
@app.get("/books", response_model=Page[BookOut], tags=["Books"], summary="List and filter books")
def list_books(
    genre: Optional[str] = Query(None, description="exact genre, case-insensitive"),
    author: Optional[str] = Query(None, description="part of an author name, case-insensitive"),
    available: Optional[bool] = Query(None, description="true = at least one copy in stock"),
    search: Optional[str] = Query(None, description="part of the title"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    rows = list(books.values())
    if genre:
        rows = [b for b in rows if b["genre"].lower() == genre.lower()]
    if author:
        rows = [b for b in rows if any(author.lower() in a.lower() for a in b["authors"])]
    if available is not None:
        rows = [b for b in rows if (b["copies_available"] > 0) == available]
    if search:
        rows = [b for b in rows if search.lower() in b["title"].lower()]
    rows.sort(key=lambda b: b["title"].lower())
    result = paginate(rows, page, limit)
    result["items"] = [book_out(b) for b in result["items"]]
    return result


@app.post("/books", response_model=BookOut, status_code=201, tags=["Books"], responses=CONFLICT)
def create_book(payload: BookCreate):
    if any(b["isbn"] == payload.isbn for b in books.values()):
        raise HTTPException(409, f"ISBN {payload.isbn} already exists")
    book_id = next_id("book")
    books[book_id] = {"id": book_id, **payload.model_dump(), "copies_available": payload.copies_total}
    return book_out(books[book_id])


@app.get("/books/{book_id}", response_model=BookOut, tags=["Books"], responses=NOT_FOUND)
def get_book(book_id: int):
    return book_out(get_or_404(books, book_id, "Book"))


@app.put("/books/{book_id}", response_model=BookOut, tags=["Books"], responses={**NOT_FOUND, **CONFLICT})
def update_book(book_id: int, payload: BookUpdate):
    book = get_or_404(books, book_id, "Book")
    changes = payload.model_dump(exclude_unset=True)
    if "copies_total" in changes:
        on_loan = book["copies_total"] - book["copies_available"]
        if changes["copies_total"] < on_loan:
            raise HTTPException(409, f"{on_loan} copies are currently on loan")
        book["copies_available"] = changes["copies_total"] - on_loan
    book.update(changes)
    return book_out(book)


@app.delete("/books/{book_id}", status_code=204, tags=["Books"], responses={**NOT_FOUND, **CONFLICT})
def delete_book(book_id: int):
    book = get_or_404(books, book_id, "Book")
    if book["copies_available"] != book["copies_total"]:
        raise HTTPException(409, "Book has copies on loan")
    del books[book_id]
    return Response(status_code=204)


# ================================= MEMBERS =================================
@app.get("/members", response_model=Page[MemberOut], tags=["Members"])
def list_members(
    status: Optional[str] = Query(None, pattern="^(ACTIVE|SUSPENDED)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    rows = [m for m in members.values() if not status or m["status"] == status]
    rows.sort(key=lambda m: m["name"].lower())
    return paginate(rows, page, limit)


@app.post("/members", response_model=MemberOut, status_code=201, tags=["Members"], responses=CONFLICT)
def create_member(payload: MemberCreate):
    if any(m["email"].lower() == payload.email.lower() for m in members.values()):
        raise HTTPException(409, "Email already registered")
    member_id = next_id("member")
    members[member_id] = {"id": member_id, **payload.model_dump(), "joined_on": date.today()}
    return members[member_id]


@app.get("/members/{member_id}", response_model=MemberOut, tags=["Members"], responses=NOT_FOUND)
def get_member(member_id: int):
    return get_or_404(members, member_id, "Member")


@app.put("/members/{member_id}", response_model=MemberOut, tags=["Members"], responses={**NOT_FOUND, **CONFLICT})
def update_member(member_id: int, payload: MemberUpdate):
    member = get_or_404(members, member_id, "Member")
    changes = payload.model_dump(exclude_unset=True)
    new_email = changes.get("email")
    if new_email and any(m["id"] != member_id and m["email"].lower() == new_email.lower() for m in members.values()):
        raise HTTPException(409, "Email already registered")
    member.update(changes)
    return member


@app.delete("/members/{member_id}", status_code=204, tags=["Members"], responses={**NOT_FOUND, **CONFLICT})
def delete_member(member_id: int):
    get_or_404(members, member_id, "Member")
    if any(l["member_id"] == member_id and not l["return_date"] for l in loans.values()):
        raise HTTPException(409, "Member has books that are not returned")
    del members[member_id]
    return Response(status_code=204)


@app.get("/members/{member_id}/loans", response_model=Page[LoanOut], tags=["Members"], responses=NOT_FOUND)
def member_loans(member_id: int, active: Optional[bool] = None,
                 page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Nested resource: all loans of one member."""
    get_or_404(members, member_id, "Member")
    rows = [loan_out(l) for l in loans.values() if l["member_id"] == member_id]
    if active is not None:
        rows = [l for l in rows if (l["status"] == "ACTIVE") == active]
    result = paginate(rows, page, limit)
    return result


# ================================= LOANS =================================
@app.post("/loans", response_model=LoanOut, status_code=201, tags=["Loans"],
          responses={**NOT_FOUND, **CONFLICT}, summary="Borrow a book")
def borrow_book(payload: LoanCreate):
    book = get_or_404(books, payload.book_id, "Book")
    member = get_or_404(members, payload.member_id, "Member")
    if member["status"] != "ACTIVE":
        raise HTTPException(409, "Member is suspended")
    if book["copies_available"] < 1:
        raise HTTPException(409, "No copies available")
    if any(l["book_id"] == book["id"] and l["member_id"] == member["id"] and not l["return_date"]
           for l in loans.values()):
        raise HTTPException(409, "Member already borrowed this book")
    book["copies_available"] -= 1
    loan_id = next_id("loan")
    today = date.today()
    loans[loan_id] = {"id": loan_id, "book_id": book["id"], "member_id": member["id"],
                      "loan_date": today, "due_date": today + timedelta(days=LOAN_DAYS), "return_date": None}
    return loan_out(loans[loan_id])


@app.post("/loans/{loan_id}/return", response_model=LoanOut, tags=["Loans"],
          responses={**NOT_FOUND, **CONFLICT}, summary="Return a book")
def return_book(loan_id: int):
    loan = get_or_404(loans, loan_id, "Loan")
    if loan["return_date"]:
        raise HTTPException(409, "Loan already returned")
    loan["return_date"] = date.today()
    books[loan["book_id"]]["copies_available"] += 1
    return loan_out(loan)


@app.get("/loans", response_model=Page[LoanOut], tags=["Loans"])
def list_loans(member_id: Optional[int] = None, book_id: Optional[int] = None,
               status: Optional[str] = Query(None, pattern="^(ACTIVE|RETURNED)$"),
               page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    rows = [loan_out(l) for l in loans.values()]
    if member_id is not None:
        rows = [l for l in rows if l["member_id"] == member_id]
    if book_id is not None:
        rows = [l for l in rows if l["book_id"] == book_id]
    if status:
        rows = [l for l in rows if l["status"] == status]
    return paginate(rows, page, limit)


@app.get("/loans/{loan_id}", response_model=LoanOut, tags=["Loans"], responses=NOT_FOUND)
def get_loan(loan_id: int):
    return loan_out(get_or_404(loans, loan_id, "Loan"))
