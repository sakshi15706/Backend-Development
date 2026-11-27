"""Tests for the middleware and routes of this practical (run: python manage.py test)."""
from django.test import SimpleTestCase
from django.urls import NoReverseMatch, resolve, reverse


class RoutingTests(SimpleTestCase):
    def test_health_route(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_student_list_route(self):
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["students"], [])

    def test_student_detail_route_passes_int_parameter(self):
        response = self.client.get("/api/students/42/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["student_id"], 42)

    def test_non_integer_id_does_not_match(self):
        # <int:student_id> only matches digits, so this is a 404, not a server error.
        self.assertEqual(self.client.get("/api/students/abc/").status_code, 404)

    def test_missing_trailing_slash_is_redirected(self):
        # APPEND_SLASH (default) redirects /api/students/42 to /api/students/42/
        response = self.client.get("/api/students/42")
        self.assertEqual(response.status_code, 301)

    def test_url_names_reverse(self):
        self.assertEqual(reverse("student-list"), "/api/students/")
        self.assertEqual(reverse("student-detail", kwargs={"student_id": 7}), "/api/students/7/")
        self.assertEqual(resolve("/api/students/7/").kwargs, {"student_id": 7})

    def test_detail_name_needs_its_parameter(self):
        with self.assertRaises(NoReverseMatch):
            reverse("student-detail")


class MiddlewareTests(SimpleTestCase):
    def test_logs_request_and_response(self):
        with self.assertLogs("students.middleware", level="INFO") as logs:
            self.client.get("/api/health/")
        joined = "\n".join(logs.output)
        self.assertIn("Request: GET /api/health/", joined)
        self.assertIn("Response: 200 in", joined)
        self.assertIn("ms", joined)

    def test_logs_error_status_code(self):
        with self.assertLogs("students.middleware", level="INFO") as logs:
            self.client.get("/api/does-not-exist/")
        self.assertIn("Response: 404", "\n".join(logs.output))

    def test_logs_query_string(self):
        with self.assertLogs("students.middleware", level="INFO") as logs:
            self.client.get("/api/students/?page=2")
        self.assertIn("/api/students/?page=2", "\n".join(logs.output))

    def test_middleware_is_registered_first(self):
        from django.conf import settings
        self.assertEqual(settings.MIDDLEWARE[0], "students.middleware.SimpleLoggingMiddleware")
        self.assertIn("django.contrib.sessions.middleware.SessionMiddleware", settings.MIDDLEWARE)

    def test_response_is_returned_unchanged(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response["Content-Type"], "application/json")
