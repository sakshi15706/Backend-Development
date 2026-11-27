# Unit 2 (P-11): Assignment-I Discussion and Solution Review (Lecture 24)

## Lab exercise
1. Review a peer's Assignment-I solution using the code review checklist.
2. Identify at least 3 areas for improvement and suggest solutions.
3. Refactor your own assignment based on the discussion points.
4. Add unit tests for your API endpoints.
5. Document your API using Swagger UI and Postman.
6. Deploy your API to a cloud platform (Heroku, Railway, or Render).

## What is in this folder, per step
| Step | Deliverable | Status |
|---|---|---|
| 1 and 2 | `CODE_REVIEW_CHECKLIST.md` (the lecture's checklist with weights and scoring) and `PEER_REVIEW_TEMPLATE.md` (with a worked example) | **You must fill in the review of a real peer's code.** I cannot review a classmate's work I have not seen. |
| 3 | `app/` (layered reference project) and `REFACTOR_NOTES.md` (before/after, how to refactor yours) | Reference solution done. Apply the same steps to your own assignment. |
| 4 | `tests/` (28 tests) | Done and passing; mutation-checked |
| 5 | Swagger at `/docs`, `docs/openapi.json` for Postman import | Done (see `DEPLOYMENT.md` for the Postman steps) |
| 6 | `render.yaml`, `Procfile`, `Dockerfile`, `DEPLOYMENT.md` | Files ready and start command tested locally. **Deploying needs your account.** Dockerfile not built (no Docker daemon in my environment). |

## Run locally
```bash
cd "unit-2(P-11)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
uvicorn app.main:app --reload
pytest -q
```
Swagger UI: http://127.0.0.1:8000/docs  |  Health: http://127.0.0.1:8000/health

To get an admin locally, add `ADMIN_EMAIL=admin@upes.ac.in` and `ADMIN_PASSWORD=Admin@12345` to `.env` and start the server once.

## Structure
```
app/
  main.py          app, error handlers, router wiring, /health
  config.py        settings from environment variables
  database.py      engine and session
  models.py        Student, Course, Enrollment (+ indexes)
  schemas.py       Pydantic request/response models
  auth.py          bcrypt, JWT, require_admin, require_owner_or_admin
  exceptions.py    NotFoundError, ConflictError, ForbiddenError
  bootstrap.py     creates the first admin from env vars
  routers/         auth, students, courses, enrollments   (HTTP layer)
  services/        student_service, course_service, enrollment_service  (business layer)
tests/             conftest.py + one test file per area
docs/openapi.json  exported API spec
```

## Endpoints (all under `/api/v1`)
| Area | Endpoints | Who |
|---|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` | public / logged in |
| Students | `GET /students` (filter, search, pagination) | admin |
| | `GET`, `PATCH /students/{id}` | admin or that student |
| | `DELETE /students/{id}` | admin |
| Courses | `POST`, `DELETE /courses` | admin |
| | `GET /courses`, `GET /courses/{id}` | any logged-in user |
| Enrollments | `GET`, `POST /students/{id}/enrollments`, `DELETE .../{course_id}` | admin or that student |
| | `PATCH /students/{id}/enrollments/{course_id}` (grade) | admin |

## Report checklist for this practical
- [ ] Filled-in `PEER_REVIEW_TEMPLATE.md` with 3 or more real improvements
- [ ] Before/after of your own refactor (use `REFACTOR_NOTES.md` as the model)
- [ ] `pytest -q` output screenshot
- [ ] Swagger UI and Postman screenshots
- [ ] Deployed URL and a screenshot of `/docs` on it
