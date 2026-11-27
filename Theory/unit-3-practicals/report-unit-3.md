# Backend Development Lab Report: Unit 3 (Frameworks and Performance Optimization)

| | |
|---|---|
| Name | _(your name)_ |
| SAP ID / Roll no. | _(your SAP ID)_ |
| Course | Backend Development, UPES |
| Source | Unit 3 lecture slides by Dr. Prateek Raj Gautam |
| Folders | `unit-3(P-1)` to `unit-3(P-8)` inside `Theory` |

## 1. Summary
Eight practicals: one Express.js exercise followed by a Django project that grows from middleware and routing to external APIs, testing, security, caching, forms and file uploads. Each folder runs on its own (earlier code is copied forward) and has its own `README.md` and automated tests.

| Practical | Lecture / source | Topic | Tests (all passing) |
|---|---|---|---|
| P-1 | Lecture 25 | Express.js setup and basic server | 3 (`node --test`) |
| P-2 | Lecture 27 | Django middleware and URL routing | 12 |
| P-3 | Lecture 28 | Integrating third-party APIs (timeouts, 503, mocks) | 24 |
| P-4 | Lecture 29 | Testing and debugging Django applications | 29 |
| P-5 | Lecture 30 | Security: authentication and authorization | 54 |
| P-6 | Lecture 31 | Caching and query optimisation | 81 |
| P-7 | Optional tutorial | Django forms: student registration | 64 |
| P-8 | Tutorial | File uploads (form and REST), static vs media | 95 |

The test counts are **cumulative**, because each folder includes the code and tests of the practicals it builds on (P-6 has 81 because it contains P-5's 54 plus 27 new). The number of distinct tests across the unit is smaller than the sum (3+12+24+29+54+81+64+95 = 362). Lecture 26 (Django overview and setup) was not among the files supplied, so P-2 includes the minimal project setup it assumes (`student_system` project, `students` app, a health route).

Stack: Node 22 and Express 4; Python, Django 6.1, Django REST Framework, Pillow, `requests`, SQLite.

## 2. Practical details

### P-1: Express.js (Lecture 25)
`npm init`, `npm install express`, and `app.js` answering `API is running` on `/` with `express.json()` in the pipeline. The server starts only when run directly, so tests can import the app. Tests cover the root route, an unknown route (404) and malformed JSON being rejected.

### P-2: Middleware and routing (Lecture 27)
Logging middleware (`__init__` stores `get_response`, `__call__` logs the request, calls the next layer, then logs status and elapsed milliseconds), registered first in `MIDDLEWARE`; app-level `urls.py` included under `api/students/`; fixed and `<int:student_id>` routes. `DEBUGGING.md` records three deliberately introduced routing errors with the prediction and the actual result: a converter/argument name mismatch gives 500 (`TypeError`), a non-matching pattern gives 404, a missing trailing slash gives 404.

### P-3: Third-party APIs (Lecture 28)
A service utility (`students/utils.py`) calls the external API with a configurable 2 second timeout and turns timeouts, HTTP errors, network failures and invalid JSON into safe error results; the view maps failures to **503**. Tests replace `requests.get` with mocks, so none touches the internet.

### P-4: Testing and debugging (Lecture 29)
A `Student` model with database-backed list and detail views (404 with a message), and a suite covering health, list, detail, model rules, mocked external service (success and timeout) and the middleware. `DEFECT_DIAGNOSIS.md` records a real run of the intentional defect (health view returning 201): the failure `AssertionError: 201 != 200`, how to read it, the fix, and the re-run.

### P-5: Authentication and authorization (Lecture 30)
Built-in login/logout with a login template, `@login_required` (student list and detail, secure-data), `@staff_member_required`, `@permission_required("students.view_student", raise_exception=True)`, and a `setup_roles` command that creates a `Registrar` group. Behaviour:

| Request | Anonymous | Logged in, no permission | Authorized |
|---|---|---|---|
| protected view | 302 redirect to login | 200 | 200 |
| permission view (`records/`) | 403 | 403 | 200 |
| staff view | 302 to admin login | 302 | 200 |

Tests implement the six-row table from the slides and add: permission through a group, a wrong permission not helping, superuser, `is_staff` not granting model permissions, the `next` redirect, CSRF (403 without a token), logout, identical error for unknown user and wrong password, and hashed passwords.

### P-6: Caching and performance (Lecture 31)
`Department` (ForeignKey) and `Course` (ManyToMany) models, an N+1 list view kept for measuring, the `select_related()` fix, `prefetch_related()`, `values()`, pagination (default 20, maximum 100), a low-level cache for a counts summary with signal-based invalidation, a `cache_page` cache for a public departments endpoint, and a `measure_performance` command that seeds temporary data in a rolled-back transaction. Measured on my sandbox (SQLite, 500 students, page size 100):

| Request | DB queries | ms (median) |
|---|---|---|
| student list before (N+1) | 104 | 15.14 |
| student list after (`select_related`) | 4 | 2.16 |
| students + courses (`prefetch_related`) | 5 | 6.42 |
| summary, first request (cache miss) | 6 | 1.75 |
| summary, second request (cache hit) | 2 | 0.83 |
| departments, first / second (`cache_page`) | 1 / 0 | 1.25 / 0.43 |

The query counts are exact and repeatable; the millisecond values depend on the machine and are small because SQLite runs in-process. Responses before and after optimisation are verified identical. Cache expiry, invalidation and staleness are each demonstrated by a test, and the student list is deliberately **not** `cache_page`-cached because it holds personal data (a shared per-view cache would hand one user's response to another).

### P-7: Django forms (optional tutorial)
A `forms` app with a model, `ModelForm`, GET/POST view, redirect after POST, server-side validation (age, phone, name, course list, required checkbox), CSRF, duplicate-email handling (form validation plus the database constraint), view and middleware logging, and a separate `services.py` for the external notification (timeout, never raises, skipped unless configured). Completed suggested exercises 1, 2, 3, 4, 7 and 8; exercises 5 and 6 (update and delete pages) are left for you. A tutorial inconsistency is fixed: the view redirects to the namespaced URL name `forms_app:registration-success`.

### P-8: File uploads (tutorial)
A normal upload form (5 MB, PDF/TXT/DOCX), an image upload checked by Pillow (2 MB, 4000x4000), a DRF upload endpoint, safe generated file names, static files with `collectstatic`, and the PBL **student document portal**: PDF only (extension and `%PDF-` content check), 10 MB, UUID stored name with the original name kept separately, private storage with no URL, and per-owner list and download in both HTML and REST (another user's file returns 404). `docs/PRODUCTION.md` covers the production design (reverse proxy, object storage, signed URLs, checklist). I also ran the API against a real `runserver` with `curl`: 201 for a valid PDF, 400 for a text file renamed `.pdf`, 403 anonymous, 404 for another user's file.

## 3. How to run
```bash
cd "unit-3(P-6)"                       # quote the name: brackets are special in some shells
python -m venv venv
venv\Scripts\activate                  # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```
P-1: `cd "unit-3(P-1)" && npm install && npm test && npm start`.

## 4. Limitations and honest notes
- **Lecture 26 missing:** its setup is assumed and re-created minimally in P-2.
- **Redis cache (P-6):** the Redis configuration path is included but untested (no Redis server in my environment); local-memory caching is what the tests use.
- **Not deployed or scanned (P-8):** the Nginx sample, object storage and virus scanning are described in `docs/PRODUCTION.md`, not run. The PDF check looks at the `%PDF-` header only; it is not a malware scan.
- **Timings** come from a shared sandbox and are indicative only.
- **Third-party calls:** every automated test mocks HTTP. The real endpoint (`jsonplaceholder.typicode.com`) was not called from my environment, so try `/api/students/external/1/` yourself.
- **Beyond the slides:** several additions go past the slide text (cache invalidation signals, pagination, 404-for-not-yours downloads, content checks). Each README says so, so you can explain or remove them.
- **Slide differences:** the slides use `/students/` and `students_project`; the project keeps `/api/students/` and `student_system` from the earlier practicals. The login template, `uv` commands and URL prefixes are adapted and noted in the READMEs.

## 5. To finish before submission
- [ ] Add your name and SAP ID above
- [ ] Run each practical yourself and add screenshots (test output, browser pages, curl results)
- [ ] P-2 and P-4: do the intentional routing error and defect on your own machine and record your results
- [ ] P-5: create the admin and a regular user and record the six test cases by hand
- [ ] P-6: run `python manage.py measure_performance` and use your own numbers
- [ ] `git add . && git commit -m "Unit 3 practicals" && git push`

## Sources
Unit 3 lecture slides (Dr. Prateek Raj Gautam), as supplied in the HTML exports.
