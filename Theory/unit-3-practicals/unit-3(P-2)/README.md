# Unit 3 (P-2): Django Middleware and URL Routing (Lecture 27)

**PBL:** add logging and student-detail routes to the Student Management API.

> Lecture 26 (Django overview and setup) was not among the files you sent. The slides refer to its result (project `student_system`, app `students`, a `health-check` route), so this folder includes that minimal setup. Nothing here depends on anything else.

## Setup
```bash
cd "unit-3(P-2)"
python -m venv venv
venv\Scripts\activate           # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py runserver
```
(The project was created with `django-admin startproject student_system .` and `python manage.py startapp students`.)

## What is implemented
| Slide task | File |
|---|---|
| Task 1: logging middleware (method, path, status, elapsed ms) | `students/middleware.py` |
| Task 2: register it first in `MIDDLEWARE` | `student_system/settings.py` |
| Task 3: app-level routes `""` and `"<int:student_id>/"`, views, include under `api/students/` | `students/urls.py`, `students/views.py`, `student_system/urls.py` |
| Task 4: diagnose common errors | `DEBUGGING.md` |
| PBL: break a route, predict, fix | `DEBUGGING.md` (three experiments, results recorded) |
| Logging configuration (so the messages actually print) | `LOGGING` in `settings.py` |

## Try it
```bash
python manage.py runserver
curl http://127.0.0.1:8000/api/health/       # {"status": "ok"}
curl http://127.0.0.1:8000/api/students/     # {"students": [], "message": "Student list endpoint"}
curl http://127.0.0.1:8000/api/students/42/  # {"student_id": 42, "message": ...}
```
The server terminal shows, for each request:
```
[INFO] students.middleware: Request: GET /api/students/42/
[INFO] students.middleware: Response: 200 in 0.45 ms
```

## Test
```bash
python manage.py test
```
12 tests: health, list and detail routes; `<int:...>` rejecting `abc`; trailing-slash redirect; `reverse()` names; the middleware logging request, status, query string and elapsed time; registration order.

## Concepts to be able to explain
- **Middleware contract:** `__init__(get_response)` stores the next handler; `__call__(request)` runs code before the view, calls `self.get_response(request)`, runs code after, and returns the response.
- **Order:** the request goes down the `MIDDLEWARE` list, the response comes back up in reverse.
- **URLconf:** `path()` maps a pattern to a view; `<int:student_id>` validates and converts the segment and passes it as the keyword argument `student_id`; `name=` allows `reverse()`.
- **Why `include()`:** each app owns its routes (`students/urls.py`), the project file only adds the prefix.

## Optional extras from the slides
Modify a request or response inside `__call__`:
```python
request.course_name = "Django"        # before get_response: a view can read request.course_name
response["X-Course"] = "Django"       # after get_response: adds a response header
```
