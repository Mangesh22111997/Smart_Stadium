"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth
from app.services.firebase_auth_service import FirebaseAuthService
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify Firebase ID token or Custom Session Token.
    
    Priority:
    1. Firebase ID Token (Bearer)
    2. Custom Session Token (Bearer - checked against active_sessions)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    
    # 1. Try Firebase ID Token verification
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception:
        # Not a valid Firebase ID token, try custom session token
        pass
        
    # 2. Try Custom Session Token verification
    session = FirebaseAuthService.verify_session(token)
    if session:
        # Map custom session data to a common user dict
        return {
            "uid": session.get("user_id"),
            "email": session.get("email"),
            "username": session.get("username"),
            "is_admin": session.get("is_admin", False),
            "is_security": session.get("is_security", False),
            "session_type": "custom"
        }
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

def admin_only(current_user: dict = Depends(verify_token)) -> dict:
    """
    Dependency to ensure the user has admin privileges.
    
    Args:
        current_user: Decoded user claims/session
        
    Returns:
        User dict if authorized
    """
    if not current_user.get("is_admin"):
        # Check if it's a firebase admin (if we set custom claims) or just the custom session
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized - Admin access required"
        )
    return current_user
