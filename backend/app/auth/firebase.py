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
            
            print(f"✅ Token decoded successfully")
            print(f"📋 Token keys: {list(decoded_token.keys())}")
            print(f"🔑 Token content: {decoded_token}")
            
            # Extract user information
            # Handle both 'uid' and 'user_id' field names
            uid = decoded_token.get('uid') or decoded_token.get('user_id') or decoded_token.get('sub')
            
            if not uid:
                print(f"❌ No UID found in token. Available keys: {list(decoded_token.keys())}")
                return None
            
            user_info = {
                'uid': uid,
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'email_verified': decoded_token.get('email_verified', False)
            }
            
            print(f"✅ User info extracted: uid={uid}, email={decoded_token.get('email')}")
            return user_info
            
        except ValueError as e:
            # Token is invalid (expired, malformed, etc.)
            print(f"❌ Invalid token (ValueError): {e}")
            return None
        except KeyError as e:
            # Missing required field
            print(f"❌ Token missing required field: {e}")
            return None
        except Exception as e:
            # Other errors (network, Firebase issues, etc.)
            print(f"❌ Token verification error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

# Create a global instance
firebase_auth = FirebaseAuth()