
"""
Firebase Configuration Module
Handles Firebase Realtime Database initialization and configuration
"""

import pyrebase
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# FIREBASE CONFIG
# ============================================================================

firebaseConfig = {
    'apiKey': "AIzaSyCcanmGKxtXCawn0EML0bpL6LgmI1p2CiE",
    'authDomain': "smart-stadium-system-db.firebaseapp.com",
    'databaseURL': "https://smart-stadium-system-db-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "smart-stadium-system-db",
    'storageBucket': "smart-stadium-system-db.firebasestorage.app",
    'messagingSenderId': "771554077981",
    'appId': "1:771554077981:web:2b627c9f72edb53a5245f4",
    'measurementId': "G-BBJBX9TCCH"
}

# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

def initialize_firebase() -> Any:
    """
    Initialize Firebase with Realtime Database
    
    Returns:
        Firebase app instance
    """
    try:
        logger.info("🔑 Initializing Firebase...")
        firebase = pyrebase.initialize_app(firebaseConfig)
        logger.info("✅ Firebase initialized successfully")
        return firebase
        
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {str(e)}")
        raise


# Global Firebase instance
_firebase_app: Optional[Any] = None


def get_firebase_app() -> Any:
    """
    Get Firebase app instance (lazy initialization)
    
    Returns:
        Firebase app instance
    """
    global _firebase_app
    if _firebase_app is None:
        _firebase_app = initialize_firebase()
    return _firebase_app


def get_db_connection() -> Any:
    """
    Get Firebase Realtime Database connection
    
    Returns:
        Realtime Database instance
    """
    firebase = get_firebase_app()
    return firebase.database()


def get_auth_connection() -> Any:
    """
    Get Firebase Authentication connection
    
    Returns:
        Auth instance
    """
    firebase = get_firebase_app()
    return firebase.auth()


def get_storage_connection() -> Any:
    """
    Get Firebase Storage connection
    
    Returns:
        Storage instance
    """
    firebase = get_firebase_app()
    return firebase.storage()


# ============================================================================
# COLLECTION NAMES (Constants)
# ============================================================================

class Collections:
    """Collection/Path name constants"""
    USERS = "users"
    TICKETS = "tickets"
    FOOD_ORDERS = "food_orders"
    EMERGENCIES = "emergencies"
    GATES = "gates"
    CROWD_DATA = "crowd_data"
    NOTIFICATIONS = "notifications"
    STAFF = "staff"
    BOOTH_ALLOCATION = "booth_allocation"
