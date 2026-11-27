# Unit 3 (P-3): Integrating Third-Party APIs and Services (Lecture 28)

**PBL:** add an external data service to the Student Management API. Two-second timeout, **503** when the dependency fails, and mocked tests for success and timeout.

Builds on P-2 (middleware, routes, `health`); those files are copied here so this folder runs on its own.

## Setup
```bash
cd "unit-3(P-3)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt      # Django + requests
python manage.py runserver
```

## What is implemented
| Slide task | File |
|---|---|
| Task 1: install the HTTP client | `requirements.txt` (`requests`) |
| Task 2: service utility with timeout and error handling | `students/utils.py` |
| Task 3: view returning 503 on failure | `students/views.py` (`external_data_view`) |
| Task 4: route | `students/urls.py` (`external/<int:post_id>/`) |
| Task 5 / PBL: mocked tests | `students/tests.py` |
| Config (URL and timeout from settings / environment) | end of `student_system/settings.py` |

## Try it
```bash
curl http://127.0.0.1:8000/api/students/external/1/
```
Needs internet access to `jsonplaceholder.typicode.com`. You get that post's JSON. To see the failure path, switch your Wi-Fi off, or set `EXTERNAL_API_TIMEOUT=0.001` before starting the server: the response becomes `503 {"error": "External service timed out"}`.

## Tests (no internet needed)
```bash
python manage.py test
```
24 tests. `students/tests.py` mocks `requests.get` (`@patch("students.utils.requests.get")`) and covers success, timeout, connection error, HTTP 5xx, invalid JSON, the view's 200/503 behaviour, and a view-to-utility integration path. `students/test_routing.py` is the P-2 suite, kept to catch regressions.

## Things worth knowing (and saying in the viva)
- **Why a service layer:** the view only decides the HTTP status; `utils.py` owns the HTTP client. That lets you test the utility alone and swap the provider later.
- **Why a timeout:** without one, a hung dependency hangs your worker too.
- **Why 503:** the *dependency* failed, not the client's request, so the API answers "Service Unavailable" rather than 500 or 404.
- **Patch target:** patch where the name is *looked up* (`students.utils.requests.get`), not where it is defined.
- **One deliberate difference from the slide:** `requests.exceptions.JSONDecodeError` is a subclass of both `RequestException` and `ValueError`. With the slide's exact handler order, an invalid-JSON response would be reported as "unavailable" because the `RequestException` handler comes first. Here it has its own handler before it, and there is a test for it.
- The URL and timeout come from settings (defaults equal to the slide's values) instead of being hard-coded, as the slide recommends for production.
