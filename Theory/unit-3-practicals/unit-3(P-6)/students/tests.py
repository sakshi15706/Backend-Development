"""Lecture 29: tests for the Student API.

Run everything:        python manage.py test
Run one class:         python manage.py test students.tests.StudentAPITest
Run one method:        python manage.py test students.tests.StudentAPITest.test_health_endpoint
More detail / stop early:  python manage.py test -v 2   |   python manage.py test --failfast
"""
from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import NoReverseMatch, reverse

from .models import Student
from .utils import get_external_data


# ---------------------------------------------------------------- endpoint tests
class StudentAPITest(TestCase):
    def test_health_endpoint(self):
        # self.client behaves like a tiny browser; reverse() looks the URL up by NAME
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_health_is_json(self):
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response["Content-Type"], "application/json")


class StudentRouteTest(TestCase):
    # Since Lecture 30 the list and detail views need a logged-in user (see test_auth.py for
    # the anonymous / permission cases), so these tests log in first.
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user("tester", password="pw-12345-x"))

    def test_student_detail_returns_record(self):
        # create the data INSIDE the test; never rely on your development database
        student = Student.objects.create(name="Aarav", email="aarav@example.com")
        response = self.client.get(reverse("student-detail", kwargs={"student_id": student.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["student_id"], student.id)
        self.assertEqual(response.json()["name"], "Aarav")
        self.assertEqual(response.json()["email"], "aarav@example.com")

    def test_unknown_student_returns_404_with_message(self):
        response = self.client.get(reverse("student-detail", kwargs={"student_id": 9999}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "Student not found")

    def test_detail_url_needs_its_parameter(self):
        # common mistake from the slide: reverse("student-detail") without kwargs
        with self.assertRaises(NoReverseMatch):
            reverse("student-detail")

    def test_list_empty(self):
        response = self.client.get(reverse("student-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["students"], [])
        self.assertEqual(response.json()["count"], 0)

    def test_list_returns_all_students_with_fields(self):
        Student.objects.create(name="Aarav", email="aarav@example.com")
        Student.objects.create(name="Neha", email="neha@example.com")
        data = self.client.get(reverse("student-list")).json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["students"]), 2)
        self.assertEqual([s["name"] for s in data["students"]], ["Aarav", "Neha"])
        self.assertEqual(set(data["students"][0]), {"student_id", "name", "email", "department"})

    def test_tests_are_isolated_from_each_other(self):
        # Another test created students, but Django rolls the database back after each test.
        self.assertEqual(Student.objects.count(), 0)

    def test_unknown_url_is_404(self):
        self.assertEqual(self.client.get("/api/nope/").status_code, 404)


# ---------------------------------------------------------------- model tests
class StudentModelTest(TestCase):
    def test_saved_correctly(self):
        student = Student.objects.create(name="Aarav", email="aarav@example.com")
        student.refresh_from_db()
        self.assertEqual(student.name, "Aarav")
        self.assertIsNotNone(student.created_at)

    def test_str(self):
        self.assertEqual(str(Student(name="Aarav", email="a@x.com")), "Aarav <a@x.com>")

    def test_email_must_be_unique(self):
        Student.objects.create(name="A", email="same@example.com")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Student.objects.create(name="B", email="same@example.com")


# ------------------------------------------------- mocked external service tests
class ExternalServiceTest(SimpleTestCase):
    # patch the place where the code LOOKS UP the dependency: students.utils.requests.get
    @patch("students.utils.requests.get")
    def test_timeout_returns_safe_error(self, mock_get):
        mock_get.side_effect = requests.Timeout
        result = get_external_data(1)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "External service timed out")

    @patch("students.utils.requests.get")
    def test_success_returns_data(self, mock_get):
        mock_get.return_value.json.return_value = {"name": "Aarav"}
        mock_get.return_value.raise_for_status.return_value = None
        result = get_external_data(1)
        self.assertEqual(result["data"]["name"], "Aarav")
        self.assertIsNone(result["error"])

    @patch("students.utils.requests.get")
    def test_view_maps_failure_to_503(self, mock_get):
        mock_get.side_effect = requests.ConnectionError
        response = self.client.get(reverse("external-data", kwargs={"post_id": 1}))
        self.assertEqual(response.status_code, 503)
