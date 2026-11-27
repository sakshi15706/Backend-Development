"""Sliding-window rate limiter (in memory).

Allows `max_calls` per `window` seconds for each key (here: client IP).
In memory means it works for ONE server process. With several workers/servers use Redis
(for example the `slowapi` or `fastapi-limiter` packages) so that all of them share the counters.
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, Response


class RateLimiter:
    def __init__(self, max_calls: int, window: float, clock=time.monotonic):
        self.max_calls = max_calls
        self.window = window
        self.clock = clock                       # injectable so tests need not wait a real minute
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str):
        """Returns (allowed, remaining, retry_after_seconds)."""
        now = self.clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:     # forget attempts older than the window
                hits.popleft()
            if len(hits) >= self.max_calls:
                return False, 0, max(1, int(self.window - (now - hits[0])) + 1)
            hits.append(now)
            if not hits:
                self._hits.pop(key, None)
            return True, self.max_calls - len(hits), 0

    def reset(self):
        with self._lock:
            self._hits.clear()


login_limiter = RateLimiter(max_calls=5, window=60)


def login_rate_limit(request: Request, response: Response):
    """FastAPI dependency: 5 login attempts per minute per IP address."""
    key = request.client.host if request.client else "unknown"
    allowed, remaining, retry_after = login_limiter.check(key)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after), "X-RateLimit-Limit": str(login_limiter.max_calls),
                     "X-RateLimit-Remaining": "0"},
        )
    response.headers["X-RateLimit-Limit"] = str(login_limiter.max_calls)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
