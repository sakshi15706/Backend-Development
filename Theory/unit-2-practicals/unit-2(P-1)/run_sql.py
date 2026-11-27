"""Runs the three SQL files on SQLite so you can check them without installing MySQL/PostgreSQL.

    python run_sql.py

For MySQL / PostgreSQL run the same files in order (01, 02, 03) from Workbench / psql.
"""
import sqlite3
from pathlib import Path

here = Path(__file__).parent
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")

for name in ("01_library_schema.sql", "02_library_sample_data.sql", "03_normalization.sql"):
    db.executescript((here / name).read_text())
    print(f"ran {name}")


def show(title, sql):
    print(f"\n== {title}")
    cur = db.execute(sql)
    print(" | ".join(c[0] for c in cur.description))
    for row in cur.fetchall():
        print(" | ".join(str(v) for v in row))


show("Books with their authors",
     """SELECT b.title, GROUP_CONCAT(a.name, ', ') AS authors
        FROM books b JOIN book_authors ba ON ba.book_id = b.id
        JOIN authors a ON a.id = ba.author_id GROUP BY b.id ORDER BY b.id""")

show("Books currently borrowed (not returned)",
     """SELECT m.name AS member, b.title, l.due_date
        FROM loans l JOIN members m ON m.id = l.member_id JOIN books b ON b.id = l.book_id
        WHERE l.return_date IS NULL ORDER BY m.name""")

show("3NF tables joined back to the ORIGINAL table",
     """SELECT o.id AS order_id, c.name AS customer_name, c.email AS customer_email,
               p.name AS product_name, p.price AS product_price, oi.quantity
        FROM order_items oi JOIN orders o ON o.id = oi.order_id
        JOIN customers c ON c.id = o.customer_id JOIN products p ON p.id = oi.product_id
        ORDER BY o.id, p.id""")

# constraint checks
for label, stmt in [
    ("duplicate ISBN rejected", "INSERT INTO books (id,title,isbn) VALUES (9,'X','9780132350884')"),
    ("loan for missing book rejected", "INSERT INTO loans VALUES (9,99,1,'2024-01-01','2024-01-10',NULL)"),
    ("due date before loan date rejected", "INSERT INTO loans VALUES (9,1,1,'2024-01-10','2024-01-01',NULL)"),
]:
    try:
        db.execute(stmt)
        print(f"FAIL: {label} was NOT rejected")
    except sqlite3.IntegrityError as e:
        print(f"OK: {label} ({e})")
