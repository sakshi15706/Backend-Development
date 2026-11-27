# Code Review Checklist (Lecture 24)

Use this to review a peer's Assignment-I solution. Mark each line **Yes / No / N/A** and write a short note for every **No**. Criteria and weights come from the lecture's evaluation table.

| Criteria | Weight |
|---|---|
| Database Design | 20% |
| Code Quality | 25% |
| API Design | 20% |
| Security | 15% |
| Documentation | 10% |
| Testing | 10% |

## 1. Database (Database Design, 20%)
- [ ] All tables have primary keys
- [ ] Foreign keys are defined for relationships
- [ ] Appropriate indexes exist on frequently queried columns (email, branch, foreign keys)
- [ ] Data types are correct (INT for ids, VARCHAR for text, DATE for dates)
- [ ] `NOT NULL` on required fields
- [ ] `UNIQUE` on unique fields (email)
- [ ] Tables are normalised (3NF) without over-normalising
- [ ] ER diagram is included and matches the actual schema
- [ ] Cascade rules make sense (deleting a student removes their enrolments, not the courses)

## 2. API endpoints (API Design, 20%)
- [ ] RESTful naming: nouns and plurals (`/students`), no verbs (`/getStudents`)
- [ ] Correct HTTP methods (GET read, POST create, PUT/PATCH update, DELETE delete)
- [ ] Correct status codes: 201 create, 204 delete, 404 not found, 409 conflict, 422 invalid
- [ ] Request validation at the API boundary
- [ ] Response models defined (no password hashes or internal fields leaked)
- [ ] Error handling for all edge cases, with one consistent error shape
- [ ] Pagination on every collection endpoint, with a maximum page size
- [ ] Filtering and searching where useful

## 3. Authentication and authorization (Security, 15%)
- [ ] Passwords are hashed (bcrypt or Argon2), never plain text
- [ ] JWT tokens have an expiry
- [ ] Protected routes require authentication (401 without a token)
- [ ] Role-based access control is implemented (403 for the wrong role)
- [ ] Ownership checks protect user-specific resources
- [ ] Secrets come from environment variables, not the source code
- [ ] Rate limiting on login
- [ ] A user cannot give themselves a higher role

## 4. Code quality (Code Quality, 25%)
- [ ] Code is organised into routers, services, models (separation of concerns)
- [ ] Type hints are used throughout
- [ ] Configuration is externalised (`config.py` / `.env`)
- [ ] Error messages are descriptive
- [ ] No hard-coded values or magic numbers
- [ ] No duplicated code between endpoints
- [ ] Logging is used instead of `print`
- [ ] Meaningful names for functions and variables

## 5. Documentation (Documentation, 10%)
- [ ] Swagger UI is accessible at `/docs`
- [ ] Endpoints have summaries and descriptions
- [ ] Request/response examples are provided
- [ ] Error responses are documented
- [ ] README explains setup, running and testing
- [ ] Postman collection included

## 6. Testing (Testing, 10%)
- [ ] Tests exist and pass
- [ ] Happy paths are tested for every endpoint
- [ ] Error paths are tested (404, 409, 422, 401, 403)
- [ ] Tests use a separate test database
- [ ] Authorization is tested (a student cannot do admin actions)

## Scoring
For each criterion: `score = (ticks / applicable lines) x weight`.

| Criteria | Weight | Ticks / lines | Score |
|---|---|---|---|
| Database Design | 20 | | |
| Code Quality | 25 | | |
| API Design | 20 | | |
| Security | 15 | | |
| Documentation | 10 | | |
| Testing | 10 | | |
| **Total** | **100** | | |

## Review etiquette
Criticise the code, not the person. For each problem say **what** is wrong, **where** (file and line), **why** it matters, and **how** to fix it. Also name at least one thing the author did well.
