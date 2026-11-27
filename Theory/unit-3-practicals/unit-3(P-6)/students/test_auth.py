"""Lecture 30 test cases (the table in the slides) plus a few extras.

| Test case                         | User state              | Expected                    |
| Access protected view             | Anonymous               | Redirect to login page      |
| Access protected view             | Authenticated user      | View executes               |
| Access permission-protected view  | User without permission | Access denied (403)         |
| Access permission-protected view  | User with permission    | View executes               |
| Submit a valid login form         | Valid credentials       | Session established         |
| Submit an invalid login form      | Invalid credentials     | Login rejected              |
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import Student

User = get_user_model()
PASSWORD = "pw-12345-x"


def make_user(username="regular", **extra):
    return User.objects.create_user(username, password=PASSWORD, **extra)


def give_permission(user, codename="view_student"):
    user.user_permissions.add(Permission.objects.get(content_type__app_label="students", codename=codename))
    # permissions are cached on the user object; re-fetch so the new permission is seen
    return User.objects.get(pk=user.pk)


class LoginRequiredTests(TestCase):
    """Authentication: who are you?"""

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("secure-data"))
        self.assertEqual(response.status_code, 302)            # a redirect is NOT a 403
        self.assertEqual(response.url, "/accounts/login/?next=/api/students/secure-data/")

    def test_authenticated_user_sees_view(self):
        self.client.force_login(make_user())
        response = self.client.get(reverse("secure-data"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "You are authenticated.", "username": "regular"})

    def test_student_list_is_protected(self):
        # PBL task: anonymous visitors must not access the student list
        Student.objects.create(name="Aarav", email="a@example.com")
        response = self.client.get(reverse("student-list"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(b"Aarav", response.content)

    def test_student_detail_is_protected(self):
        student = Student.objects.create(name="Aarav", email="a@example.com")
        response = self.client.get(reverse("student-detail", kwargs={"student_id": student.id}))
        self.assertEqual(response.status_code, 302)

    def test_health_stays_public(self):
        # monitoring must work without a login
        self.assertEqual(self.client.get(reverse("health-check")).status_code, 200)

    def test_login_next_parameter_survives(self):
        response = self.client.get("/accounts/login/", {"next": "/api/students/secure-data/"})
        self.assertContains(response, 'value="/api/students/secure-data/"')


class PermissionTests(TestCase):
    """Authorization: what may you do?"""

    def test_user_without_permission_gets_403(self):
        self.client.force_login(make_user())
        response = self.client.get(reverse("student-records"))
        self.assertEqual(response.status_code, 403)            # raise_exception=True -> 403, no redirect

    def test_anonymous_also_gets_403_on_permission_view(self):
        # raise_exception=True turns even the anonymous case into 403 (not a redirect)
        self.assertEqual(self.client.get(reverse("student-records")).status_code, 403)

    def test_user_with_permission_sees_records(self):
        Student.objects.create(name="Aarav", email="a@example.com")
        user = give_permission(make_user())
        self.client.force_login(user)
        response = self.client.get(reverse("student-records"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["records"][0]["name"], "Aarav")

    def test_permission_through_group(self):
        from django.contrib.auth.models import Group
        group = Group.objects.create(name="Registrar")
        group.permissions.add(Permission.objects.get(codename="view_student"))
        user = make_user()
        user.groups.add(group)
        self.client.force_login(User.objects.get(pk=user.pk))
        self.assertEqual(self.client.get(reverse("student-records")).status_code, 200)

    def test_wrong_permission_does_not_help(self):
        # holding 'add_student' must not grant 'view_student'
        user = give_permission(make_user(), "add_student")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("student-records")).status_code, 403)

    def test_superuser_has_every_permission(self):
        self.client.force_login(User.objects.create_superuser("root", password=PASSWORD))
        self.assertEqual(self.client.get(reverse("student-records")).status_code, 200)


class StaffTests(TestCase):
    def test_anonymous_redirected_to_admin_login(self):
        response = self.client.get(reverse("staff-data"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_non_staff_user_is_redirected(self):
        self.client.force_login(make_user())
        self.assertEqual(self.client.get(reverse("staff-data")).status_code, 302)

    def test_staff_user_gets_access(self):
        self.client.force_login(make_user("staff", is_staff=True))
        response = self.client.get(reverse("staff-data"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Staff access granted.")

    def test_staff_flag_is_not_a_model_permission(self):
        # is_staff opens the staff view, but does NOT grant students.view_student
        self.client.force_login(make_user("staff", is_staff=True))
        self.assertEqual(self.client.get(reverse("student-records")).status_code, 403)


class LoginFormTests(TestCase):
    def setUp(self):
        make_user()

    def test_login_page_renders_with_csrf_token(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_login_establishes_session(self):
        response = self.client.post(reverse("login"), {"username": "regular", "password": PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/api/students/secure-data/")     # LOGIN_REDIRECT_URL
        self.assertIn("sessionid", response.cookies)
        # the session now authenticates later requests
        self.assertEqual(self.client.get(reverse("secure-data")).status_code, 200)

    def test_valid_login_honours_next(self):
        response = self.client.post(
            reverse("login") + "?next=/api/students/",
            {"username": "regular", "password": PASSWORD},
        )
        self.assertEqual(response.url, "/api/students/")

    def test_invalid_login_is_rejected(self):
        response = self.client.post(reverse("login"), {"username": "regular", "password": "wrong"})
        self.assertEqual(response.status_code, 200)                      # form shown again
        self.assertNotIn("sessionid", response.cookies)
        self.assertContains(response, "Please enter a correct username and password")
        self.assertEqual(self.client.get(reverse("secure-data")).status_code, 302)

    def test_unknown_user_gets_same_message(self):
        # the page must not reveal whether the username exists
        known = self.client.post(reverse("login"), {"username": "regular", "password": "wrong"})
        unknown = self.client.post(reverse("login"), {"username": "nobody", "password": "wrong"})
        self.assertContains(unknown, "Please enter a correct username and password")
        self.assertEqual(known.status_code, unknown.status_code)

    def test_login_post_without_csrf_token_is_forbidden(self):
        strict = Client(enforce_csrf_checks=True)       # the normal test client skips CSRF checks
        response = strict.post(reverse("login"), {"username": "regular", "password": PASSWORD})
        self.assertEqual(response.status_code, 403)

    def test_logout_ends_session(self):
        self.client.force_login(User.objects.get(username="regular"))
        self.assertEqual(self.client.get(reverse("secure-data")).status_code, 200)
        self.client.post(reverse("logout"))                              # logout requires POST in Django 5+
        self.assertEqual(self.client.get(reverse("secure-data")).status_code, 302)

    def test_passwords_are_stored_hashed(self):
        stored = User.objects.get(username="regular").password
        self.assertNotEqual(stored, PASSWORD)
        self.assertTrue(stored.startswith(("pbkdf2_", "argon2", "bcrypt", "scrypt")))


class SetupRolesCommandTests(TestCase):
    def test_command_creates_registrar_group_with_permission(self):
        from django.core.management import call_command
        call_command("setup_roles", verbosity=0)
        call_command("setup_roles", verbosity=0)                         # idempotent
        from django.contrib.auth.models import Group
        group = Group.objects.get(name="Registrar")
        self.assertEqual(list(group.permissions.values_list("codename", flat=True)), ["view_student"])
