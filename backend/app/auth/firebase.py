"""
Firebase authentication utilities for FastAPI backend.
This module handles Firebase ID token verification.
"""
import os
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

class FirebaseAuth:
    """
    Firebase authentication handler.
    
    This class verifies Firebase ID tokens sent from the frontend.
    Think of it as a "bouncer" that checks if tokens are legitimate.
    """
    
    def __init__(self):
        # Get the Firebase project ID from our config
        self.project_id = settings.firebase_project_id
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a Firebase ID token and return user information.
        
        Args:
            token: Firebase ID token from frontend
            
        Returns:
            User info dict if token is valid, None if invalid
            
        This is the CORE function that:
        1. Takes a token from React frontend
        2. Asks Firebase "is this token real?"
        3. Returns user info if valid
        """
        try:
            # Verify the token with Firebase
            # This is like asking Firebase: "Is this token legitimate?"
            decoded_token = id_token.verify_firebase_token(
                token, 
                requests.Request(),
                audience=self.project_id
            )
            
            # Extract user information
            user_info = {
                'uid': decoded_token['uid'],  # Firebase user ID
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'email_verified': decoded_token.get('email_verified', False)
            }
            
            return user_info
            
        except ValueError as e:
            # Token is invalid (expired, malformed, etc.)
            print(f"Invalid token: {e}")
            return None
        except Exception as e:
            # Other errors (network, Firebase issues, etc.)
            print(f"Token verification error: {e}")
            return None

# Create a global instance
firebase_auth = FirebaseAuth()