"""Steps 2 to 4: measure a query without an index, add an index on branch, re-run, compare plans.

    python benchmark_index.py
"""
from common import connect, plan, timed

db = connect()
db.execute("DROP INDEX IF EXISTS idx_students_branch")

QUERY = "SELECT * FROM students WHERE branch = ?"
print("Query:", QUERY, "\n")

results = {}
for branch in ("CHEM", "CSE"):          # CHEM ~1% of rows (selective), CSE ~30% (not selective)
    t, n = timed(db, QUERY, (branch,))
    results[branch] = {"before": t, "rows": n, "plan_before": plan(db, QUERY, (branch,))}

db.execute("CREATE INDEX idx_students_branch ON students(branch)")
db.execute("ANALYZE")

for branch in results:
    t, n = timed(db, QUERY, (branch,))
    results[branch]["after"] = t
    results[branch]["plan_after"] = plan(db, QUERY, (branch,))

print(f"{'branch':<8}{'rows':>8}{'no index':>14}{'with index':>14}{'speed-up':>11}")
for branch, r in results.items():
    print(f"{branch:<8}{r['rows']:>8}{r['before']*1000:>11.2f} ms{r['after']*1000:>11.2f} ms{r['before']/r['after']:>10.1f}x")

r = results["CHEM"]
print("\nEXPLAIN QUERY PLAN before the index:", *r["plan_before"], sep="\n  ")
print("EXPLAIN QUERY PLAN after the index:", *r["plan_after"], sep="\n  ")

print("""
Reading the result
  - 'SCAN students'                  = full table scan, every row is read.
  - 'SEARCH students USING INDEX ..' = the index jumps straight to the matching rows.
  - The more selective the filter (CHEM 1% vs CSE 30%) the bigger the gain; when a query
    returns a large share of the table an index helps much less.
PostgreSQL / MySQL equivalent:  EXPLAIN ANALYZE SELECT * FROM students WHERE branch = 'CHEM';
(look for  Seq Scan -> Index Scan  and the drop in execution time).""")
