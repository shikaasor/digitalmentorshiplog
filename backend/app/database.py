from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

from app.config import settings

# check if serverless
IS_SEVERLESS = os.getenv("VERCEL") == "1"

if IS_SEVERLESS:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG)
else:
    # Create SQLAlchemy engine for Supabase PostgreSQL with aggressive connection disposal
    # Using NullPool to destroy connections immediately after use
    # This prevents connection exhaustion on Supabase free tier (15-20 max connections)
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,           # No connection pooling - create and destroy immediately
        pool_pre_ping=True,            # Verify connections before using them
        echo=settings.DEBUG
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get database session
def get_db():
    """
    Database session dependency with aggressive connection cleanup.

    Creates a new database connection for each request and ensures it's
    properly closed and disposed immediately after use. This prevents
    connection exhaustion on Supabase's limited connection pool.

    With NullPool, connections are automatically destroyed when closed.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Rollback on any error
        db.rollback()
        raise
    finally:
        # Close the session - with NullPool, this destroys the connection immediately
        db.close()


# Utility function to check database connection status
def get_pool_status():
    """
    Get current database connection status for monitoring.

    Since we're using NullPool (no connection pooling), this returns
    basic connection health status instead of pool metrics.

    Returns:
        dict: Connection status information
    """
    try:
        # Test database connectivity
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()

        return {
            "pool_type": "NullPool (Immediate Disposal)",
            "status": "connected",
            "pooling": "disabled",
            "note": "Connections are created and destroyed immediately after each request"
        }
    except Exception as e:
        return {
            "pool_type": "NullPool (Immediate Disposal)",
            "status": "error",
            "error": str(e)
        }
