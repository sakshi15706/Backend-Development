# PBL: introduce one routing error, predict, fix

The PBL asks you to break a route on purpose, **predict** the result first, then fix it. The three experiments below were actually run against this project (Django test client, `DEBUG=False`); do the same on your machine and screenshot the results.

Edit `students/urls.py` (or the project `urls.py`), restart / reload, then request `GET /api/students/42/`.

| # | Break it like this | Prediction | Actual result | Why |
|---|---|---|---|---|
| A | Rename the converter: `path("<int:id>/", views.student_detail)` | The URL matches, but the view is called with `id=42` and it only accepts `student_id` | **500** (`TypeError: student_detail() got an unexpected keyword argument 'id'`) | The name inside `<int:...>` must equal the view's argument name (Task 4 table: "TypeError about student_id") |
| B | Change the path so it no longer matches: `path("<str:student_id>/x/", ...)` | No pattern matches `/api/students/42/` | **404** | Pattern/prefix/trailing slash mismatch |
| C | Remove the trailing slash: `path("<int:student_id>", ...)` | The URL with a slash no longer matches | **404** | Django patterns are literal; `/42/` is not `/42` |

**Fix:** restore `path("<int:student_id>/", views.student_detail, name="student-detail")`. Then run `python manage.py test` to confirm the routes work again.

## Other symptoms from Task 4
| Symptom | Likely cause | How to check |
|---|---|---|
| `ModuleNotFoundError` | wrong import or app location | is `students` next to `manage.py` and in `INSTALLED_APPS`? |
| Middleware does not log | wrong dotted path in `MIDDLEWARE` or server not restarted | the path must be `students.middleware.SimpleLoggingMiddleware` |
| No log output at all | logger level filters it | `LOGGING` in `settings.py` sets the `students` logger to INFO |

## Execution order (explain this in the viva)
`MIDDLEWARE` is processed **top to bottom** on the way in and **bottom to top** on the way out:

```
request  -> SimpleLoggingMiddleware (log request, start timer)
         -> Security / Session / Common / CSRF / Auth / Messages ...
         -> URLconf -> view
response <- ... <- SimpleLoggingMiddleware (log status + elapsed ms)
```
Because our middleware is first, its timer includes everything the other middleware and the view do.
