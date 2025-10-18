"""
Database connection and session management.
Creates the connection to Supabase PostgreSQL database.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Test connections before use
    echo=settings.debug   # Show SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # Don't auto-commit (we control transactions)
    autoflush=False    # Don't auto-flush (we control when to save)
)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Dependency to get database session.
    This is used by FastAPI to provide database access to endpoints.
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to the endpoint
    finally:
        db.close()  # Always close the session when done