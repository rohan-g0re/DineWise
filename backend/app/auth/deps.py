"""
FastAPI dependencies for authentication.
This module provides dependencies that can be used in route handlers.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.db import get_db
from app.models import User
from app.auth.firebase import firebase_auth

# HTTP Bearer token security scheme
# This tells FastAPI to look for "Authorization: Bearer <token>" headers
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that verifies Firebase token and returns current user.
    
    This function:
    1. Extracts token from Authorization header
    2. Verifies token with Firebase
    3. Creates/updates user in our database
    4. Returns User object
    
    Usage in routes:
    @app.get("/protected-route")
    async def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.email}!"}
    """
    
    # Extract token from "Bearer <token>" header
    token = credentials.credentials
    
    # Verify token with Firebase
    firebase_user = firebase_auth.verify_token(token)
    
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user exists in our database
    statement = select(User).where(User.firebase_uid == firebase_user['uid'])
    user = db.exec(statement).first()
    
    if not user:
        # Create new user if they don't exist
        user = User(
            email=firebase_user['email'],
            full_name=firebase_user['name'] or firebase_user['email'],
            firebase_uid=firebase_user['uid']
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user info (in case name changed)
        user.email = firebase_user['email']
        user.full_name = firebase_user['name'] or firebase_user['email']
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns user if authenticated, None if not.
    
    Use this for routes that work for both authenticated and anonymous users.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None