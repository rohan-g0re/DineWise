"""
Authentication routes for testing Firebase integration.
"""
from fastapi import APIRouter, Depends
from app.models import User
from app.auth.deps import get_current_user

# Create router with prefix and tags
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Test route to verify Firebase authentication is working.
    
    This route:
    1. Requires a valid Firebase token
    2. Returns current user information
    3. Proves our auth system works
    
    Usage:
    GET /auth/me
    Headers: Authorization: Bearer <firebase_token>
    
    Response:
    {
        "user_id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "firebase_uid": "abc123",
        "created_at": "2024-01-01T00:00:00"
    }
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "firebase_uid": current_user.firebase_uid,
        "created_at": current_user.created_at
    }

@router.get("/test")
async def test_auth_system():
    """
    Public test route to verify the auth system is set up.
    
    This route:
    1. Does NOT require authentication
    2. Returns system status
    3. Helps debug auth setup
    
    Usage:
    GET /auth/test
    """
    return {
        "message": "Authentication system is running",
        "status": "ok",
        "endpoints": {
            "protected": "/auth/me (requires Authorization header)",
            "public": "/auth/test (no auth required)"
        }
    }