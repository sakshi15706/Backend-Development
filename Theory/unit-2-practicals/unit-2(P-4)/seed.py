"""Step 1: create a students table with 100,000 sample records.

    python seed.py            (about 1 second)
"""
import random
from datetime import date, timedelta

from common import DB_PATH, connect

N = 100_000
random.seed(42)

BRANCHES = ["CSE", "ECE", "IT", "ME", "CE", "EEE", "CHEM", "BIO", "AI", "DS"]
WEIGHTS = [30, 20, 20, 15, 10, 3, 1, 0.5, 0.3, 0.2]       # skewed: some branches are rare
FIRST = ["Aarav", "Diya", "Rohan", "Priya", "Vikram", "Neha", "Karan", "Sara", "Arjun", "Meera",
         "Ishaan", "Tara", "Kabir", "Anaya", "Yash", "Zoya"]
LAST = ["Sharma", "Verma", "Singh", "Gupta", "Nair", "Rao", "Khan", "Das", "Mehta", "Bose"]

DB_PATH.unlink(missing_ok=True)
db = connect()
db.execute("""
    CREATE TABLE students (
        id              INTEGER PRIMARY KEY,
        name            TEXT NOT NULL,
        email           TEXT NOT NULL UNIQUE,
        branch          TEXT NOT NULL,
        enrollment_date DATE NOT NULL
    )""")

start = date(2020, 8, 1)
rows = (
    (
        i,
        f"{random.choice(FIRST)} {random.choice(LAST)}",
        f"user{i}@upes.ac.in",
        random.choices(BRANCHES, WEIGHTS)[0],
        (start + timedelta(days=random.randint(0, 2000))).isoformat(),
    )
    for i in range(1, N + 1)
)
db.executemany("INSERT INTO students VALUES (?,?,?,?,?)", rows)
db.commit()

print(f"Inserted {db.execute('SELECT COUNT(*) FROM students').fetchone()[0]:,} rows into {DB_PATH.name}")
for branch, n in db.execute("SELECT branch, COUNT(*) FROM students GROUP BY branch ORDER BY 2 DESC"):
    print(f"  {branch:<5} {n:>6}")
