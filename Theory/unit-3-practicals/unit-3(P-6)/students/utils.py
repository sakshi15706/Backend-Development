"""Service utility for the third-party API (Lecture 28, Task 2).

All HTTP-client code lives here, not in the view, so it is easy to test with a mock.
The function never raises: it always returns {"data": ..., "error": ...}.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_external_data(post_id):
    url = settings.EXTERNAL_API_URL.format(post_id=post_id)
    try:
        # timeout: never wait forever for a slow dependency
        response = requests.get(url, timeout=settings.EXTERNAL_API_TIMEOUT)
        # raise_for_status turns HTTP 4xx/5xx into an exception
        response.raise_for_status()
        return {"data": response.json(), "error": None}
    except requests.Timeout:
        logger.warning("External API timed out: %s", url)
        return {"data": None, "error": "External service timed out"}
    except requests.exceptions.JSONDecodeError:
        # Must come BEFORE RequestException: in requests >= 2.27 this exception is
        # a RequestException too, so the generic handler below would hide it.
        logger.warning("External API returned invalid JSON: %s", url)
        return {"data": None, "error": "External service returned invalid JSON"}
    except requests.RequestException:
        logger.warning("External API unavailable: %s", url)
        return {"data": None, "error": "External service is unavailable"}
    except ValueError:
        # older requests versions raise a plain ValueError from response.json()
        return {"data": None, "error": "External service returned invalid JSON"}
