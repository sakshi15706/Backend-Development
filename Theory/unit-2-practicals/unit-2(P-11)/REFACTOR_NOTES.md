# Refactoring Notes

This folder is a worked example of refactoring a working but "flat" solution (everything in `main.py`, the style of practicals P-6 to P-8) into the structure recommended in Lecture 24. Use it as a guide when you refactor **your own** Assignment-I; the checklist items you fixed go into your report.

## Before and after
| Before (flat) | After (this project) | Checklist item fixed |
|---|---|---|
| One `main.py` holding routes, DB queries and rules | `routers/` (HTTP only), `services/` (business rules), `models.py`, `schemas.py` | Code is well-organised |
| `DATABASE_URL`, secret and token lifetime as constants in code | `config.py` reads environment variables / `.env`; production refuses the dev secret | Configuration externalised, no hard-coded secrets |
| `raise HTTPException(404, ...)` repeated in every route | services raise `NotFoundError` / `ConflictError` / `ForbiddenError`; one handler in `main.py` maps them to responses | No duplicated code, consistent errors |
| `limit=...` literals scattered around | `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` in settings | No magic numbers |
| Ownership and admin checks written inline | `require_admin`, `require_owner_or_admin` dependencies in `auth.py` | Centralised authorization |
| Single index on the primary key only | indexes on `email`, `branch` and `(branch, name)` | Appropriate indexes |
| Routes mounted at `/students` | everything under `/api/v1` | Versioning (Lecture 23) |
| `print` debugging | `logging` with levels | Logging |
| No health endpoint | `GET /health` for the hosting platform | Deployment readiness |
| Manual testing in Postman only | 28 automated tests in `tests/` using a throw-away database | Testing |

## Layer responsibilities
```
HTTP request
   |
routers/    parse and validate the request, check permissions (Depends), return the response model
   |
services/   business rules and database queries, raise domain errors, know nothing about HTTP
   |
models.py   table definitions          schemas.py   request/response shapes
```
Rule of thumb: if a function mentions `status_code` or `Response`, it belongs in a router; if it mentions a SQLAlchemy `Session`, it belongs in a service.

## How to refactor your own assignment (suggested order)
1. **Write tests first** for what already works (`tests/`), so you notice when a refactor breaks something.
2. Move settings to `config.py` and `.env`.
3. Split `main.py` into `routers/` files, one per resource.
4. Move queries and rules from the routers into `services/`.
5. Replace repeated `HTTPException`s with domain errors and one handler.
6. Add the missing checklist items (indexes, pagination limits, rate limiting, logging).
7. Re-run the tests after every step.

## Known simplifications (be ready to explain in the viva)
- Tables are created with `create_all` at startup. Real projects use **Alembic** migrations.
- No refresh tokens, and no token revocation on logout.
- Login rate limiting from P-9 is not included here (add `rate_limit.py` from P-9 if your assignment needs it).
- Only two roles (student, admin).
