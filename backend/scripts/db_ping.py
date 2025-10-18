#!/usr/bin/env python3
"""
Database connection test script.
Tests if we can connect to the Supabase database.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path so we can import from app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def ping_db():
    """Test database connection by running a simple SELECT query."""
    try:
        # Load environment variables from .env file
        load_dotenv(backend_dir / ".env")
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            print("Make sure you have a .env file with DATABASE_URL set")
            return False
        
        print(f"🔗 Connecting to database...")
        print(f"📍 URL: {database_url[:50]}...")  # Show first 50 chars for debugging
        
        # Create engine and test connection
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test_value, NOW() as current_time"))
            row = result.fetchone()
            
            print("✅ Database connection successful!")
            print(f"📊 Test query result: {row[0]}")
            print(f"⏰ Database time: {row[1]}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 Testing database connection...")
    print("=" * 50)
    
    success = ping_db()
    
    print("=" * 50)
    if success:
        print("🎉 Database ping completed successfully!")
        sys.exit(0)
    else:
        print("💥 Database ping failed!")
        sys.exit(1)