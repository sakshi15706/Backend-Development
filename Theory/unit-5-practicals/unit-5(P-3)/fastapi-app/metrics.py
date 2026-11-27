"""Latency recorder for FastAPI (Lecture 58, section 4). Same rules as the Express version."""
import math
import threading
import time
from collections import deque


def percentile(sorted_values, p):
    """Nearest-rank percentile (index = ceil(p * n) - 1); the slide's int(n * p) returns the maximum for p99 at n = 100."""
    if not sorted_values:
        return 0.0
    rank = min(max(math.ceil(p * len(sorted_values)), 1), len(sorted_values))
    return sorted_values[rank - 1]


class Recorder:
    def __init__(self, window_size=1000, ignore_paths=("/metrics", "/metrics/reset")):
        self.window_size = window_size
        self.ignore_paths = set(ignore_paths)
        self._lock = threading.Lock()          # sync endpoints run in a thread pool, so guard shared state
        self.reset()

    def reset(self):
        with getattr(self, "_lock", threading.Lock()):
            self.samples = deque(maxlen=self.window_size)    # bounded: oldest dropped automatically
            self.total = 0
            self.errors = 0
            self.started = time.perf_counter()

    def record(self, path, ms, status):
        with self._lock:
            self.samples.append((path, ms))
            self.total += 1
            if status >= 500:
                self.errors += 1

    def snapshot(self, path=None):
        with self._lock:
            values = sorted(ms for p, ms in self.samples if path is None or p == path)
            total, errors = self.total, self.errors
            seconds = time.perf_counter() - self.started
        r = lambda x: round(x, 3)
        return {
            "count": len(values),
            "p50": r(percentile(values, 0.50)),
            "p95": r(percentile(values, 0.95)),
            "p99": r(percentile(values, 0.99)),
            "max": r(values[-1] if values else 0.0),
            "mean": r(sum(values) / len(values) if values else 0.0),
            "totalRequests": total,
            "errors": errors,
            "errorRate": r(errors / total * 100) if total else 0.0,
            "requestsPerSecond": r(total / seconds) if seconds > 0 else 0.0,
            "window": self.window_size,
        }
