"""
Application configuration management.
Loads and validates environment variables using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    
    # API Keys
    yelp_api_key: str
    firebase_project_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    
    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    
    # CORS Origins (allowed frontend URLs)
    cors_origins: List[str] = [
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000"
    ]
    
    # Security
    jwt_audience: Optional[str] = None
    jwt_issuer: Optional[str] = None
    
    # App Info
    app_name: str = "DineWise API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allows both DATABASE_URL and database_url
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Ensure database URL is properly formatted."""
        if not v:
            raise ValueError("DATABASE_URL is required")
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string")
        return v
    
    @validator("yelp_api_key")
    def validate_yelp_api_key(cls, v):
        """Ensure Yelp API key is present."""
        if not v:
            raise ValueError("YELP_API_KEY is required")
        return v


# Create a single instance of settings
settings = Settings()


# Helper function to get settings (useful for dependency injection)
def get_settings() -> Settings:
    """Get application settings."""
    return settings