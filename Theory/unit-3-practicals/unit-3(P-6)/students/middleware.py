"""Task 1: request logging middleware (Lecture 27)."""
import logging
import time

logger = logging.getLogger(__name__)


class SimpleLoggingMiddleware:
    def __init__(self, get_response):
        # Django passes the next middleware (or the view handler) when it builds the chain.
        self.get_response = get_response

    def __call__(self, request):
        # ---- request phase: runs BEFORE the view ----
        start_time = time.perf_counter()
        logger.info("Request: %s %s", request.method, request.get_full_path())

        # pass control to the next middleware / the view
        response = self.get_response(request)

        # ---- response phase: runs AFTER the view returns ----
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Response: %s in %.2f ms",
            response.status_code,
            duration_ms,
        )
        return response
