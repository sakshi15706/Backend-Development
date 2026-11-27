from django.conf import settings
from django.test import SimpleTestCase


class MiddlewareTests(SimpleTestCase):
    def test_logs_request_and_response(self):
        with self.assertLogs("students.middleware", level="INFO") as logs:
            self.client.get("/api/health/")
        joined = "\n".join(logs.output)
        self.assertIn("Request: GET /api/health/", joined)
        self.assertIn("Response: 200 in", joined)

    def test_logs_error_status_code(self):
        with self.assertLogs("students.middleware", level="INFO") as logs:
            self.client.get("/api/does-not-exist/")
        self.assertIn("Response: 404", "\n".join(logs.output))

    def test_registered_first(self):
        self.assertEqual(settings.MIDDLEWARE[0], "students.middleware.SimpleLoggingMiddleware")
