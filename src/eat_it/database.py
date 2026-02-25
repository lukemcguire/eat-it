"""Database engine and session management with WAL mode."""

from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from eat_it.config import get_settings

_engine = None


def _get_database_path() -> Path:
    """Extract database path from database URL."""
    settings = get_settings()
    # Parse sqlite:///./data/eat-it.db -> ./data/eat-it.db
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return Path(url[10:])
    return Path("./data/eat-it.db")


def _set_pragma(dbapi_connection, connection_record) -> None:  # noqa: ARG001
    """Set SQLite PRAGMA settings and load sqlite-vec extension."""
    # Load sqlite-vec extension for vector search support
    dbapi_connection.enable_load_extension(True)
    import sqlite_vec

    sqlite_vec.load(dbapi_connection)

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA wal_autocheckpoint=1000")
    cursor.close()


def get_engine():
    """Get or create the database engine with WAL mode configuration."""
    global _engine  # noqa: PLW0603
    if _engine is not None:
        return _engine

    settings = get_settings()

    # Ensure data directory exists before connecting
    db_path = _get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(settings.database_url)

    # Register event listener for PRAGMA configuration
    # Note: We need to access the raw connection for PRAGMA settings
    from sqlalchemy import event

    event.listen(_engine, "connect", _set_pragma)

    return _engine


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize database, creating data directory and tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


# Module-level engine for convenience
engine = get_engine()
