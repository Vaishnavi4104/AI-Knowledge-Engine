"""
Database configuration and connection management
"""

import logging
from typing import Generator

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Database URL - can be overridden with environment variable
# Set to None to disable database (use in-memory only)
DATABASE_URL = settings.database_url

# Initialize engine and session as None
engine = None
SessionLocal = None
DB_AVAILABLE = False

# Try to create database connection if DATABASE_URL is provided
if DATABASE_URL:
    try:
        connect_args = {"connect_timeout": 5} if DATABASE_URL.startswith("postgresql") else {}

        # Create SQLAlchemy engine
        engine = create_engine(
            DATABASE_URL,
            echo=settings.debug,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args=connect_args,
        )

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Create SessionLocal class
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        logger.info("Database connection established successfully")

    except Exception as exc:  # pragma: no cover - startup logging
        logger.warning("Database connection failed: %s", exc)
        logger.info("Continuing without database - data will not be persisted")
        engine = None
        SessionLocal = None
        DB_AVAILABLE = False
else:
    logger.info("DATABASE_URL not set - running without database (in-memory only)")

# Create Base class for models
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()


def get_db() -> Generator:
    """Dependency that yields a database session or None if unavailable."""

    if not DB_AVAILABLE or SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    except OperationalError as exc:  # pragma: no cover - runtime safety
        logger.error("Database operation failed: %s", exc)
        db.rollback()
        yield None
    finally:
        if db:
            db.close()


def create_tables():
    """Create all tables defined in the models."""

    if not DB_AVAILABLE or engine is None:
        logger.warning("Database not available - cannot create tables")
        return

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as exc:  # pragma: no cover - startup logging
        logger.error("Failed to create tables: %s", exc)


def drop_tables():
    """Drop all tables (use with caution)."""

    if not DB_AVAILABLE or engine is None:
        logger.warning("Database not available - cannot drop tables")
        return

    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as exc:  # pragma: no cover - startup logging
        logger.error("Failed to drop tables: %s", exc)
