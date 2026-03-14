import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/database_nlt",
)

SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() in ("1", "true")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=SQL_ECHO,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for FastAPI: yields a DB session and closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create tables from entities. Call once at app startup."""
    from src.inventory.entity import InventoryItemEntity

    Base.metadata.create_all(bind=engine)
