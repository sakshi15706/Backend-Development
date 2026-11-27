import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).with_name("bench.db")


def connect():
    return sqlite3.connect(DB_PATH)


def timed(db, sql, params=(), repeat=5):
    """Run the query `repeat` times, return (best_seconds, row_count)."""
    best, rows = None, 0
    for _ in range(repeat):
        start = time.perf_counter()
        rows = len(db.execute(sql, params).fetchall())
        elapsed = time.perf_counter() - start
        best = elapsed if best is None else min(best, elapsed)
    return best, rows


def plan(db, sql, params=()):
    """EXPLAIN QUERY PLAN (SQLite).  PostgreSQL/MySQL: use EXPLAIN / EXPLAIN ANALYZE."""
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]
