"""Step 6: connection pooling in FastAPI + SQLAlchemy.

    python seed.py
    uvicorn app:app --reload        ->  http://127.0.0.1:8000/docs
"""
from fastapi import Depends, FastAPI, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from common import DB_PATH

URL = f"sqlite:///{DB_PATH}"

# BEFORE: no pooling. Every request opens and closes a brand-new database connection.
engine_no_pool = create_engine(URL, poolclass=NullPool)

# AFTER: a pool of reusable connections kept open between requests.
engine_pooled = create_engine(
    URL,
    pool_size=10,        # connections kept open
    max_overflow=20,     # extra connections allowed under burst load
    pool_timeout=30,     # seconds to wait for a free connection before erroring
    pool_recycle=1800,   # replace connections older than 30 min (avoids stale connections)
    pool_pre_ping=True,  # test a connection before using it
)

SessionNoPool = sessionmaker(bind=engine_no_pool)
SessionPooled = sessionmaker(bind=engine_pooled)


def db_no_pool():
    with SessionNoPool() as session:
        yield session


def db_pooled():
    with SessionPooled() as session:
        yield session


app = FastAPI(title="Query optimisation and connection pooling")

# The unoptimised query from the lab exercise
SLOW_SQL = text("""
    SELECT * FROM students
    WHERE UPPER(branch) = 'CSE' AND name LIKE '%ar%'
    ORDER BY enrollment_date
""")

FAST_SQL = text("""
    SELECT id, name, email, enrollment_date FROM students
    WHERE branch = 'CSE' AND name LIKE '%ar%'
    ORDER BY enrollment_date
    LIMIT :limit
""")


@app.get("/students/slow", tags=["before"])
def students_slow(limit: int = Query(50, ge=1, le=500), db: Session = Depends(db_no_pool)):
    """Unoptimised query, no pooling. (Rows are cut in Python so the payload matches /fast.)"""
    rows = db.execute(SLOW_SQL).mappings().all()[:limit]
    return [dict(r) for r in rows]


@app.get("/students/fast", tags=["after"])
def students_fast(limit: int = Query(50, ge=1, le=500), db: Session = Depends(db_pooled)):
    """Optimised query plus pooled connections."""
    rows = db.execute(FAST_SQL, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]


@app.get("/pool-status", tags=["after"])
def pool_status():
    return {"pool": engine_pooled.pool.status()}
