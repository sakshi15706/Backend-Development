"""External-API code lives here, NOT in the form class (the form validates, a service talks
to other systems).  It never raises: a failing notification must not break a registration
that is already saved.

In production do not make the user wait for a slow external API; move this call to a
background worker (Celery, Django-Q ...).
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def notify_registration(student):
    """POST a small JSON payload about a new registration. Returns True / False.

    Returns False without calling anything when REGISTRATION_NOTIFY_URL is not configured.
    """
    url = settings.REGISTRATION_NOTIFY_URL
    if not url:
        logger.info("Registration notification skipped (REGISTRATION_NOTIFY_URL not set)")
        return False

    payload = {"student_id": student.id, "name": student.name, "course": student.course}
    try:
        response = requests.post(url, json=payload, timeout=settings.REGISTRATION_NOTIFY_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Could not notify external registration service: student_id=%s", student.id)
        return False
    return True
