# PBL: diagnose an intentionally introduced defect (Task 5)

This was actually run against this project.

## 1. Expected behaviour (write it down first)
`GET /api/health/` returns **HTTP 200** and `{"status": "ok"}`.

## 2. Introduce the defect
In `students/views.py`:
```python
def health_check(request):
    return JsonResponse({"status": "ok"}, status=201)     # <-- bug: should be 200
```

## 3. Reproduce with the test
```bash
python manage.py test students.tests.StudentAPITest.test_health_endpoint
```
Output (trimmed):
```
FAIL: test_health_endpoint (students.tests.StudentAPITest.test_health_endpoint)
AssertionError: 201 != 200
Ran 1 test in 0.008s
FAILED (failures=1)
```

## 4. Read it from the bottom up
- Last line: `201 != 200` means the **actual** status was 201 and the test **expected** 200 (`assertEqual(first, second)`; first is `response.status_code`).
- The traceback points at the assertion line in `students/tests.py`; follow it back to the code that produced the response: `health_check` in `students/views.py`.
- The log line from the middleware (`Response: 201 in ... ms`) confirms the same thing from the running application's side.

## 5. Fix the code, not the test
Restore `status=200` (the default). Do **not** change the test to expect 201: the requirement is 200, and a test must describe required behaviour, not hide a defect.

## 6. Re-run
```bash
python manage.py test students.tests.StudentAPITest.test_health_endpoint   # OK
python manage.py test                                                       # whole suite, check for regressions
```

## Debugging checklist
1. Write down the expected behaviour.
2. Reproduce with a test.
3. Read the failure and traceback bottom-up.
4. Inspect the first application line involved.
5. Fix, then re-run the focused test.
6. Run the full suite.
