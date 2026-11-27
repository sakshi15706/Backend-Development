# Unit 2 (P-4): Query Optimization (Lecture 17)

## Lab exercise
1. Create a `students` table with 100,000 sample records using a script.
2. Run a query without an index and measure the execution time.
3. Create an index on the `branch` column and re-run the same query.
4. Use `EXPLAIN` to compare the execution plans before and after indexing.
5. Optimise the slow query (`UPPER(branch) = 'CSE' AND name LIKE '%ar%' ORDER BY enrollment_date`) and explain the changes.
6. Implement connection pooling in a FastAPI application using SQLAlchemy.
7. Benchmark API response times before and after optimisation.

## Run
```bash
cd "unit-2(P-4)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt

python seed.py                  # step 1
python benchmark_index.py       # steps 2, 3, 4
python optimize_slow_query.py   # step 5 (explanation is printed at the end)
python benchmark_api.py         # step 7
uvicorn app:app --reload        # step 6, Swagger UI at /docs
```
The database is SQLite (`bench.db`, created by `seed.py`, about 6 MB). For PostgreSQL / MySQL the SQL is the same; use `EXPLAIN ANALYZE` instead of `EXPLAIN QUERY PLAN`.

## Files
| File | Step |
|---|---|
| `seed.py` | 1: 100,000 rows with realistic skew (rare and common branches) |
| `benchmark_index.py` | 2, 3, 4: timing and plans before/after the index |
| `optimize_slow_query.py` | 5: slow vs optimised query, with the reasons |
| `app.py` | 6: `NullPool` engine (before) vs pooled engine (after) |
| `benchmark_api.py` | 7: API timings before/after |
| `common.py` | timing and EXPLAIN helpers |

## Record your own numbers
Timings depend on your machine, so paste the output of the scripts into your lab report. Typical findings:
- An index on a selective column (CHEM, ~1% of rows) turns `SCAN students` into `SEARCH ... USING INDEX` and is faster (about 2 to 3x on 100,000 rows; the gap grows with table size).
- An index on a filter that matches a big share of the table (CSE, ~30%) gives no gain and can even be slightly slower, because the database still has to read a large part of the table.
- The biggest win comes from fixing the query itself (step 5): removing `UPPER()`, adding a composite index and a `LIMIT`.
- `UPPER(col) = ...`, a leading-wildcard `LIKE '%x'`, and `SELECT *` without `LIMIT` are classic slow-query causes.

## Connection pool settings (app.py)
| Setting | Meaning |
|---|---|
| `pool_size` | connections kept open and reused |
| `max_overflow` | extra temporary connections under load |
| `pool_timeout` | seconds to wait for a free connection |
| `pool_recycle` | close connections older than this, avoids stale ones |
| `pool_pre_ping` | check a connection is alive before using it |
