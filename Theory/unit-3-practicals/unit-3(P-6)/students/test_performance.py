"""Lecture 31 tests: query optimisation, caching, pagination, safe caching.

Query COUNTS are asserted, not times: counts are exact and the same on every machine,
while timings vary.  The pattern is: run the same view with a small and a large data set;
an optimised view issues the same number of queries for both.
"""
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .cache_keys import SUMMARY_KEY
from .models import Course, Department, Student

User = get_user_model()


def make_students(n, departments=3, courses=3):
    depts = [Department.objects.get_or_create(name=f"Dept {i}")[0] for i in range(departments)]
    crs = [Course.objects.get_or_create(name=f"Course {i}")[0] for i in range(courses)]
    start = Student.objects.count()
    created = []
    for i in range(n):
        s = Student.objects.create(name=f"Student {start + i}", email=f"s{start + i}@example.com",
                                   department=depts[i % departments])
        s.courses.set(crs[: 1 + i % courses])
        created.append(s)
    return created


class PerfTestCase(TestCase):
    def setUp(self):
        cache.clear()                                   # LocMem cache is shared across tests otherwise
        self.client.force_login(User.objects.create_user("tester", password="pw-12345-x"))

    def queries_for(self, url_name):
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200)
        # the session lookup and the user lookup of the logged-in client are always there
        return len(ctx.captured_queries), response

    def tearDown(self):
        cache.clear()


class NPlusOneTests(PerfTestCase):
    def test_slow_view_runs_one_query_per_student(self):
        make_students(5)
        few, _ = self.queries_for("student-list-slow")
        make_students(10)
        many, _ = self.queries_for("student-list-slow")
        self.assertEqual(many - few, 10)                # 10 more students = exactly 10 more queries

    def test_optimised_view_query_count_does_not_depend_on_data_size(self):
        make_students(5)
        few, _ = self.queries_for("student-list")
        make_students(15)                               # 20 students in total (page size is 20)
        many, _ = self.queries_for("student-list")
        self.assertEqual(few, many)

    def test_select_related_is_much_cheaper(self):
        make_students(15)
        slow, _ = self.queries_for("student-list-slow")
        fast, _ = self.queries_for("student-list")
        self.assertEqual(slow - fast, 15)               # saved one query per student
        self.assertLessEqual(fast, 4)                   # session + user + count + students

    def test_both_versions_return_identical_data(self):
        make_students(7)
        _, slow = self.queries_for("student-list-slow")
        _, fast = self.queries_for("student-list")
        self.assertEqual(slow.json(), fast.json())      # correctness is unchanged by the optimisation

    def test_prefetch_related_avoids_one_query_per_student_for_courses(self):
        make_students(5)
        few, _ = self.queries_for("student-courses")
        make_students(15)
        many, response = self.queries_for("student-courses")
        self.assertEqual(few, many)
        first = response.json()["students"][0]
        self.assertIn("courses", first)
        self.assertEqual(first["courses"], ["Course 0"])

    def test_values_view_returns_only_requested_columns(self):
        make_students(3)
        data = self.client.get(reverse("student-names")).json()
        self.assertEqual(set(data["students"][0]), {"id", "name"})

    def test_student_without_department_is_handled(self):
        Student.objects.create(name="No Dept", email="nd@example.com")
        data = self.client.get(reverse("student-list")).json()
        self.assertIsNone(data["students"][0]["department"])

    def test_detail_uses_single_joined_query(self):
        student = make_students(1)[0]
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse("student-detail", kwargs={"student_id": student.id}))
        self.assertEqual(response.json()["department"], "Dept 0")
        self.assertEqual(len(ctx.captured_queries), 3)  # session + user + student JOIN department


class PaginationTests(PerfTestCase):
    def test_default_page_size(self):
        make_students(25)
        data = self.client.get(reverse("student-list")).json()
        self.assertEqual(len(data["students"]), 20)
        self.assertEqual((data["count"], data["total_pages"], data["page"]), (25, 2, 1))

    def test_second_page(self):
        make_students(25)
        data = self.client.get(reverse("student-list"), {"page": 2}).json()
        self.assertEqual(len(data["students"]), 5)

    def test_page_size_is_capped(self):
        make_students(5)
        data = self.client.get(reverse("student-list"), {"page_size": 100000}).json()
        self.assertEqual(data["page_size"], 100)

    def test_bad_parameters_do_not_crash(self):
        make_students(3)
        response = self.client.get(reverse("student-list"), {"page": "abc", "page_size": "x"})
        self.assertEqual(response.status_code, 200)

    def test_page_beyond_the_end_returns_last_page(self):
        make_students(3)
        self.assertEqual(self.client.get(reverse("student-list"), {"page": 99}).json()["page"], 1)


class SummaryCacheTests(PerfTestCase):
    def test_first_request_misses_second_hits(self):
        make_students(5)
        first_queries, first = self.queries_for("student-summary")
        second_queries, second = self.queries_for("student-summary")
        self.assertEqual(first["X-Cache"], "MISS")
        self.assertEqual(second["X-Cache"], "HIT")
        self.assertGreater(first_queries, second_queries)
        self.assertEqual(second_queries, 2)             # only session + user: NO summary queries
        self.assertEqual(first.json(), second.json())   # correctness verified

    def test_summary_values(self):
        make_students(6, departments=2, courses=3)
        Student.objects.create(name="X", email="x@example.com")
        data = self.client.get(reverse("student-summary")).json()
        self.assertEqual(data, {
            "total_students": 7, "total_departments": 2, "total_courses": 3,
            "students_without_department": 1,
        })

    def test_cache_is_invalidated_when_a_student_is_added(self):
        make_students(2)
        self.assertEqual(self.client.get(reverse("student-summary")).json()["total_students"], 2)
        make_students(1)                                # signal clears the key
        response = self.client.get(reverse("student-summary"))
        self.assertEqual(response["X-Cache"], "MISS")
        self.assertEqual(response.json()["total_students"], 3)

    def test_cache_is_invalidated_when_a_student_is_deleted(self):
        students = make_students(3)
        self.client.get(reverse("student-summary"))
        students[0].delete()
        self.assertEqual(self.client.get(reverse("student-summary")).json()["total_students"], 2)

    def test_without_invalidation_data_is_stale(self):
        """What the slide warns about: bypass the signals with a raw bulk insert."""
        make_students(2)
        self.client.get(reverse("student-summary"))
        Student.objects.bulk_create([Student(name="Raw", email="raw@example.com")])   # no post_save signal
        stale = self.client.get(reverse("student-summary")).json()
        self.assertEqual(stale["total_students"], 2)    # cached value, one student behind
        self.assertEqual(Student.objects.count(), 3)

    @override_settings(SUMMARY_CACHE_TIMEOUT=1)
    def test_entry_expires_after_the_timeout(self):
        make_students(2)
        self.client.get(reverse("student-summary"))
        self.assertIsNotNone(cache.get(SUMMARY_KEY))
        time.sleep(1.2)
        self.assertIsNone(cache.get(SUMMARY_KEY))       # expired by itself
        self.assertEqual(self.client.get(reverse("student-summary"))["X-Cache"], "MISS")

    def test_summary_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("student-summary")).status_code, 302)

    def test_cached_summary_holds_no_personal_data(self):
        make_students(2)
        self.client.get(reverse("student-summary"))
        cached = str(cache.get(SUMMARY_KEY))
        self.assertNotIn("@", cached)                   # no e-mail addresses
        self.assertNotIn("Student", cached)             # no names


class PerViewCacheTests(PerfTestCase):
    def test_department_list_is_cached_for_five_minutes(self):
        make_students(4)
        first_queries, first = self.queries_for("department-list")
        second_queries, second = self.queries_for("department-list")
        self.assertGreater(first_queries, 0)
        self.assertEqual(second_queries, 0)             # served from cache: not even a session lookup
        self.assertEqual(first.json(), second.json())
        self.assertIn("max-age=300", second["Cache-Control"])

    def test_department_list_is_public_and_has_no_personal_data(self):
        make_students(3)
        self.client.logout()
        response = self.client.get(reverse("department-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"@", response.content)
        self.assertEqual(set(response.json()["departments"][0]), {"id", "name", "student_count"})

    def test_per_view_cache_can_be_stale(self):
        make_students(3, departments=1)
        before = self.client.get(reverse("department-list")).json()["departments"][0]["student_count"]
        make_students(2, departments=1)
        after = self.client.get(reverse("department-list")).json()["departments"][0]["student_count"]
        self.assertEqual(before, after)                 # still the old number: cache_page is not invalidated


class SafeCachingTests(PerfTestCase):
    """The slide's security note: do not put shared caching on personal data."""

    def test_student_list_is_not_page_cached(self):
        make_students(2)
        response = self.client.get(reverse("student-list"))
        self.assertNotIn("max-age", response.get("Cache-Control", ""))

    def test_student_list_shows_new_data_immediately(self):
        make_students(2)
        self.assertEqual(self.client.get(reverse("student-list")).json()["count"], 2)
        make_students(1)
        self.assertEqual(self.client.get(reverse("student-list")).json()["count"], 3)

    def test_anonymous_user_never_receives_cached_student_list(self):
        make_students(2)
        self.client.get(reverse("student-list"))        # a logged-in user primes whatever caches exist
        self.client.logout()
        response = self.client.get(reverse("student-list"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(b"@example.com", response.content)
