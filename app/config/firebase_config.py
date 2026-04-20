# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



"""
Firebase Configuration Module
Handles Firebase Realtime Database initialization and configuration
"""

import pyrebase
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Any
import logging
import os

logger = logging.getLogger(__name__)

from app.config.settings import (
    FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_DATABASE_URL,
    FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID,
    FIREBASE_APP_ID, FIREBASE_MEASUREMENT_ID
)

# ============================================================================
# FIREBASE CONFIG
# ============================================================================

firebaseConfig = {
    'apiKey': FIREBASE_API_KEY,
    'authDomain': FIREBASE_AUTH_DOMAIN,
    'databaseURL': FIREBASE_DATABASE_URL,
    'projectId': FIREBASE_PROJECT_ID,
    'storageBucket': FIREBASE_STORAGE_BUCKET,
    'messagingSenderId': FIREBASE_MESSAGING_SENDER_ID,
    'appId': FIREBASE_APP_ID,
    'measurementId': FIREBASE_MEASUREMENT_ID
}

# ============================================================================
# FIREBASE INITIALIZATION
# ============================================================================

def initialize_firebase() -> Any:
    """
    Initialize Firebase with Realtime Database and Admin SDK
    
    Returns:
        Firebase app instance
    """
    try:
        logger.info("🔑 Initializing Firebase...")
        
        # Initialize Pyrebase (for RTDB REST)
        firebase = pyrebase.initialize_app(firebaseConfig)
        
        # Initialize Firebase Admin SDK (for token verification)
        if not firebase_admin._apps:
            # Check for service account path in env, fallback to default credentials
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': FIREBASE_DATABASE_URL
                })
            else:
                # Use default credentials or partial config
                firebase_admin.initialize_app(options={
                    'databaseURL': FIREBASE_DATABASE_URL
                })
            
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

import threading

_db_lock = threading.Lock()
_db_instance = None

def get_db_connection_pooled():
    """
    Thread-safe database connection with singleton pattern.
    Prevents creating multiple Firebase connections under concurrent load.
    """
    global _db_instance
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:   # Double-checked locking
                _db_instance = get_firebase_app().database()
    return _db_instance
