"""Step 7: benchmark API response times before and after optimisation.

    python seed.py
    python benchmark_api.py
It creates the composite index for the 'after' run and removes it for the 'before' run.
"""
import statistics
import time

from fastapi.testclient import TestClient

from app import app
from common import connect

REQUESTS = 30
client = TestClient(app)


def set_index(enabled: bool):
    db = connect()
    db.execute("DROP INDEX IF EXISTS idx_students_branch_date")
    if enabled:
        db.execute("CREATE INDEX idx_students_branch_date ON students(branch, enrollment_date)")
        db.execute("ANALYZE")
    db.commit()
    db.close()


def bench(path):
    client.get(path)  # warm-up
    times = []
    for _ in range(REQUESTS):
        start = time.perf_counter()
        r = client.get(path)
        times.append((time.perf_counter() - start) * 1000)
        assert r.status_code == 200
    times.sort()
    return statistics.mean(times), times[int(len(times) * 0.95) - 1], len(r.json())


set_index(False)
before = bench("/students/slow")
set_index(True)
after = bench("/students/fast")

print(f"{REQUESTS} requests each (TestClient, SQLite, 100,000 rows)\n")
print(f"{'':<34}{'avg ms':>9}{'p95 ms':>9}{'rows':>7}")
print(f"{'BEFORE  /students/slow  (no pool)':<34}{before[0]:>9.1f}{before[1]:>9.1f}{before[2]:>7}")
print(f"{'AFTER   /students/fast  (pooled)':<34}{after[0]:>9.1f}{after[1]:>9.1f}{after[2]:>7}")
print(f"\nImprovement: {before[0] / after[0]:.1f}x faster on average")
print("pool status:", client.get("/pool-status").json()["pool"])
print("""
Note: on SQLite the connection is a local file, so most of the gain comes from the query/index change.
Pooling matters far more with PostgreSQL/MySQL, where opening a connection costs a network round trip
and authentication (often 5 to 50 ms). Re-run this exercise against PostgreSQL to see that effect.""")
