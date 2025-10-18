# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import health

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DineWise API - Restaurant search and review platform",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # ["http://localhost:5173", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(health.router)

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API information."""
    return {
        "message": "Welcome to DineWise API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health/"
    }