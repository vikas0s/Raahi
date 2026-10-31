"""
Database connection, session management, and lifecycle for Raahi Transit Platform.
Supports PostgreSQL (with connection pooling) and fallback SQLite for local development.
"""
import os
import time
import logging
import sqlite3
from pathlib import Path
from typing import Generator, Dict, Any, Optional
from dotenv import load_dotenv

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine

# Load root .env
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=root_env)

logger = logging.getLogger("raahi.database")

Base = declarative_base()

# Read DATABASE_URL from environment
RAW_DB_URL = os.getenv("DATABASE_URL", "").strip()

# Default SQLite database path
DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent.parent / "raahi_transit.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

# Resolve connection URL
if not RAW_DB_URL:
    DATABASE_URL = DEFAULT_SQLITE_URL
    IS_POSTGRES = False
else:
    # Handle Heroku/Supabase postgres:// scheme
    if RAW_DB_URL.startswith("postgres://"):
        DATABASE_URL = RAW_DB_URL.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = RAW_DB_URL
    IS_POSTGRES = "postgresql" in DATABASE_URL.lower()

# Configure engine with robust pooling
if IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 5}
    )
else:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )

    # Enable foreign keys for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Dict[str, Any]:
    """
    Checks database connectivity and latency without exposing credentials.
    Returns status, dialect, latency_ms, and active status.
    """
    start_time = time.perf_counter()
    dialect_name = engine.dialect.name
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "status": "connected",
            "dialect": dialect_name,
            "latency_ms": latency_ms,
            "pooling": "active" if IS_POSTGRES else "standard",
            "is_postgres": IS_POSTGRES
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "disconnected",
            "dialect": dialect_name,
            "error": "Connection failed",
            "is_postgres": IS_POSTGRES
        }


def init_db():
    """Create all database tables idempotently and migrate existing schemas."""
    try:
        from . import models  # Ensure all models are imported before create_all
        Base.metadata.create_all(bind=engine)
        
        # Check and migrate legacy saved_routes table if needed
        with engine.begin() as conn:
            try:
                result = conn.execute(text("PRAGMA table_info(saved_routes)"))
                cols = {row[1] for row in result.fetchall()}
                if cols and "user_id" not in cols:
                    conn.execute(text("ALTER TABLE saved_routes ADD COLUMN user_id TEXT"))
                if cols and "preferences_json" not in cols:
                    conn.execute(text("ALTER TABLE saved_routes ADD COLUMN preferences_json TEXT"))
            except Exception:
                pass  # On PostgreSQL, table_info is different; Base.metadata.create_all already creates proper schema

        logger.info(f"Database tables initialized successfully ({engine.dialect.name}).")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise e
