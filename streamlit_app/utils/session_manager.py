"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Session management utilities for Streamlit
"""

import streamlit as st
from typing import Optional, Dict, Any

class SessionManager:
    """Manages user sessions in Streamlit"""
    
    # Session keys
    USER_ID = "user_id"
    USERNAME = "username"
    EMAIL = "email"
    SESSION_TOKEN = "session_token"
    USER_TYPE = "user_type"  # "customer", "admin", "security"
    IS_LOGGED_IN = "is_logged_in"
    ADMIN_TYPE = "admin_type"  # "staff", "moderator", "superadmin"
    PERMISSIONS = "permissions"
    
    @staticmethod
    def init_session() -> None:
        """Initialize session state if not already done"""
        defaults = {
            SessionManager.IS_LOGGED_IN: False,
            SessionManager.USER_ID: None,
            SessionManager.USERNAME: None,
            SessionManager.EMAIL: None,
            SessionManager.SESSION_TOKEN: None,
            SessionManager.USER_TYPE: None,
            SessionManager.ADMIN_TYPE: None,
            SessionManager.PERMISSIONS: {},
        }
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def login_user(user_id: str, username: str, email: str, 
                   session_token: str, user_type: str = "customer") -> None:
        """Set user as logged in"""
        st.session_state[SessionManager.IS_LOGGED_IN] = True
        st.session_state[SessionManager.USER_ID] = user_id
        st.session_state[SessionManager.USERNAME] = username
        st.session_state[SessionManager.EMAIL] = email
        st.session_state[SessionManager.SESSION_TOKEN] = session_token
        st.session_state[SessionManager.USER_TYPE] = user_type
    
    @staticmethod
    def login_admin(admin_id: str, username: str, email: str, 
                    session_token: str, admin_type: str, permissions: Dict[str, Any]) -> None:
        """Set admin as logged in"""
        st.session_state[SessionManager.IS_LOGGED_IN] = True
        st.session_state[SessionManager.USER_ID] = admin_id
        st.session_state[SessionManager.USERNAME] = username
        st.session_state[SessionManager.EMAIL] = email
        st.session_state[SessionManager.SESSION_TOKEN] = session_token
        st.session_state[SessionManager.USER_TYPE] = "admin"
        st.session_state[SessionManager.ADMIN_TYPE] = admin_type
        st.session_state[SessionManager.PERMISSIONS] = permissions
    
    @staticmethod
    def login_security(staff_id: str, username: str, email: str, 
                      session_token: str, role: str, permissions: Dict[str, Any]) -> None:
        """Set security staff as logged in"""
        st.session_state[SessionManager.IS_LOGGED_IN] = True
        st.session_state[SessionManager.USER_ID] = staff_id
        st.session_state[SessionManager.USERNAME] = username
        st.session_state[SessionManager.EMAIL] = email
        st.session_state[SessionManager.SESSION_TOKEN] = session_token
        st.session_state[SessionManager.USER_TYPE] = "security"
        st.session_state[SessionManager.ADMIN_TYPE] = role  # Store role in admin_type field
        st.session_state[SessionManager.PERMISSIONS] = permissions
    
    @staticmethod
    def logout() -> None:
        """Clear user session"""
        st.session_state[SessionManager.IS_LOGGED_IN] = False
        st.session_state[SessionManager.USER_ID] = None
        st.session_state[SessionManager.USERNAME] = None
        st.session_state[SessionManager.EMAIL] = None
        st.session_state[SessionManager.SESSION_TOKEN] = None
        st.session_state[SessionManager.USER_TYPE] = None
        st.session_state[SessionManager.ADMIN_TYPE] = None
        st.session_state[SessionManager.PERMISSIONS] = {}
    
    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in"""
        return st.session_state.get(SessionManager.IS_LOGGED_IN, False)
    
    @staticmethod
    def is_admin() -> bool:
        """Check if user is admin"""
        return st.session_state.get(SessionManager.USER_TYPE) == "admin"
    
    @staticmethod
    def is_customer() -> bool:
        """Check if user is customer"""
        return st.session_state.get(SessionManager.USER_TYPE) == "customer"
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """Get current user ID"""
        return st.session_state.get(SessionManager.USER_ID)
    
    @staticmethod
    def get_session_token() -> Optional[str]:
        """Get current session token"""
        return st.session_state.get(SessionManager.SESSION_TOKEN)
    
    @staticmethod
    def get_username() -> Optional[str]:
        """Get current username"""
        return st.session_state.get(SessionManager.USERNAME)
    
    @staticmethod
    def get_email() -> Optional[str]:
        """Get current email"""
        return st.session_state.get(SessionManager.EMAIL)
    
    @staticmethod
    def get_admin_type() -> Optional[str]:
        """Get admin type"""
        return st.session_state.get(SessionManager.ADMIN_TYPE)
    
    @staticmethod
    def has_permission(permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = st.session_state.get(SessionManager.PERMISSIONS, {})
        return permissions.get(permission, False)
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get user type/role"""
        return st.session_state.get(SessionManager.USER_TYPE)
    
    @staticmethod
    def is_security() -> bool:
        """Check if user is security staff"""
        return st.session_state.get(SessionManager.USER_TYPE) == "security"
    
    @staticmethod
    def set_session_token(token: str) -> None:
        """Set session token"""
        st.session_state[SessionManager.SESSION_TOKEN] = token
    
    @staticmethod
    def set_user_id(user_id: str) -> None:
        """Set user ID"""
        st.session_state[SessionManager.USER_ID] = user_id
    
    @staticmethod
    def set_username(username: str) -> None:
        """Set username"""
        st.session_state[SessionManager.USERNAME] = username
    
    @staticmethod
    def set_user_role(user_type: str) -> None:
        """Set user type/role"""
        st.session_state[SessionManager.USER_TYPE] = user_type
