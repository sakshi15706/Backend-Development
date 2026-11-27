from django.apps import AppConfig


class StudentsConfig(AppConfig):
    name = "students"

    def ready(self):
        from . import signals  # noqa: F401  (registers the cache-invalidation receivers)
