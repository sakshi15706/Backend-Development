# Unit 3 (P-6): Caching and Performance Optimization in Django (Lecture 31)

**PBL:** a Student API is slow because it fetches each student's department with a separate query (N+1) and recalculates the same statistics on every request. Reduce response time and database load, and compare before and after.

Builds on P-5. New here: `Department` (ForeignKey) and `Course` (ManyToMany) models, the N+1 view and its `select_related()` fix, `prefetch_related()`, a low-level cache with invalidation, a per-view cache for public data, pagination, a `measure_performance` command and 27 tests.

## Setup
```bash
cd "unit-3(P-6)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py measure_performance          # the before/after table (below)
python manage.py test                         # 81 tests
```

## Endpoints
| URL | What it shows |
|---|---|
| `/api/students/slow/` | **BEFORE**: N+1, one extra query per student (kept only for measuring) |
| `/api/students/` | **AFTER**: `select_related("department")`, one JOIN query, paginated (`?page=2&page_size=50`, max 100) |
| `/api/students/courses/` | `prefetch_related("courses")` for the many-to-many relation (2 queries, not 1 + N) |
| `/api/students/names/` | `values("id", "name")`: only the columns needed |
| `/api/students/summary/` | **low-level cache** (`cache.get/set`, 5 minutes); header `X-Cache: MISS` then `HIT` |
| `/api/departments/` | **per-view cache** (`@cache_page(300)`), public data only |

Student endpoints need a login (Lecture 30). Log in at `/accounts/login/` first, or use Django admin to create users.

## Measured results (your numbers will differ)
`python manage.py measure_performance` seeds temporary data inside a transaction and rolls it back afterwards (your database is untouched). Run on my sandbox with SQLite, 500 students, 10 departments, page size 100; the session and user lookups of a logged-in request (2 queries) are included in every count:

| Request | DB queries | ms (median) | cache |
|---|---|---|---|
| student list BEFORE (N+1) | **104** | 15.14 | - |
| student list AFTER (`select_related`) | **4** | 2.16 | - |
| students + courses (`prefetch_related`) | 5 | 6.42 | - |
| summary, 1st request | 6 | 1.75 | MISS |
| summary, 2nd request | 2 | 0.83 | HIT |
| departments (`cache_page`), 1st | 1 | 1.25 | MISS |
| departments (`cache_page`), 2nd | 0 | 0.43 | HIT |

The query counts are exact and repeatable: 100 students on a page cost 100 extra queries before and none after. The millisecond figures are small because SQLite runs in the same process with no network; on a networked database each avoided query saves a round trip, so the real gain is larger. Do not quote a fixed percentage (the slide warns against it); run the command on your machine and use your own numbers. Responses before and after are verified identical.

## Metrics table for the report (slide section 12)
| Metric | Before | After |
|---|---|---|
| HTTP response time | N+1 view (measure) | `select_related` view (measure) |
| Number of database queries | 1 + N (+2) | 2 (+2) |
| Cache status | uncached / first request MISS | repeated request HIT |
| Response correctness | verified: identical JSON (`test_both_versions_return_identical_data`) | |
| Data freshness | verified by `SummaryCacheTests` | |

## Cache expiry and stale data (PBL task 7)
- **Expiry**: every entry has a timeout (`SUMMARY_CACHE_TIMEOUT`, 300 s). After it passes, the next request is a MISS and recomputes the value (`test_entry_expires_after_the_timeout`).
- **Stale data**: until expiry, a cached value does not know the database changed. Two strategies are used here:
  - the summary is **invalidated** by signals (`students/signals.py`) whenever a `Student` or `Department` is saved or deleted or enrolments change, so it is never stale for normal saves. Raw `bulk_create()` and SQL bypass signals, and a test shows the summary then lags (`test_without_invalidation_data_is_stale`);
  - `/api/departments/` uses `cache_page` and is **not** invalidated: it can be up to 5 minutes old (`test_per_view_cache_can_be_stale`). That is acceptable for public head-counts, not for anything that must be exact.

## Safe caching (the slide's security note)
`cache_page` stores the whole response under the URL, and later requests are answered **without running the view**, so a user-specific or permission-protected response could be served to someone else.
- The student list contains personal data, so it is **not** wrapped in `cache_page` (`test_student_list_is_not_page_cached`).
- The cached summary contains only counts and is the same for everyone (`test_cached_summary_holds_no_personal_data`).
- `/api/departments/` has only names and counts and is public.
- If personal data must be cached, use the low-level API with a per-user key (for example `f"student-list:{request.user.pk}"`) or `vary_on_cookie`, and think about invalidation.
- The slide's example stacks `@login_required` on `@cache_page`. Even though anonymous users are redirected, every logged-in user would then share one cached copy, which is why it is not used for the student list here.

## Evaluation mapping (10 marks)
| Criterion | Marks | Evidence |
|---|---|---|
| Query optimisation | 3 | `student_list` (`select_related`), `student_courses_view` (`prefetch_related`), `NPlusOneTests` |
| Caching implementation | 3 | `CACHES` in settings, `student_summary_view`, `department_list`, timeouts from settings, `SummaryCacheTests`, `PerViewCacheTests` |
| Performance testing | 2 | `measure_performance` table, query-count tests |
| Data correctness and security | 2 | identical-response test, invalidation, `SafeCachingTests` |

## Testing checklist from the slide
- [x] returns the expected student data (`test_both_versions_return_identical_data`)
- [x] query counts before and after (`NPlusOneTests`)
- [x] repeated requests reuse the cache (`test_first_request_misses_second_hits`, `PerViewCacheTests`)
- [x] cached data expires after the timeout (`test_entry_expires_after_the_timeout`)
- [x] updates and stale responses (`test_cache_is_invalidated_*`, `*_stale`)
- [x] no private data in cached responses (`SafeCachingTests`)
- [x] pagination (`PaginationTests`)

## Notes
- **Local-memory cache** is the default: no server needed, but each process has its own copy, so it is not shared between gunicorn workers. Set `REDIS_URL=redis://127.0.0.1:6379/1` (and `pip install redis`) to use Django's built-in Redis backend. The Redis path is untested here (no Redis server in my environment); the slides' `django-redis` package works as well.
- The admin list page uses `list_select_related`, the same fix for the admin.
- Tests clear the cache in `setUp`/`tearDown` because the local-memory cache would otherwise carry values from one test to the next.
- Index tip: a ForeignKey column is indexed automatically. Add `db_index=True` or `Meta.indexes` for other columns you filter on a lot, and measure first.
