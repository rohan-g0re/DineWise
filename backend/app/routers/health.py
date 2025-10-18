from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Create router instance
router = APIRouter(
    prefix="/health",  # All routes in this router will start with /health
    tags=["health"],   # Group these routes in the API docs
    responses={404: {"description": "Not found"}}
)

@router.get("/")
def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict[str, str]: Status of the API
    """
    return {"status": "ok"}

@router.get("/detailed")
def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    
    Returns:
        Dict[str, Any]: Detailed status information
    """
    return {
        "status": "ok",
        "service": "DineWise API",
        "version": "1.0.0",
        "uptime": "running"
    }

@router.get("/ping")
def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for load balancers.
    
    Returns:
        Dict[str, str]: Simple pong response
    """
    return {"message": "pong"}