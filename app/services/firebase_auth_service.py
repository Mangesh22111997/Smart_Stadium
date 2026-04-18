"""
Firebase Authentication Service
Handles user registration, login, and authentication with Firebase Realtime Database
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.config.firebase_config import get_db_connection, get_auth_connection
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthService:
    """Service for Firebase-based authentication"""
    
    # Database paths
    USERS_PATH = "users"
    ADMINS_PATH = "admins"
    ACTIVE_SESSIONS_PATH = "active_sessions"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password
    
    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        phone: str = None,
        name: str = None
    ) -> Dict[str, Any]:
        """
        Register a new user in Firebase
        
        Args:
            username: Unique username
            email: User's email address
            password: User's password (will be hashed)
            phone: Optional phone number
            name: Optional full name
            
        Returns:
            User data with ID if successful
        """
        try:
            db = get_db_connection()
            
            # Check if username exists
            users = db.child(FirebaseAuthService.USERS_PATH).get()
            if users.val():
                for user_key, user_data in users.val().items():
                    if user_data.get('username') == username:
                        raise ValueError(f"Username '{username}' already exists")
                    if user_data.get('email') == email:
                        raise ValueError(f"Email '{email}' already registered")
            
            # Create new user
            user_data = {
                "username": username,
                "email": email,
                "password_hash": FirebaseAuthService.hash_password(password),
                "phone": phone or "",
                "name": name or username,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "profile_complete": False
            }
            
            # Push to Firebase (auto-generates key)
            result = db.child(FirebaseAuthService.USERS_PATH).push(user_data)
            
            logger.info(f"✅ User registered: {username}")
            print(f"✅ User registered: {username} ({result['name']})")
            
            return {
                "user_id": result['name'],
                **user_data,
                "password_hash": "***"  # Don't expose hash
            }
            
        except Exception as e:
            logger.error(f"❌ User registration failed: {str(e)}")
            raise
    
    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and create session
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            User data with session token if successful
        """
        try:
            db = get_db_connection()
            
            # Find user by username
            users = db.child(FirebaseAuthService.USERS_PATH).get()
            if not users.val():
                raise ValueError("Username or password incorrect")
            
            user_found = None
            user_id = None
            
            for uid, user_data in users.val().items():
                if user_data.get('username') == username:
                    user_found = user_data
                    user_id = uid
                    break
            
            if not user_found:
                raise ValueError("Username or password incorrect")
            
            # Verify password
            if not FirebaseAuthService.verify_password(password, user_found.get('password_hash')):
                raise ValueError("Username or password incorrect")
            
            if not user_found.get('is_active'):
                raise ValueError("Account is inactive")
            
            # Update last login
            db.child(FirebaseAuthService.USERS_PATH).child(user_id).update({
                "last_login": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            # Create session
            session_token = hashlib.sha256(
                f"{user_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            db.child(FirebaseAuthService.ACTIVE_SESSIONS_PATH).child(session_token).set({
                "user_id": user_id,
                "username": username,
                "email": user_found.get('email'),
                "login_time": datetime.now().isoformat(),
                "is_active": True
            })
            
            logger.info(f"✅ User logged in: {username}")
            print(f"✅ User logged in: {username}")
            
            return {
                "user_id": user_id,
                "username": username,
                "email": user_found.get('email'),
                "name": user_found.get('name'),
                "session_token": session_token,
                "login_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Login failed: {str(e)}")
            raise
    
    @staticmethod
    def logout_user(session_token: str) -> bool:
        """
        Logout user by removing session
        
        Args:
            session_token: User's session token
            
        Returns:
            True if successful
        """
        try:
            db = get_db_connection()
            db.child(FirebaseAuthService.ACTIVE_SESSIONS_PATH).child(session_token).remove()
            logger.info("✅ User logged out")
            return True
        except Exception as e:
            logger.error(f"❌ Logout failed: {str(e)}")
            return False
    
    @staticmethod
    def verify_session(session_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify if a session is valid
        
        Args:
            session_token: Session token to verify
            
        Returns:
            Session data if valid, None otherwise
        """
        try:
            db = get_db_connection()
            session = db.child(FirebaseAuthService.ACTIVE_SESSIONS_PATH).child(session_token).get()
            
            if session.val():
                return session.val()
            return None
            
        except Exception as e:
            logger.error(f"❌ Session verification failed: {str(e)}")
            return None
    
    @staticmethod
    def register_admin(
        username: str,
        email: str,
        password: str,
        admin_name: str,
        admin_type: str = "staff",  # staff, moderator, superadmin
        phone: str = None
    ) -> Dict[str, Any]:
        """
        Register a new admin in Firebase
        
        Args:
            username: Unique admin username
            email: Admin's email address
            password: Admin's password (will be hashed)
            admin_name: Admin's full name
            admin_type: Type of admin (staff, moderator, superadmin)
            phone: Optional phone number
            
        Returns:
            Admin data with ID if successful
        """
        try:
            db = get_db_connection()
            
            # Check if admin username exists
            admins = db.child(FirebaseAuthService.ADMINS_PATH).get()
            if admins.val():
                for admin_key, admin_data in admins.val().items():
                    if admin_data.get('username') == username:
                        raise ValueError(f"Admin username '{username}' already exists")
                    if admin_data.get('email') == email:
                        raise ValueError(f"Admin email '{email}' already exists")
            
            # Create new admin
            admin_data = {
                "username": username,
                "email": email,
                "password_hash": FirebaseAuthService.hash_password(password),
                "phone": phone or "",
                "name": admin_name,
                "admin_type": admin_type,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True,
                "permissions": FirebaseAuthService._get_admin_permissions(admin_type)
            }
            
            # Push to Firebase
            result = db.child(FirebaseAuthService.ADMINS_PATH).push(admin_data)
            
            logger.info(f"✅ Admin registered: {username} ({admin_type})")
            print(f"✅ Admin registered: {username} ({admin_type})")
            
            return {
                "admin_id": result['name'],
                **admin_data,
                "password_hash": "***"
            }
            
        except Exception as e:
            logger.error(f"❌ Admin registration failed: {str(e)}")
            raise
    
    @staticmethod
    def _get_admin_permissions(admin_type: str) -> List[str]:
        """
        Get permissions based on admin type
        
        Args:
            admin_type: Type of admin
            
        Returns:
            List of permissions
        """
        permissions = {
            "staff": ["view_dashboard", "manage_emergencies", "view_reports"],
            "moderator": ["view_dashboard", "manage_users", "manage_emergencies", "view_reports", "update_settings"],
            "superadmin": ["*"]  # All permissions
        }
        return permissions.get(admin_type, [])
    
    @staticmethod
    def admin_login(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate admin
        
        Args:
            username: Admin's username
            password: Admin's password
            
        Returns:
            Admin data with session token if successful
        """
        try:
            db = get_db_connection()
            
            # Find admin by username
            admins = db.child(FirebaseAuthService.ADMINS_PATH).get()
            if not admins.val():
                raise ValueError("Admin username or password incorrect")
            
            admin_found = None
            admin_id = None
            
            for aid, admin_data in admins.val().items():
                if admin_data.get('username') == username:
                    admin_found = admin_data
                    admin_id = aid
                    break
            
            if not admin_found:
                raise ValueError("Admin username or password incorrect")
            
            # Verify password
            if not FirebaseAuthService.verify_password(password, admin_found.get('password_hash')):
                raise ValueError("Admin username or password incorrect")
            
            if not admin_found.get('is_active'):
                raise ValueError("Admin account is inactive")
            
            # Update last login
            db.child(FirebaseAuthService.ADMINS_PATH).child(admin_id).update({
                "last_login": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            # Create session
            session_token = hashlib.sha256(
                f"admin_{admin_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            db.child(FirebaseAuthService.ACTIVE_SESSIONS_PATH).child(session_token).set({
                "admin_id": admin_id,
                "username": username,
                "email": admin_found.get('email'),
                "admin_type": admin_found.get('admin_type'),
                "login_time": datetime.now().isoformat(),
                "is_admin": True,
                "permissions": admin_found.get('permissions')
            })
            
            logger.info(f"✅ Admin logged in: {username}")
            print(f"✅ Admin logged in: {username}")
            
            return {
                "admin_id": admin_id,
                "username": username,
                "email": admin_found.get('email'),
                "name": admin_found.get('name'),
                "admin_type": admin_found.get('admin_type'),
                "session_token": session_token,
                "login_time": datetime.now().isoformat(),
                "permissions": admin_found.get('permissions')
            }
            
        except Exception as e:
            logger.error(f"❌ Admin login failed: {str(e)}")
            raise
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by ID
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            User profile data or None
        """
        try:
            db = get_db_connection()
            user = db.child(FirebaseAuthService.USERS_PATH).child(user_id).get()
            
            if user.val():
                user_data = user.val()
                user_data["user_id"] = user_id
                user_data.pop("password_hash", None)  # Remove password hash
                return user_data
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {str(e)}")
            return None
    
    @staticmethod
    def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user profile
        
        Args:
            user_id: Firebase user ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            db = get_db_connection()
            
            # Don't allow password hash update through this method
            updates.pop("password_hash", None)
            updates["updated_at"] = datetime.now().isoformat()
            
            db.child(FirebaseAuthService.USERS_PATH).child(user_id).update(updates)
            
            logger.info(f"✅ User profile updated: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update user profile: {str(e)}")
            return False
    
    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """
        Get all registered users
        
        Returns:
            List of user profiles (without passwords)
        """
        try:
            db = get_db_connection()
            users = db.child(FirebaseAuthService.USERS_PATH).get()
            
            if not users.val():
                return []
            
            user_list = []
            for user_id, user_data in users.val().items():
                user_data["user_id"] = user_id
                user_data.pop("password_hash", None)
                user_list.append(user_data)
            
            return user_list
            
        except Exception as e:
            logger.error(f"❌ Failed to get all users: {str(e)}")
            return []
