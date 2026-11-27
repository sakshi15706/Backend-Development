"""Cache keys and timeouts in one place (no magic strings in the views)."""
from django.conf import settings

SUMMARY_KEY = "student-summary"


def summary_timeout():
    return settings.SUMMARY_CACHE_TIMEOUT
