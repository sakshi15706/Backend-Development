from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {},
    pool_pre_ping=True,                                 # drop dead connections (important on cloud databases)
)


@event.listens_for(engine, "connect")
def _sqlite_foreign_keys(dbapi_connection, _):
    if settings.is_sqlite:
        dbapi_connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
