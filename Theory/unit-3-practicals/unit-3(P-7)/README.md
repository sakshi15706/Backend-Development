# Unit 3 (P-7): Optional Django Forms, a Student Registration Form (tutorial)

The tutorial builds a registration form in a new app called `forms`: ModelForm, GET/POST handling, server-side validation, CSRF, redirect after POST, duplicate-email handling, middleware logging and a safe external API call.

Builds on P-3 (project, `students` app, logging middleware, external-API utility). The project is called `student_system` here (the slides call it `students_project`); the code is the same.

## Setup
```bash
cd "unit-3(P-7)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/forms/register/ . Admin: http://127.0.0.1:8000/admin/ . Staff-only list of registrations: http://127.0.0.1:8000/forms/registrations/ .

```bash
python manage.py test            # 64 tests (forms: 40)
python manage.py test forms -v 2
```

## Tutorial step to file
| Tutorial section | File |
|---|---|
| 2-3 create and register the app | `forms/`, `INSTALLED_APPS` in `student_system/settings.py` |
| 4 model | `forms/models.py`, `forms/migrations/0001_initial.py` |
| 5 ModelForm, `clean_age()` | `forms/forms.py` |
| 6 views, redirect after POST | `forms/views.py` |
| 7 URLs with `app_name` | `forms/urls.py`, `student_system/urls.py` |
| 8 templates, 9 CSRF | `forms/templates/forms/` |
| 10 logging | `forms/views.py` (view log) + `students/middleware.py` (request log) |
| 11 duplicate e-mail, `IntegrityError` | `forms/views.py` |
| 12 external API | `forms/services.py` |
| 14 admin | `forms/admin.py` |

## The seven checks from section 13 (all automated in `forms/tests.py`)
1. Empty form shows required-field errors (`test_empty_post_shows_errors_and_saves_nothing`)
2. Invalid e-mail rejected (`test_invalid_email_shows_error`)
3. Age below 16 shows the custom error (`test_age_below_16_shows_custom_error`)
4. Valid data creates a row (`test_valid_post_saves_and_redirects_to_success`)
5. Same e-mail again is rejected (`test_duplicate_email_is_rejected`, also case-insensitive and the database race)
6. Refreshing the success page does not repeat the submission (`test_refreshing_success_page_does_not_resubmit`)
7. Logs show both the middleware and the view entries (`LoggingTests`)

## Suggested exercises (section 16): what is done
| # | Exercise | Status |
|---|---|---|
| 1 | phone number field with length check | done (`phone`, optional, exactly 10 digits) |
| 2 | course as a dropdown (`ChoiceField`) | done (`COURSE_CHOICES`) |
| 3 | confirmation checkbox | done (`agree_to_rules`, required, not stored) |
| 4 | page that lists registered students | done, **staff only** because it shows personal data |
| 5 | update form with `instance=` | not done (left for you) |
| 6 | delete confirmation page | not done (left for you) |
| 7 | tests: valid, invalid age, invalid e-mail, duplicate | done, many more |
| 8 | shared base template instead of inline CSS | done (`base.html`) |

## Things worth knowing for the viva
- **Fix to the tutorial text.** Section 6 redirects to `"registration-success"`, but section 7 sets `app_name = "forms_app"`. With a namespace that name no longer resolves (`NoReverseMatch`); the view uses `redirect("forms_app:registration-success")`, as section 11 also shows.
- **`TestCase` vs `SimpleTestCase`.** Form tests use `TestCase` because a ModelForm checks `unique=True` fields with a database query. A `SimpleTestCase` fails with "Database queries are not allowed" (that is how I found it).
- **Server-side validation.** `min`/`max` on the `age` input only help the browser. The real check is `clean_age()`, and a test posts the bad value directly.
- **CSRF.** The normal test client skips CSRF checks, so `test_post_without_csrf_token_is_forbidden` uses `Client(enforce_csrf_checks=True)` and expects 403.
- **E-mail** is lower-cased in `clean_email()`, so `AARAV@Example.com` cannot be registered next to `aarav@example.com`.
- **Logs** carry the student id, not the e-mail address, to keep personal data out of log files.
- **External call.** `notify_registration()` only runs after a successful save, has a 5 s timeout, never raises, and is skipped when `REGISTRATION_NOTIFY_URL` is empty (default), so nothing contacts the internet unless you configure it. Tests mock `requests.post`. In production move the call to a background worker (Celery, Django-Q) so the user does not wait.
- **App name.** `forms` clashes in meaning with `django.forms`. It works because ours is imported as `forms` and Django's as `django.forms`, but a name like `registrations` is clearer in real projects.
