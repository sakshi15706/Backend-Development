from django.apps import AppConfig


class FormsConfig(AppConfig):
    name = "forms"
    # NOTE: "forms" is also the name of django.forms. It works (our package is imported as
    # `forms`, Django's as `django.forms`), but in a real project call the app
    # `registrations` or `student_forms` to avoid confusion.
