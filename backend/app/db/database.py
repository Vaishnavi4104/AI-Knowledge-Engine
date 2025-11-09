"""
Database configuration and connection management
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)

# Database URL - can be overridden with environment variable
# Set to None to disable database (use in-memory only)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    None  # Default to None - database is optional
)

# Initialize engine and session as None
engine = None
SessionLocal = None
DB_AVAILABLE = False

# Try to create database connection if DATABASE_URL is provided
if DATABASE_URL:
    try:
        # Create SQLAlchemy engine
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            connect_args={"connect_timeout": 5}  # 5 second timeout
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create SessionLocal class
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.warning(f"Database connection failed: {str(e)}")
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
    """
    Dependency to get database session.
    Returns None if database is not available.
    Yields a database session and ensures it's closed after use.
    
    Usage:
        @app.get("/endpoint")
        def some_endpoint(db: Session = Depends(get_db)):
            if db is None:
                # Database not available, skip DB operations
                pass
            else:
                # Use db session here
                pass
    """
    if not DB_AVAILABLE or SessionLocal is None:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database operation failed: {str(e)}")
        db.rollback()
        yield None
    finally:
        if db:
            db.close()


def create_tables():
    """
    Create all tables defined in the models.
    Call this function to initialize the database schema.
    """
    if not DB_AVAILABLE or engine is None:
        logger.warning("Database not available - cannot create tables")
        return
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")


def drop_tables():
    """
    Drop all tables.
    Use with caution - this will delete all data!
    """
    if not DB_AVAILABLE or engine is None:
        logger.warning("Database not available - cannot drop tables")
        return
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
