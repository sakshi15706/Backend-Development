"""P-3: RESTful API with FastAPI (CRUD with validation)."""
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Books API", version="1.0.0")


class BookIn(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    year: Optional[int] = Field(None, ge=0, le=2100)


class Book(BookIn):
    id: int


books: dict[int, Book] = {
    1: Book(id=1, title="Clean Code", author="Robert C. Martin", year=2008),
    2: Book(id=2, title="The Pragmatic Programmer", author="Hunt & Thomas", year=1999),
}
next_id = 3


@app.get("/")
def root():
    return {"message": "FastAPI is running. Open /docs for Swagger UI."}


@app.get("/books", response_model=list[Book])
def list_books(author: Optional[str] = Query(None, description="filter by author")):
    result = list(books.values())
    if author:
        result = [b for b in result if author.lower() in b.author.lower()]
    return result


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]


@app.post("/books", response_model=Book, status_code=201)
def create_book(payload: BookIn):
    global next_id
    book = Book(id=next_id, **payload.model_dump())
    books[next_id] = book
    next_id += 1
    return book


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, payload: BookIn):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    books[book_id] = Book(id=book_id, **payload.model_dump())
    return books[book_id]


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    del books[book_id]
