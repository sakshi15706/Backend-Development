"""Tests for the registration form. Run: python manage.py test forms

These cover the checklist from the tutorial: empty form, invalid e-mail, age below 16,
valid data, duplicate e-mail, refresh after success, CSRF, logging and the external call.
No test touches the real internet.
"""
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import StudentRegistrationForm
from .models import StudentRegistration
from .services import notify_registration

VALID = {
    "name": "Aarav Sharma",
    "email": "aarav@example.com",
    "age": "20",
    "phone": "9876543210",
    "course": "BCA",
    "agree_to_rules": "on",
}


def data(**changes):
    d = dict(VALID)
    d.update(changes)
    return d


class FormValidationTests(TestCase):
    """Form-level tests (no view). TestCase, not SimpleTestCase: a ModelForm checks that the
    e-mail is unique, which queries the database."""

    def errors(self, **changes):
        form = StudentRegistrationForm(data(**changes))
        form.is_valid()
        return form.errors

    def test_empty_form_reports_required_fields(self):
        form = StudentRegistrationForm({})
        self.assertFalse(form.is_valid())
        for field in ("name", "email", "age", "course", "agree_to_rules"):
            self.assertIn(field, form.errors)

    def test_phone_is_optional(self):
        self.assertNotIn("phone", self.errors(phone=""))

    def test_invalid_email(self):
        self.assertIn("email", self.errors(email="not-an-email"))

    def test_age_below_minimum(self):
        self.assertEqual(self.errors(age="15")["age"], ["The student must be at least 16 years old."])

    def test_age_boundary_16_is_accepted(self):
        self.assertNotIn("age", self.errors(age="16"))

    def test_age_above_maximum(self):
        self.assertIn("age", self.errors(age="101"))

    def test_age_must_be_a_number(self):
        self.assertIn("age", self.errors(age="twenty"))

    def test_negative_age_rejected(self):
        self.assertIn("age", self.errors(age="-5"))

    def test_phone_must_be_ten_digits(self):
        self.assertIn("phone", self.errors(phone="12345"))
        self.assertIn("phone", self.errors(phone="98765abcde"))
        self.assertNotIn("phone", self.errors(phone="9876543210"))

    def test_course_must_be_in_the_list(self):
        self.assertIn("course", self.errors(course="Underwater Basket Weaving"))

    def test_must_agree_to_rules(self):
        errors = self.errors(agree_to_rules="")
        self.assertEqual(errors["agree_to_rules"], ["You must agree to the rules to register."])

    def test_name_whitespace_is_cleaned(self):
        form = StudentRegistrationForm(data(name="  Aarav    Sharma  "))
        form.is_valid()
        self.assertEqual(form.cleaned_data["name"], "Aarav Sharma")

    def test_one_letter_name_rejected(self):
        self.assertIn("name", self.errors(name=" A "))


class RegisterViewTests(TestCase):
    url = property(lambda self: reverse("forms_app:register"))

    def test_get_shows_empty_form_with_csrf_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, 'enctype="multipart/form-data"', count=0)   # a plain form, no files
        self.assertEqual(StudentRegistration.objects.count(), 0)

    def test_namespaced_url(self):
        self.assertEqual(self.url, "/forms/register/")

    def test_valid_post_saves_and_redirects_to_success(self):
        response = self.client.post(self.url, data())
        self.assertRedirects(response, reverse("forms_app:registration-success"))
        saved = StudentRegistration.objects.get()
        self.assertEqual((saved.name, saved.email, saved.age, saved.course), ("Aarav Sharma", "aarav@example.com", 20, "BCA"))
        self.assertEqual(saved.phone, "9876543210")

    def test_agree_checkbox_is_not_stored(self):
        self.client.post(self.url, data())
        self.assertFalse(hasattr(StudentRegistration.objects.get(), "agree_to_rules"))

    def test_success_page_shows_message_once(self):
        response = self.client.post(self.url, data(), follow=True)
        self.assertContains(response, "Student registration submitted successfully.")
        again = self.client.get(reverse("forms_app:registration-success"))
        self.assertNotContains(again, "submitted successfully")          # messages are shown once

    def test_refreshing_success_page_does_not_resubmit(self):
        self.client.post(self.url, data())
        for _ in range(3):                                               # refresh = GET again
            self.client.get(reverse("forms_app:registration-success"))
        self.assertEqual(StudentRegistration.objects.count(), 1)

    def test_empty_post_shows_errors_and_saves_nothing(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertEqual(StudentRegistration.objects.count(), 0)

    def test_invalid_email_shows_error(self):
        response = self.client.post(self.url, data(email="bad"))
        self.assertContains(response, "Enter a valid email address")

    def test_age_below_16_shows_custom_error(self):
        response = self.client.post(self.url, data(age="15"))
        self.assertContains(response, "The student must be at least 16 years old.")
        self.assertEqual(StudentRegistration.objects.count(), 0)

    def test_invalid_post_keeps_what_the_user_typed(self):
        response = self.client.post(self.url, data(age="15"))
        self.assertContains(response, 'value="Aarav Sharma"')            # form built from request.POST

    def test_duplicate_email_is_rejected(self):
        self.client.post(self.url, data())
        response = self.client.post(self.url, data(name="Someone Else"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(StudentRegistration.objects.count(), 1)

    def test_duplicate_email_ignores_letter_case(self):
        self.client.post(self.url, data())
        response = self.client.post(self.url, data(email="AARAV@Example.COM"))
        self.assertContains(response, "already exists")

    def test_database_integrity_error_is_shown_as_form_error(self):
        # simulate the race: validation passes, then the database refuses the row
        with patch("forms.forms.StudentRegistrationForm.save", side_effect=IntegrityError):
            response = self.client.post(self.url, data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A student with this email already exists.")

    def test_post_without_csrf_token_is_forbidden(self):
        strict = Client(enforce_csrf_checks=True)       # the normal test client skips CSRF checks
        self.assertEqual(strict.post(self.url, data()).status_code, 403)
        self.assertEqual(StudentRegistration.objects.count(), 0)

    def test_get_is_the_only_other_allowed_flow(self):
        # the view treats every non-POST as a fresh form
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_html_in_name_is_escaped_on_the_list_page(self):
        StudentRegistration.objects.create(name="<script>alert(1)</script>", email="x@example.com", age=20, course="BCA")
        self.client.force_login(get_user_model().objects.create_superuser("root", password="pw-12345-x"))
        response = self.client.get(reverse("forms_app:registration-list"))
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")


class LoggingTests(TestCase):
    def test_view_logs_id_and_middleware_logs_request(self):
        with self.assertLogs("forms.views", level="INFO") as view_logs, \
                self.assertLogs("students.middleware", level="INFO") as mw_logs:
            self.client.post(reverse("forms_app:register"), data())
        student = StudentRegistration.objects.get()
        self.assertTrue(any(f"id={student.id}" in line for line in view_logs.output))
        self.assertFalse(any("aarav@example.com" in line for line in view_logs.output))   # no e-mail in the log
        self.assertTrue(any("POST /forms/register/" in line for line in mw_logs.output))   # request-level log
        self.assertTrue(any("Response: 302" in line for line in mw_logs.output))


class ListPageTests(TestCase):
    def test_anonymous_cannot_see_the_list(self):
        response = self.client.get(reverse("forms_app:registration-list"))
        self.assertEqual(response.status_code, 302)

    def test_staff_sees_registrations(self):
        StudentRegistration.objects.create(name="Neha", email="n@example.com", age=19, course="MCA")
        self.client.force_login(get_user_model().objects.create_user("st", password="pw-12345-x", is_staff=True))
        self.assertContains(self.client.get(reverse("forms_app:registration-list")), "Neha")


class ModelTests(TestCase):
    def test_str(self):
        self.assertEqual(str(StudentRegistration(name="Neha", course="MCA")), "Neha - MCA")

    def test_email_unique_in_database(self):
        StudentRegistration.objects.create(name="A", email="a@example.com", age=20, course="BCA")
        with self.assertRaises(IntegrityError):
            StudentRegistration.objects.create(name="B", email="a@example.com", age=21, course="BCA")


# ---------------------------------------------------------- external API, mocked
class NotifyServiceTests(TestCase):
    student_kwargs = dict(name="Aarav", email="a@example.com", age=20, course="BCA")

    @override_settings(REGISTRATION_NOTIFY_URL="https://notify.example.test/registrations", REGISTRATION_NOTIFY_TIMEOUT=5)
    @patch("forms.services.requests.post")
    def test_posts_payload_with_timeout(self, mock_post):
        mock_post.return_value = Mock(raise_for_status=Mock())
        student = StudentRegistration.objects.create(**self.student_kwargs)
        self.assertTrue(notify_registration(student))
        mock_post.assert_called_once_with(
            "https://notify.example.test/registrations",
            json={"student_id": student.id, "name": "Aarav", "course": "BCA"},
            timeout=5,
        )

    @override_settings(REGISTRATION_NOTIFY_URL="https://notify.example.test/registrations")
    @patch("forms.services.requests.post", side_effect=requests.Timeout)
    def test_timeout_returns_false_and_logs(self, mock_post):
        student = StudentRegistration.objects.create(**self.student_kwargs)
        with self.assertLogs("forms.services", level="ERROR"):
            self.assertFalse(notify_registration(student))

    @override_settings(REGISTRATION_NOTIFY_URL="https://notify.example.test/registrations")
    @patch("forms.services.requests.post")
    def test_http_error_returns_false(self, mock_post):
        mock_post.return_value.raise_for_status.side_effect = requests.HTTPError("500")
        student = StudentRegistration.objects.create(**self.student_kwargs)
        with self.assertLogs("forms.services", level="ERROR"):
            self.assertFalse(notify_registration(student))

    @override_settings(REGISTRATION_NOTIFY_URL="")
    @patch("forms.services.requests.post")
    def test_not_configured_means_no_call(self, mock_post):
        student = StudentRegistration.objects.create(**self.student_kwargs)
        self.assertFalse(notify_registration(student))
        mock_post.assert_not_called()

    @override_settings(REGISTRATION_NOTIFY_URL="https://notify.example.test/registrations")
    @patch("forms.services.requests.post", side_effect=requests.ConnectionError)
    def test_failed_notification_does_not_break_registration(self, mock_post):
        with self.assertLogs("forms.services", level="ERROR"):
            response = self.client.post(reverse("forms_app:register"), data())
        self.assertRedirects(response, reverse("forms_app:registration-success"))
        self.assertEqual(StudentRegistration.objects.count(), 1)           # saved anyway

    @override_settings(REGISTRATION_NOTIFY_URL="https://notify.example.test/registrations")
    @patch("forms.services.requests.post")
    def test_notification_only_after_valid_save(self, mock_post):
        self.client.post(reverse("forms_app:register"), data(age="10"))    # invalid
        mock_post.assert_not_called()
        mock_post.return_value = Mock(raise_for_status=Mock())
        self.client.post(reverse("forms_app:register"), data())            # valid
        mock_post.assert_called_once()
