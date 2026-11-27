# Unit 2 (P-6): Implementing RESTful APIs (Lecture 19)

## Lab exercise
1. Implement the complete Student Management API with all CRUD operations.
2. Add filtering to `GET /students` (by branch, department, search).
3. Implement pagination with `page`, `limit`, `total` and `total_pages` in the response.
4. Create a `POST /courses` endpoint and test it with Postman.
5. Implement nested endpoints for student enrollments.
6. Add proper error handling for all endpoints (404, 409, 422).
7. Document the API using FastAPI's built-in Swagger UI.

## Run
```bash
cd "unit-2(P-6)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q
```
Swagger UI: http://127.0.0.1:8000/docs. The SQLite file `students.db` is created on first start.

## Endpoints
| Method | URL | Notes |
|---|---|---|
| POST / GET | `/departments` | helper resource |
| POST | `/courses` | 201, 409 duplicate id, 404 unknown department, 422 |
| GET | `/courses`, `/courses/{id}` | filter by `department_id`, `credits` |
| POST | `/students` | 201, 409 duplicate email, 404 unknown department |
| GET | `/students?branch=&department_id=&search=&page=&limit=` | filter + pagination |
| GET, PUT, PATCH, DELETE | `/students/{id}` | PUT replaces, PATCH updates some fields |
| GET, POST | `/students/{id}/enrollments` | nested resource |
| PATCH, DELETE | `/students/{id}/enrollments/{course_id}` | set grade / drop course |

Pagination response: `{ "items": [...], "page": 1, "limit": 10, "total": 19, "total_pages": 2 }`

## Error handling
| Code | When |
|---|---|
| 404 | student / course / department / enrollment does not exist |
| 409 | duplicate email, duplicate course id, already enrolled |
| 422 | validation failed (bad email, branch not in CSE/ECE/IT/ME/CE, credits outside 1 to 6, page < 1 ...) |

All errors use the shape `{"detail": "..."}` (422 returns a list of field errors).

## Postman walk-through
1. `POST /departments` body `{"name": "Computer Science"}`
2. `POST /courses` body `{"id": "CS301", "title": "Database Systems", "credits": 4, "department_id": 1}` (expect 201; send again, expect 409)
3. `POST /students` body `{"name": "Aarav", "email": "aarav@upes.ac.in", "branch": "CSE", "department_id": 1}`
4. `POST /students/1/enrollments` body `{"course_id": "CS301", "semester": "Fall 2024"}`
5. `GET /students?branch=CSE&search=aar&page=1&limit=5`
6. `GET /students/1/enrollments`, then `DELETE /students/1` and check that enrollments are gone.
Tip: in Postman, set Body to **raw / JSON** or you will get 422.
