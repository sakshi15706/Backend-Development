"""python manage.py measure_performance [--students 500] [--departments 10] [--courses 8]

Produces the BEFORE / AFTER table the Lecture 31 PBL asks for:
  * the N+1 list view vs the select_related() list view  (query count + time)
  * the first (cache MISS) and second (cache HIT) request to the summary and department views

Everything runs inside a database transaction that is rolled back at the end, so your own
data is untouched.  Timings depend on your machine, database and data size; the query
COUNTS are exact.
"""
import logging
import statistics
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.test import Client
from django.test.utils import CaptureQueriesContext, override_settings
from django.urls import reverse

from students.cache_keys import SUMMARY_KEY
from students.models import Course, Department, Student


class Command(BaseCommand):
    help = "Measure query counts, response time and cache behaviour before/after optimisation."

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=500)
        parser.add_argument("--departments", type=int, default=10)
        parser.add_argument("--courses", type=int, default=8)
        parser.add_argument("--repeat", type=int, default=5, help="timing repetitions (median is reported)")

    def handle(self, *args, **opts):
        logging.disable(logging.CRITICAL)           # keep the middleware's per-request log out of the table
        try:
            with override_settings(ALLOWED_HOSTS=["*"]), transaction.atomic():
                self._run(opts)
                transaction.set_rollback(True)      # undo the seeded rows
        finally:
            logging.disable(logging.NOTSET)
            cache.delete(SUMMARY_KEY)

    # ------------------------------------------------------------------------------
    def _seed(self, n, n_dept, n_course):
        depts = Department.objects.bulk_create([Department(name=f"PERF-Dept-{i}") for i in range(n_dept)])
        courses = Course.objects.bulk_create([Course(name=f"PERF-Course-{i}") for i in range(n_course)])
        base = Student.objects.count()
        students = Student.objects.bulk_create([
            Student(name=f"PERF Student {i}", email=f"perf{base + i}@example.invalid", department=depts[i % n_dept])
            for i in range(n)
        ])
        links = []
        through = Student.courses.through
        for i, s in enumerate(students):
            for c in courses[: 1 + i % n_course]:
                links.append(through(student_id=s.pk, course_id=c.pk))
        through.objects.bulk_create(links)

    def _get(self, client, name, **params):
        with CaptureQueriesContext(connection) as ctx:
            start = time.perf_counter()
            response = client.get(reverse(name), params)
            elapsed = (time.perf_counter() - start) * 1000
        return response, len(ctx.captured_queries), elapsed

    def _median(self, client, name, repeat, **params):
        runs = [self._get(client, name, **params) for _ in range(repeat)]
        return runs[0][0], runs[0][1], statistics.median(r[2] for r in runs)

    def _run(self, opts):
        n = opts["students"]
        self._seed(n, opts["departments"], opts["courses"])
        user = get_user_model().objects.create_user("perf-user", password="x")
        client = Client()
        client.force_login(user)
        page_size = min(n, 100)
        self.stdout.write(f"\nData: {n} students, {opts['departments']} departments, {opts['courses']} courses "
                          f"(page_size={page_size}; session + user lookups = 2 queries are included in every count)\n")

        rows = []
        for label, name in [("student list BEFORE (N+1)", "student-list-slow"),
                            ("student list AFTER  (select_related)", "student-list")]:
            response, queries, ms = self._median(client, name, opts["repeat"], page_size=page_size)
            rows.append((label, queries, ms, "-", response.status_code))
        resp_slow = client.get(reverse("student-list-slow"), {"page_size": page_size}).json()
        resp_fast = client.get(reverse("student-list"), {"page_size": page_size}).json()
        same = resp_slow == resp_fast

        response, queries, ms = self._median(client, "student-courses", opts["repeat"], page_size=page_size)
        rows.append(("students + courses (prefetch_related)", queries, ms, "-", response.status_code))

        cache.delete(SUMMARY_KEY)
        miss, q_miss, t_miss = self._get(client, "student-summary")
        hit, q_hit, t_hit = self._get(client, "student-summary")
        rows.append(("summary, 1st request", q_miss, t_miss, miss["X-Cache"], miss.status_code))
        rows.append(("summary, 2nd request", q_hit, t_hit, hit["X-Cache"], hit.status_code))

        cache.clear()
        d1, q1, t1 = self._get(client, "department-list")
        d2, q2, t2 = self._get(client, "department-list")
        rows.append(("departments (cache_page), 1st", q1, t1, "MISS", d1.status_code))
        rows.append(("departments (cache_page), 2nd", q2, t2, "HIT" if q2 == 0 else "MISS", d2.status_code))

        header = f"{'Request':42} {'DB queries':>10} {'ms (median)':>12} {'cache':>6} {'HTTP':>5}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for label, q, ms, cache_state, status in rows:
            self.stdout.write(f"{label:42} {q:>10} {ms:>12.2f} {cache_state:>6} {status:>5}")
        self.stdout.write(f"\nResponse correctness: slow and optimised student lists identical = {same}")
        self.stdout.write("Note: the 1st request of each pair is a single measurement, the list rows are medians.")
