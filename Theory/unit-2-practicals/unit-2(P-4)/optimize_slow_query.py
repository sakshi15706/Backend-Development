"""Step 5: optimise the slow query and explain the changes.

    python optimize_slow_query.py        (run seed.py first)
"""
from common import connect, plan, timed

db = connect()
db.execute("DROP INDEX IF EXISTS idx_students_branch")
db.execute("DROP INDEX IF EXISTS idx_students_branch_date")

SLOW = """
SELECT * FROM students
WHERE UPPER(branch) = 'CSE'
AND name LIKE '%ar%'
ORDER BY enrollment_date
"""

# Optimised version
#  1. branch compared directly (no function on the column) so an index can be used.
#  2. only the columns the API needs instead of SELECT *.
#  3. composite index (branch, enrollment_date): rows come out already sorted, no extra sort step.
#  4. LIMIT, because nobody needs 6000 rows at once (pagination).
FAST = """
SELECT id, name, email, enrollment_date FROM students
WHERE branch = 'CSE'
AND name LIKE '%ar%'
ORDER BY enrollment_date
LIMIT 50
"""

t_slow, n_slow = timed(db, SLOW)
print(f"SLOW  : {t_slow*1000:8.2f} ms  rows={n_slow}")
print("  plan:", *plan(db, SLOW), sep="\n    ")

db.execute("CREATE INDEX idx_students_branch_date ON students(branch, enrollment_date)")
db.execute("ANALYZE")

t_fast, n_fast = timed(db, FAST)
print(f"\nFAST  : {t_fast*1000:8.2f} ms  rows={n_fast}")
print("  plan:", *plan(db, FAST), sep="\n    ")
print(f"\nSpeed-up: {t_slow / t_fast:.1f}x")

print("""
Why the original query is slow
  1. UPPER(branch) = 'CSE'   wraps the column in a function, so the planner cannot use an index
                             on branch (the query is not "sargable"). Fix: compare the raw column, and store
                             branch in one canonical case (a CHECK constraint or ENUM guarantees this).
                             If you really must search case-insensitively, create a functional index:
                             CREATE INDEX idx ON students (UPPER(branch));   -- PostgreSQL / MySQL 8
  2. name LIKE '%ar%'        a leading wildcard can never use a B-tree index. It is acceptable here only
                             because the index on branch has already cut the candidate rows. For real
                             "contains" search use full-text search (PostgreSQL pg_trgm / tsvector,
                             MySQL FULLTEXT) or search by prefix ('ar%').
  3. ORDER BY enrollment_date with no usable index forces the database to sort everything (see
                             'USE TEMP B-TREE FOR ORDER BY' in the slow plan).
                             The composite index (branch, enrollment_date) returns rows pre-sorted.
  4. SELECT *                reads and transfers columns that are never used.
  5. no LIMIT                returns every match; add LIMIT/OFFSET (or keyset pagination).
""")
