import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

IS_SQLITE = DATABASE_URL.startswith("sqlite")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if IS_SQLITE else {})


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_connection, _):
    if IS_SQLITE:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
