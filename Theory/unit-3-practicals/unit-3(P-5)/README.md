# Unit 3 (P-5): Security, Authentication and Authorization in Django (Lecture 30)

**PBL:** protect student records. Anonymous visitors must not see the student list, regular users must not do admin things, and only users with the right permission may open the records view.

Builds on P-4 (middleware, routes, model, external API, tests). New here: login/logout, `login_required`, `staff_member_required`, `permission_required`, a `Registrar` group and 25 new tests.

## Setup
```bash
cd "unit-3(P-5)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser          # PBL task 1: administrator account
python manage.py setup_roles              # creates the "Registrar" group (view_student)
python manage.py runserver
```
Then in http://127.0.0.1:8000/admin/ create a **regular user** (PBL task 2) and, for the authorized-user test, add that user to the `Registrar` group (Users, Groups).

## What each URL does
| URL | Protection | Anonymous | Logged in, no permission | Authorized |
|---|---|---|---|---|
| `/api/health/` | none (public on purpose) | 200 | 200 | 200 |
| `/accounts/login/` | none (built-in login view + `templates/registration/login.html`) | form | form | form |
| `/api/students/` | `@login_required` | **302** to login | 200 | 200 |
| `/api/students/<id>/` | `@login_required` | **302** | 200 / 404 | 200 / 404 |
| `/api/students/secure-data/` | `@login_required` | **302** | 200 | 200 |
| `/api/students/staff-data/` | `@staff_member_required` | **302** to admin login | **302** (not staff) | 200 (is_staff) |
| `/api/students/records/` | `@permission_required("students.view_student", raise_exception=True)` | **403** | **403** | 200 |

Key point for the viva: a **redirect (302) is not a 403**. `login_required` redirects anonymous users to the login page. `permission_required(..., raise_exception=True)` answers 403 instead of redirecting. `is_staff` only opens the admin area; it does not grant any model permission (there is a test for that).

## Try the six test cases by hand (record the result for your report)
```bash
curl -i http://127.0.0.1:8000/api/students/secure-data/            # 1 anonymous -> 302 Location: /accounts/login/?next=...
# 2 log in at http://127.0.0.1:8000/accounts/login/ in the browser, then open /api/students/secure-data/ -> 200 JSON
# 3 log in as the regular user (no group), open /api/students/records/ -> 403
# 4 add the user to the Registrar group, reload /api/students/records/ -> 200
# 5 valid login -> redirect to /api/students/secure-data/ (session cookie set)
# 6 wrong password -> the form is shown again with "Please enter a correct username and password"
```

## Run the tests
```bash
python manage.py test                 # 54 tests
python manage.py test students.test_auth
python manage.py test students.test_auth.PermissionTests -v 2
```
`students/test_auth.py` implements the slide's test-case table (anonymous / authenticated / without permission / with permission / valid login / invalid login) and adds: permission through a group, wrong permission does not help, superuser, staff vs model permission, `next` redirect, CSRF check (`Client(enforce_csrf_checks=True)` gets 403 without the token), logout, unknown user gets the same error message as a wrong password, and that passwords are stored hashed.

## Evaluation mapping (10 marks)
| Criterion | Marks | Evidence |
|---|---|---|
| Authentication implementation | 3 | `LOGIN_URL`, built-in auth URLs, login template, `login_required` views, `LoginRequiredTests`, `LoginFormTests` |
| Authorization implementation | 3 | `permission_required`, `staff_member_required`, Registrar group, `PermissionTests`, `StaffTests` |
| Functional testing | 2 | `students/test_auth.py` |
| Security practices | 2 | CSRF token in the form and tested, hashed passwords, secure cookies and SSL redirect when `DJANGO_DEBUG=0`, secret key from the environment |

## Notes and choices
- The slides put students at `/students/`; this project keeps `/api/students/` from the earlier practicals so nothing already built breaks.
- Earlier tests for list and detail now log in first, because those views are protected from this practical on.
- In production set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`; the settings then enable secure cookies and the HTTPS redirect.
- `LoginView` also shows how Django protects against CSRF: removing `{% csrf_token %}` from the template makes the POST fail with 403.
