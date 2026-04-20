
"""
API Client for communicating with FastAPI backend
"""

import requests
import json
import streamlit as st
import os
from typing import Optional, Dict, Any, List
from requests.exceptions import ConnectionError, Timeout as RequestTimeout

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10

class APIClient:
    """Handles all API calls to FastAPI backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def _safe_call(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with consistent error handling.
        Shows a Streamlit warning if the backend is unreachable.
        """
        try:
            response = getattr(self.session, method)(url, timeout=TIMEOUT, **kwargs)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, RequestTimeout):
            st.warning("⚠️ Cannot reach the server. Check your connection and refresh.", icon="🔌")
            return {"error": "connection_failed"}
        except Exception as e:
            # Handle non-200 responses that return JSON error bodies
            try:
                return response.json()
            except:
                return {"error": str(e)}

    # ==================== AUTHENTICATION ====================
    
    def signup(self, username: str, email: str, password: str, 
               phone: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """User signup"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/signup",
            json={
                "username": username,
                "email": email,
                "password": password,
                "phone": phone,
                "name": name
            }
        )
    
    def signin(self, username: str, password: str) -> Dict[str, Any]:
        """User login"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/signin",
            json={
                "username": username,
                "password": password
            }
        )
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """User logout"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/logout",
            json={"session_token": session_token}
        )
    
    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Verify if session is valid"""
        return self._safe_call(
            "get",
            f"{self.base_url}/auth/verify-session/{session_token}"
        )
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        return self._safe_call(
            "get",
            f"{self.base_url}/auth/profile/{user_id}"
        )
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        return self._safe_call(
            "put",
            f"{self.base_url}/auth/profile/{user_id}",
            json=updates
        )
    
    # ==================== ADMIN AUTHENTICATION ====================
    
    def admin_signup(self, username: str, email: str, password: str,
                    admin_name: str, admin_type: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Admin signup"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/admin/signup",
            json={
                "username": username,
                "email": email,
                "password": password,
                "admin_name": admin_name,
                "admin_type": admin_type,
                "phone": phone
            }
        )
    
    def admin_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Admin login"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/admin/signin",
            json={
                "username": username,
                "password": password
            }
        )
    
    def security_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Security staff login"""
        return self._safe_call(
            "post",
            f"{self.base_url}/auth/security/signin",
            json={
                "username": username,
                "password": password
            }
        )
    
    def get_all_users(self, session_token: str) -> Dict[str, Any]:
        """Get all users (admin only) - Sends token in header"""
        return self._safe_call(
            "get",
            f"{self.base_url}/auth/users/all",
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    # ==================== EVENTS ====================
    
    def list_events(self, limit: int = 50) -> Dict[str, Any]:
        """Get all upcoming events"""
        result = self._safe_call(
            "get",
            f"{self.base_url}/events/list",
            params={"limit": limit}
        )
        if "error" in result and "events" not in result:
            result["events"] = []
        return result
    
    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get specific event details"""
        return self._safe_call(
            "get",
            f"{self.base_url}/events/{event_id}"
        )
    
    def create_event(self, event_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Admin: Create new event"""
        return self._safe_call(
            "post",
            f"{self.base_url}/events/create",
            json=event_data,
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    # ==================== BOOKINGS ====================
    
    def create_booking(self, booking_data: Dict[str, Any], user_id: str, 
                      session_token: str) -> Dict[str, Any]:
        """Create new ticket booking"""
        return self._safe_call(
            "post",
            f"{self.base_url}/bookings/create",
            json=booking_data,
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    def get_user_bookings(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Get all bookings for user"""
        result = self._safe_call(
            "get",
            f"{self.base_url}/bookings/user/{user_id}",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        if "error" in result and "bookings" not in result:
            result["bookings"] = []
        return result
    
    def cancel_booking(self, ticket_id: str, user_id: str, session_token: str) -> Dict[str, Any]:
        """Cancel a booking"""
        return self._safe_call(
            "post",
            f"{self.base_url}/bookings/{ticket_id}/cancel",
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    # ==================== GATES ====================
    
    def get_all_gates(self) -> Dict[str, Any]:
        """Get status of all gates"""
        result = self._safe_call(
            "get",
            f"{self.base_url}/gates/all"
        )
        if "error" in result and "gates" not in result:
            result["gates"] = {}
        return result
    
    def get_gate_crowd(self, gate_name: str) -> Dict[str, Any]:
        """Get crowd percentage at specific gate"""
        return self._safe_call(
            "get",
            f"{self.base_url}/gates/{gate_name}/crowd"
        )
    
    # ==================== FOOD ORDERING ====================
    
    def get_food_menu(self) -> Dict[str, Any]:
        """Get food menu with all items"""
        result = self._safe_call(
            "get",
            f"{self.base_url}/food/menu"
        )
        if "error" in result and "items" not in result:
            result["items"] = []
        return result
    
    def place_food_order(self, order_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Place a food order"""
        return self._safe_call(
            "post",
            f"{self.base_url}/food/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    def get_user_food_orders(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Get all food orders for user"""
        result = self._safe_call(
            "get",
            f"{self.base_url}/food/orders/user/{user_id}",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        if "error" in result and "orders" not in result:
            result["orders"] = []
        return result
    
    def get_food_order(self, order_id: str, session_token: str) -> Dict[str, Any]:
        """Get specific food order details"""
        return self._safe_call(
            "get",
            f"{self.base_url}/food/orders/{order_id}",
            headers={"Authorization": f"Bearer {session_token}"}
        )
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is responsive"""
        return self._safe_call(
            "get",
            f"{self.base_url}/health/firebase"
        )


@st.cache_resource
def get_api_client() -> APIClient:
    """Get singleton API client"""
    return APIClient()
