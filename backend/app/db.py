"""
Database connection and session management.
Creates the connection to Supabase PostgreSQL database.
"""
from sqlmodel import create_engine, Session
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Test connections before use
    echo=settings.debug   # Show SQL queries in debug mode
)

def get_db():
    """
    Dependency to get database session.
    This is used by FastAPI to provide database access to endpoints.
    Uses SQLModel Session which has the .exec() method.
    """
    with Session(engine) as session:
        yield session