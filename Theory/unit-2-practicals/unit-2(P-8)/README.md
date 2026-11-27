# Unit 2 (P-8): Authorization and Role-Based Access Control (Lecture 21)

## Task
The slides for this lecture have no numbered lab list; the PBL activity is **"Implementing RBAC for the Student Management API with Admin/Faculty/Student roles"**. This practical does exactly that, on top of the JWT login from P-7. If your teacher gave you a specific task list for L21, tell me and I will align it.

## What is implemented
1. Three roles: **admin**, **faculty**, **student**.
2. Permissions are assigned to roles (`permissions.py`), using the permission names from the lecture (`students:read`, `courses:write`, `grades:write`, ...).
3. A reusable `require_permission(...)` dependency, and `require_permission_or_own(...)` for **ownership checks** (a student may touch only their own record).
4. Best practices from the lecture: deny by default, least privilege, authorization in one central file, audit log of every allow/deny decision, tests for forbidden access.
5. An admin-only endpoint to change a user's role.

## Run
```bash
cd "unit-2(P-8)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q                      # 23 tests, the full authorization matrix
```
Swagger UI: http://127.0.0.1:8000/docs (click **Authorize**: username = email, password).

Create the first admin, then register ordinary users normally with `POST /register`. The admin promotes one of them to faculty:
```bash
python create_admin.py admin@upes.ac.in "Admin@12345" "Admin User"
# log in as admin, then:  PATCH /users/{id}/role   body {"role": "faculty"}
```

## Permission matrix
| Permission | admin | faculty | student |
|---|:-:|:-:|:-:|
| `students:read` (list / view any student) | yes | yes | no |
| `students:read_own`, `students:update_own` | n/a | no | yes |
| `students:write` (update any student, enrol anyone) | yes | no | no |
| `students:delete` | yes | no | no |
| `courses:read` | yes | yes | yes |
| `courses:write`, `courses:delete` | yes | no | no |
| `grades:read` (any student) | yes | yes | no |
| `grades:read_own` | n/a | no | yes |
| `grades:write` (set grades) | yes | yes | no |
| `roles:manage` | yes | no | no |

## Endpoint access
| Endpoint | Allowed |
|---|---|
| `POST /register`, `POST /login` | public |
| `GET /me`, `GET /me/permissions` | any logged-in user |
| `GET /students` | admin, faculty |
| `GET /students/{id}` | admin, faculty, or that student |
| `PATCH /students/{id}` | admin, or that student |
| `DELETE /students/{id}` | admin only |
| `GET /courses`, `/courses/{id}`, `/departments` | everyone logged in |
| `POST /courses`, `POST /departments`, `DELETE /courses/{id}` | admin only |
| `GET /students/{id}/enrollments` | admin, faculty, or that student |
| `POST` / `DELETE /students/{id}/enrollments...` | admin, or that student (a student cannot set their own grade) |
| `PATCH /students/{id}/enrollments/{course}` (grade) | admin, faculty |
| `PATCH /users/{id}/role` | admin only (not on yourself) |

## 401 versus 403
- **401 Unauthorized**: no token, or an invalid/expired token (authentication failed).
- **403 Forbidden**: valid token, but the role lacks the permission (authorization failed).

## Design decisions worth explaining in the viva
- **Role is read from the database on every request, not from the token.** So when an admin changes a role it applies immediately, even with the old token (tested in `test_role_change_applies_immediately_with_the_old_token`).
- **Unknown role gets no permissions** (deny by default).
- **No privilege escalation:** registering always creates a student, and a `role` field in a profile update is ignored.
- **An admin cannot change their own role**, so the last admin cannot lock everybody out.
- Differences from the slides, chosen for least privilege: students get `*_own` permissions (the slide's table says "read own profile") instead of reading every student, and only admins delete students (as in the slide's decorator example). In P-7, a student could delete themselves; here they cannot.
- Roles are kept in code (`permissions.py`) for simplicity. The slides' optional database schema (roles, permissions, association tables) is the alternative when roles must be edited at runtime.

## Audit log
Decisions are logged to the console, for example:
```
authz DENY  user=3 role=student needs=students:read on endpoint
authz ALLOW user=2 role=faculty has=students:read
authz ROLE  admin=1 changed user=4 role student -> faculty
```

## Postman checks
1. Log in as the student, `GET /students`, expect **403**.
2. Log in as faculty, `GET /students`, expect **200**; `POST /courses`, expect **403**.
3. As faculty, `PATCH /students/{id}/enrollments/CS301` body `{"grade": "A"}`, expect **200**.
4. As admin, `DELETE /students/{id}`, expect **204**.
5. As student A, `GET /students/{B's id}`, expect **403**; `GET /students/{A's id}`, expect **200**.
