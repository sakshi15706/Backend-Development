# Unit 3 (P-4): Testing and Debugging Django Applications (Lecture 29)

**PBL:** build tests for the Student API (health, list, detail, model, mocked external service) and diagnose one intentionally introduced defect.

Builds on P-3 (middleware, routes, external API). New here: a real `Student` model, database-backed list/detail views and the test suite.

## Setup
```bash
cd "unit-3(P-4)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Run the tests
```bash
python manage.py test                       # everything (29 tests)
python manage.py test students.tests.StudentAPITest
python manage.py test students.tests.StudentAPITest.test_health_endpoint
python manage.py test -v 2                  # detail
python manage.py test --failfast            # stop at the first failure
```

## What is in the suite
| File | Contents |
|---|---|
| `students/tests.py` | Lecture 29 tasks: health endpoint (named URL with `reverse`), detail with `kwargs`, 404 with message, list (empty and filled), isolation between tests, model tests (saved, `__str__`, unique email), mocked external service (success, timeout, 503 mapping) |
| `students/test_external.py` | extra mocked cases from Lecture 28: connection error, HTTP 5xx, invalid JSON, view and full-path tests |
| `students/test_middleware.py` | middleware logs request and status, registered first |

Choice of test class (explain in the viva): **`TestCase`** when the test needs the database (Django creates a temporary one and rolls back after every test); **`SimpleTestCase`** when it does not (utility functions, mocks).

## Evaluation criteria mapping
| Criterion | Where |
|---|---|
| Test coverage: health, list, detail, failure paths | `StudentAPITest`, `StudentRouteTest` (404, empty list) |
| Test quality: named URLs, meaningful assertions, isolated data | `reverse()`, records created inside each test |
| Debugging: traceback, faulty code | `DEFECT_DIAGNOSIS.md` (real run: `201 != 200`) |
| Dependency testing: mock, no internet | `ExternalServiceTest`, `test_external.py` |
| CO attainment | explain how tests prevent regressions (below) |

## Notes
- The detail and list views now read the database. `GET /api/students/<id>/` returns `{"student_id", "name", "email"}` or `404 {"error": "Student not found"}`. Create students in `/admin/` (`python manage.py createsuperuser`) to try it by hand.
- Logging is used for debugging (`logger.info("Looking up student_id=%s", ...)`). Do not log passwords, tokens or personal data.
- Django Debug Toolbar (optional, from the slides) is not installed here; it is for local development only and must never be enabled in production.
- A passing suite means the *tested* behaviour works, not that everything does.
