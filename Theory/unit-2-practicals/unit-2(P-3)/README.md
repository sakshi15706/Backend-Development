# Unit 2 (P-3): CRUD Operations (Lecture 16)

## Lab exercise
1. Implement a complete CRUD API for a **Course** resource using FastAPI and SQLAlchemy.
2. Add filtering to get courses by department and credits.
3. Implement pagination (10 courses per page).
4. Create a Student model with a foreign key to Department and implement CRUD with related data.
5. Write SQL queries: students enrolled after August 2024, count per branch, students in more than 3 courses.
6. Test the API using Postman and verify all CRUD operations.

## Run
```bash
cd "unit-2(P-3)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
```
Swagger UI: http://127.0.0.1:8000/docs (SQLite file `school.db` is created automatically.)

```bash
pytest -q                 # automated tests for every requirement
python run_queries.py     # runs the 3 SQL queries on sample data
```

## Endpoints
| Method | URL | Notes |
|---|---|---|
| POST | /courses | 201, 409 duplicate code, 404 unknown department, 422 invalid |
| GET | /courses?department_id=1&credits=4&page=1&limit=10 | filter + pagination |
| GET / PUT / DELETE | /courses/{id} | 200 / 204 / 404 |
| POST, GET | /departments | helper resource |
| CRUD | /students, /students/{id} | `department_id` is a foreign key; responses include the related `department` |

Pagination response:
```json
{ "items": [...], "page": 1, "limit": 10, "total": 26, "total_pages": 3 }
```

## Testing with Postman (step 6)
1. Create a Department: `POST http://127.0.0.1:8000/departments` body (raw, JSON) `{"name": "Computer Science"}`
2. Create a Course: `POST /courses` body `{"code": "CS301", "title": "Database Systems", "credits": 4, "department_id": 1}`
3. List with filters: `GET /courses?department_id=1&credits=4&page=1`
4. Update: `PUT /courses/1` body `{"credits": 3}`
5. Delete: `DELETE /courses/1` (expect 204), then `GET /courses/1` (expect 404)
6. Negative tests: `credits: 9` (422), same `code` twice (409), `department_id: 999` (404)

## SQL queries
`sql_queries.sql` contains the three required queries. Query 3 uses an `enrollments(student_id, course_id)` junction table (built in P-2 and P-6).
