"""
Authentication Routes - API endpoints for user and admin authentication
Integrates with Firebase Realtime Database
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.services.firebase_auth_service import FirebaseAuthService
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SignUpRequest(BaseModel):
    """User sign up request"""
    username: str
    email: EmailStr
    password: str
    name: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        example = {
            "username": "mangesh-developer",
            "email": "mangesh@example.com",
            "password": "secure_password",
            "name": "Mangesh Developer",
            "phone": "+91-9876543210"
        }


class SignInRequest(BaseModel):
    """User sign in request"""
    username: str
    password: str
    
    class Config:
        example = {
            "username": "mangesh-developer",
            "password": "secure_password"
        }


class SignUpResponse(BaseModel):
    """User sign up response"""
    user_id: str
    username: str
    email: str
    name: str
    created_at: str
    message: str = "User registered successfully"


class SignInResponse(BaseModel):
    """User sign in response"""
    user_id: str
    username: str
    email: str
    name: str
    session_token: str
    login_time: str
    message: str = "Login successful"


class AdminSignUpRequest(BaseModel):
    """Admin sign up request"""
    username: str
    email: EmailStr
    password: str
    admin_name: str
    admin_type: str = "staff"  # staff, moderator, superadmin
    phone: Optional[str] = None
    
    class Config:
        example = {
            "username": "admin_mangesh",
            "email": "admin@example.com",
            "password": "admin_secure_password",
            "admin_name": "Mangesh Admin",
            "admin_type": "moderator",
            "phone": "+91-9876543210"
        }


class AdminSignInResponse(BaseModel):
    """Admin sign in response"""
    admin_id: str
    username: str
    email: str
    name: str
    admin_type: str
    session_token: str
    login_time: str
    permissions: list
    message: str = "Admin login successful"


class LogoutResponse(BaseModel):
    """Logout response"""
    message: str = "Logged out successfully"


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    username: str
    email: str
    name: str
    phone: Optional[str]
    created_at: str
    updated_at: str
    is_active: bool
    profile_complete: bool


# ============================================================================
# USER AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED, tags=["User Auth"])
async def sign_up(request: SignUpRequest) -> Dict[str, Any]:
    """
    Register a new user
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Strong password
    - **name**: User's full name (optional)
    - **phone**: Phone number (optional)
    
    Returns: User data with ID
    """
    try:
        result = FirebaseAuthService.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            name=request.name,
            phone=request.phone
        )
        
        return {
            "user_id": result["user_id"],
            "username": result["username"],
            "email": result["email"],
            "name": result["name"],
            "created_at": result["created_at"],
            "message": "User registered successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Sign up error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sign up failed"
        )


@router.post("/signin", response_model=SignInResponse, status_code=status.HTTP_200_OK, tags=["User Auth"])
async def sign_in(request: SignInRequest) -> Dict[str, Any]:
    """
    User login
    
    - **username**: User's username
    - **password**: User's password
    
    Returns: User data with session token
    """
    try:
        result = FirebaseAuthService.login_user(
            username=request.username,
            password=request.password
        )
        
        return {
            "user_id": result["user_id"],
            "username": result["username"],
            "email": result["email"],
            "name": result["name"],
            "session_token": result["session_token"],
            "login_time": result["login_time"],
            "message": "Login successful"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Sign in error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout", response_model=LogoutResponse, tags=["User Auth"])
async def logout(session_token: str) -> Dict[str, str]:
    """
    User logout
    
    - **session_token**: User's session token
    
    Returns: Logout confirmation
    """
    try:
        if FirebaseAuthService.logout_user(session_token):
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
            
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/verify-session/{session_token}", tags=["User Auth"])
async def verify_session(session_token: str) -> Dict[str, Any]:
    """
    Verify if a session token is valid
    
    - **session_token**: Session token to verify
    
    Returns: Session data if valid
    """
    try:
        session = FirebaseAuthService.verify_session(session_token)
        
        if session:
            return {
                "valid": True,
                "user_id": session.get("user_id"),
                "username": session.get("username"),
                "email": session.get("email"),
                "login_time": session.get("login_time")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
            
    except Exception as e:
        logger.error(f"Session verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session verification failed"
        )


@router.get("/profile/{user_id}", response_model=UserProfileResponse, tags=["User Auth"])
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Get user profile
    
    - **user_id**: Firebase user ID
    
    Returns: User profile data
    """
    try:
        profile = FirebaseAuthService.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return profile
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


# ============================================================================
# ADMIN AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/admin/signup", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED, tags=["Admin Auth"])
async def admin_sign_up(request: AdminSignUpRequest) -> Dict[str, Any]:
    """
    Register a new admin
    
    - **username**: Unique admin username
    - **email**: Admin email address
    - **password**: Strong password
    - **admin_name**: Admin's full name
    - **admin_type**: staff, moderator, or superadmin
    - **phone**: Phone number (optional)
    
    Returns: Admin data with ID
    """
    try:
        result = FirebaseAuthService.register_admin(
            username=request.username,
            email=request.email,
            password=request.password,
            admin_name=request.admin_name,
            admin_type=request.admin_type,
            phone=request.phone
        )
        
        return {
            "admin_id": result["admin_id"],
            "username": result["username"],
            "email": result["email"],
            "name": result["name"],
            "admin_type": result["admin_type"],
            "created_at": result["created_at"],
            "message": "Admin registered successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Admin sign up error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin registration failed"
        )


@router.post("/admin/signin", response_model=AdminSignInResponse, status_code=status.HTTP_200_OK, tags=["Admin Auth"])
async def admin_sign_in(request: SignInRequest) -> Dict[str, Any]:
    """
    Admin login
    
    - **username**: Admin's username
    - **password**: Admin's password
    
    Returns: Admin data with session token and permissions
    """
    try:
        result = FirebaseAuthService.admin_login(
            username=request.username,
            password=request.password
        )
        
        return {
            "admin_id": result["admin_id"],
            "username": result["username"],
            "email": result["email"],
            "name": result["name"],
            "admin_type": result["admin_type"],
            "session_token": result["session_token"],
            "login_time": result["login_time"],
            "permissions": result["permissions"],
            "message": "Admin login successful"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Admin sign in error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin login failed"
        )


@router.get("/users/all", tags=["Admin Auth"])
async def get_all_users(session_token: str = None) -> Dict[str, Any]:
    """
    Get all registered users (admin only)
    
    - **session_token**: Optional admin session token for verification
    
    Returns: List of all users
    """
    try:
        # Verify admin session if token provided
        if session_token:
            session = FirebaseAuthService.verify_session(session_token)
            if not session or not session.get("is_admin"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized - Admin access required"
                )
        
        users = FirebaseAuthService.get_all_users()
        
        return {
            "total": len(users),
            "users": users
        }
        
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )
