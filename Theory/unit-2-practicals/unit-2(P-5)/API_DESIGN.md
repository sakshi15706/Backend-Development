# Library Management System: API Design (Lecture 18)

## 1. Resources
| Resource | URL | Key fields |
|---|---|---|
| Book | `/books` | `id`, `title`, `authors[]`, `genre`, `isbn`, `copies_total`, `copies_available`, `available` |
| Member | `/members` | `id`, `name`, `email`, `status` (ACTIVE / SUSPENDED), `joined_on` |
| Loan | `/loans` | `id`, `book_id`, `member_id`, `loan_date`, `due_date`, `return_date`, `status` |

Naming rules used: plural nouns, no verbs in URLs, lowercase, nesting only one level (`/members/{id}/loans`).
The one action that is not plain CRUD, returning a book, is modelled as a sub-resource action: `POST /loans/{id}/return`.

## 2. Endpoints, methods and status codes
### Books
| Method | URL | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/books` | list, filter, paginate | 200 | 422 bad query |
| POST | `/books` | create | 201 | 409 duplicate ISBN, 422 |
| GET | `/books/{id}` | read one | 200 | 404 |
| PUT | `/books/{id}` | update (partial fields accepted) | 200 | 404, 409 fewer copies than on loan, 422 |
| DELETE | `/books/{id}` | delete | 204 | 404, 409 copies on loan |

### Members
| Method | URL | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/members?status=` | list, paginate | 200 | 422 |
| POST | `/members` | create | 201 | 409 email exists, 422 |
| GET | `/members/{id}` | read one | 200 | 404 |
| PUT | `/members/{id}` | update | 200 | 404, 409, 422 |
| DELETE | `/members/{id}` | delete | 204 | 404, 409 has unreturned books |
| GET | `/members/{id}/loans?active=` | nested: member's loans | 200 | 404 |

### Loans
| Method | URL | Purpose | Success | Errors |
|---|---|---|---|---|
| POST | `/loans` | borrow a book | 201 | 404 book/member, 409 no copies / suspended / already borrowed, 422 |
| POST | `/loans/{id}/return` | return a book | 200 | 404, 409 already returned |
| GET | `/loans?member_id=&book_id=&status=` | list, filter, paginate | 200 | 422 |
| GET | `/loans/{id}` | read one | 200 | 404 |

## 3. Request and response schemas
Defined as Pydantic models in `schemas.py`.

**BookCreate (request)**
```json
{ "title": "Clean Code", "authors": ["Robert C. Martin"], "genre": "Programming",
  "isbn": "9780132350884", "copies_total": 3 }
```
**BookOut (response)**
```json
{ "id": 1, "title": "Clean Code", "authors": ["Robert C. Martin"], "genre": "Programming",
  "isbn": "9780132350884", "copies_total": 3, "copies_available": 3, "available": true }
```
**LoanCreate (request)** `{ "book_id": 1, "member_id": 1 }`
**LoanOut (response)**
```json
{ "id": 1, "book_id": 1, "member_id": 1, "loan_date": "2026-11-21",
  "due_date": "2026-12-05", "return_date": null, "status": "ACTIVE" }
```
**Error (all 4xx)** `{ "detail": "No copies available" }`  (422 returns FastAPI's list of field errors)

Validation rules: title 1 to 200 chars; at least one author; ISBN is 10 or 13 digits; `copies_total` 1 to 1000; valid email; status is one of two values. Input and output models are separate so that read-only fields (`id`, `copies_available`) cannot be set by the client.

## 4. Filtering books
`GET /books?genre=Programming&author=martin&available=true&search=clean`

| Param | Rule |
|---|---|
| `genre` | exact match, case-insensitive |
| `author` | substring match on any of the book's authors |
| `available` | `true` = at least one copy in stock, `false` = all copies on loan |
| `search` | substring of the title |

Filters combine with AND.

## 5. Pagination strategy
Offset pagination with `page` (starts at 1) and `limit` (default 10, max 100), used on books, members and loans.
```json
{ "items": [ ... ], "page": 2, "limit": 10, "total": 42, "total_pages": 5 }
```
- Chosen because a library catalogue is small and users jump to arbitrary pages.
- Sorted deterministically (books by title, members by name) so pages never overlap.
- Limit is capped at 100 to protect the server.
- If the data grows to millions of rows, or rows are inserted constantly, switch to cursor (keyset) pagination: `?after=<last_id>&limit=10`, because large OFFSETs get slower and can skip or repeat rows.

## 6. OpenAPI / Swagger documentation
FastAPI generates it automatically from the code:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Raw spec: `/openapi.json` (import into Postman)

Title, description, tags, request examples and error models are configured in `main.py` and `schemas.py`.
