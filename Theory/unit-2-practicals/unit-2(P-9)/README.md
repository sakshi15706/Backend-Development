# Unit 2 (P-9): Handling API Requests and Responses (Lecture 22)

## Lab exercise
1. Create a comprehensive validation schema for a **Course** resource: required fields (title, credits), optional fields (description, prerequisites), custom validators (credits 1 to 6, title minimum length).
2. Implement file upload for student profile photos with validation.
3. Create a response model that excludes sensitive fields (password, internal notes).
4. Add custom validation for cross-field constraints (enrollment date before graduation date).
5. Test the validation by sending invalid data and verifying proper error responses.
6. Implement rate limiting for `/login` (max 5 attempts per minute).

## Run
```bash
cd "unit-2(P-9)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q                      # 37 tests covering all six steps
```
Swagger UI: http://127.0.0.1:8000/docs

## Where each step lives
| Step | File | How |
|---|---|---|
| 1 Course schema | `schemas.py` `CourseCreate` | required `title`, `credits`; optional `description`, `prerequisites`; 3 `@field_validator`s |
| 2 Photo upload | `main.py` `upload_photo`, `uploads_util.py` | JPEG/PNG only, max 2 MB, checks the real file bytes, server-chosen filename |
| 3 Response model | `schemas.py` `StudentOut` | omits `hashed_password` and `internal_notes`, so FastAPI strips them |
| 4 Cross-field | `schemas.py` `StudentCreate` (`@model_validator`) and `check_dates` | graduation after enrollment; enrollment not in the future |
| 5 Error tests | `test_api.py` | 14 invalid course cases, 8 invalid student cases, upload cases |
| 6 Rate limit | `rate_limit.py` | sliding window, 5 attempts per 60 s per IP, then **429** with `Retry-After` |

## Course rules
| Field | Rule |
|---|---|
| `title` | required, trimmed, 3 to 100 characters, not only digits |
| `credits` | required whole number from 1 to 6 (booleans and text rejected) |
| `description` | optional, up to 500 characters |
| `prerequisites` | optional list, at most 5, each like `CS101`, no duplicates |
| any other field | rejected (`extra="forbid"`) |

## Error format (all 422 responses)
```json
{
  "detail": "Validation failed",
  "errors": [
    { "field": "credits", "message": "credits must be between 1 and 6", "type": "value_error" },
    { "field": "title",   "message": "title must be at least 3 characters", "type": "value_error" }
  ]
}
```
All problems are reported in one response, so a form can highlight every wrong field at once.

## Status codes used
| Code | Meaning here |
|---|---|
| 422 | validation failed (body, types, cross-field rules, malformed JSON) |
| 415 | upload is not JPEG/PNG |
| 413 | upload larger than 2 MB |
| 400 | upload is empty, or the bytes do not match the declared type (a text file renamed `.png`) |
| 403 | uploading or editing someone else's profile |
| 429 | more than 5 login attempts in a minute |

## Testing in Postman
1. `POST /register` with `{"name":"Aarav","email":"aarav@upes.ac.in","password":"Str0ngPass1","enrollment_date":"2022-08-01","graduation_date":"2021-01-01"}` expects **422** (graduation before enrollment).
2. Fix the date, register again (201), and check the response has **no** password field.
3. `POST /login` (Body: x-www-form-urlencoded) and copy the token into Authorization, Bearer Token.
4. `POST /courses` with `{"title":"DB","credits":9}` expects 422 with two errors.
5. `POST /students/{id}/photo` (Body: form-data, key `file` of type File): a real PNG gives 200; a `.txt` gives 415; a text file renamed `.png` gives 400.
6. Send the wrong password to `/login` six times quickly: the 6th returns **429** and a `Retry-After` header.

## Security notes
- Unknown fields are rejected, so a client cannot send `role`, `internal_notes`, etc. (mass assignment).
- The client's filename is never used for saving (blocks path traversal); the server generates `student_<id>.png|jpg`.
- Declared `Content-Type` can be faked, so the first bytes of the file are checked too. For production also re-encode the image with Pillow, and store files in object storage (S3 and similar) instead of the app's disk.
- The rate limiter keeps counters in memory, which is correct for one server process. With several workers or servers use a shared store such as Redis (`slowapi`, `fastapi-limiter`). Behind a reverse proxy, key on the real client IP (`X-Forwarded-For`), not the proxy's address.
- Rate limiting by IP alone can be bypassed by many IPs; combine with account lockout or CAPTCHA for production.
