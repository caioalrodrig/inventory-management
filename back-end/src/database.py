import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/database_nlt",
)

SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in ("1", "true")


DB_CONNECT_MAX_RETRIES = int(os.getenv("DB_CONNECT_MAX_RETRIES", "30"))
DB_CONNECT_RETRY_INTERVAL = float(os.getenv("DB_CONNECT_RETRY_INTERVAL", "1.0"))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=SQL_ECHO,
)


def wait_for_db() -> None:
    """Wait for Postgres to accept connections (retry on startup)."""
    last_err = None
    for attempt in range(1, DB_CONNECT_MAX_RETRIES + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            last_err = e
            if attempt < DB_CONNECT_MAX_RETRIES:
                time.sleep(DB_CONNECT_RETRY_INTERVAL)
    raise RuntimeError(
        f"Could not connect to database after {DB_CONNECT_MAX_RETRIES} attempts. Last error: {last_err}"
    ) from last_err


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Session for read-only operations. No commit; use for queries only."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_tx():
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as conn:
        with SessionLocal(bind=conn) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise


def create_tables() -> None:
    from src.inventory.entity import InventoryItemEntity

    Base.metadata.create_all(bind=engine)
