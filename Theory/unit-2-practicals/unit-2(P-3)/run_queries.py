"""Creates a small SQLite database, loads sample data and runs the three SQL queries.

    python run_queries.py
"""
import sqlite3
from pathlib import Path

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, branch TEXT, enrollment_date DATE);
CREATE TABLE courses (id INTEGER PRIMARY KEY, code TEXT);
CREATE TABLE enrollments (student_id INT, course_id INT, PRIMARY KEY (student_id, course_id));
INSERT INTO students VALUES
 (1,'Aarav','CSE','2024-07-15'), (2,'Diya','ECE','2024-09-02'), (3,'Rohan','IT','2024-08-31'),
 (4,'Priya','CSE','2024-10-01'), (5,'Vikram','ME','2025-01-10');
INSERT INTO courses VALUES (1,'CS301'),(2,'CS302'),(3,'CS303'),(4,'CS304'),(5,'CS305');
-- Aarav: 4 courses, Diya: 3 courses, Priya: 5 courses
INSERT INTO enrollments VALUES (1,1),(1,2),(1,3),(1,4),(2,1),(2,2),(2,3),(4,1),(4,2),(4,3),(4,4),(4,5);
""")

queries = Path(__file__).with_name("sql_queries.sql").read_text().split(";")
for q in (q.strip() for q in queries):
    if not q:
        continue
    title = next(l for l in q.splitlines() if l.startswith("-- ") and l[3].isdigit())
    cur = db.execute(q)
    print(f"\n{title}")
    print(" | ".join(c[0] for c in cur.description))
    for row in cur.fetchall():
        print(" | ".join(map(str, row)))
