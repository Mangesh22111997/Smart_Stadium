"""
API Client for communicating with FastAPI backend
"""

import requests
import json
import streamlit as st
from typing import Optional, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

class APIClient:
    """Handles all API calls to FastAPI backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    # ==================== AUTHENTICATION ====================
    
    def signup(self, username: str, email: str, password: str, 
               phone: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """User signup"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/signup",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "phone": phone,
                    "name": name
                },
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def signin(self, username: str, password: str) -> Dict[str, Any]:
        """User login"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/signin",
                json={
                    "username": username,
                    "password": password
                },
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """User logout"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/logout",
                json={"session_token": session_token},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Verify if session is valid"""
        try:
            response = self.session.get(
                f"{self.base_url}/auth/verify-session/{session_token}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        try:
            response = self.session.get(
                f"{self.base_url}/auth/profile/{user_id}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            response = self.session.put(
                f"{self.base_url}/auth/profile/{user_id}",
                json=updates,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== ADMIN AUTHENTICATION ====================
    
    def admin_signup(self, username: str, email: str, password: str,
                    admin_name: str, admin_type: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """Admin signup"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/admin/signup",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "admin_name": admin_name,
                    "admin_type": admin_type,
                    "phone": phone
                },
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def admin_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Admin login"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/admin/signin",
                json={
                    "username": username,
                    "password": password
                },
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_users(self, session_token: str) -> Dict[str, Any]:
        """Get all users (admin only)"""
        try:
            response = self.session.get(
                f"{self.base_url}/auth/users/all",
                params={"session_token": session_token},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== EVENTS ====================
    
    def list_events(self, limit: int = 50) -> Dict[str, Any]:
        """Get all upcoming events"""
        try:
            response = self.session.get(
                f"{self.base_url}/events/list",
                params={"limit": limit},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "events": []}
    
    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Get specific event details"""
        try:
            response = self.session.get(
                f"{self.base_url}/events/{event_id}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def create_event(self, event_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Admin: Create new event"""
        try:
            response = self.session.post(
                f"{self.base_url}/events/create",
                json=event_data,
                params={"session_token": session_token},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== BOOKINGS ====================
    
    def create_booking(self, booking_data: Dict[str, Any], user_id: str, 
                      session_token: str) -> Dict[str, Any]:
        """Create new ticket booking"""
        try:
            response = self.session.post(
                f"{self.base_url}/bookings/create",
                json=booking_data,
                params={"user_id": user_id, "session_token": session_token},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_user_bookings(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Get all bookings for user"""
        try:
            response = self.session.get(
                f"{self.base_url}/bookings/user/{user_id}",
                params={"session_token": session_token},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "bookings": []}
    
    def cancel_booking(self, ticket_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel a booking"""
        try:
            response = self.session.post(
                f"{self.base_url}/bookings/{ticket_id}/cancel",
                params={"user_id": user_id},
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== GATES ====================
    
    def get_all_gates(self) -> Dict[str, Any]:
        """Get status of all gates"""
        try:
            response = self.session.get(
                f"{self.base_url}/gates/all",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "gates": {}}
    
    def get_gate_crowd(self, gate_name: str) -> Dict[str, Any]:
        """Get crowd percentage at specific gate"""
        try:
            response = self.session.get(
                f"{self.base_url}/gates/{gate_name}/crowd",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== FOOD ORDERING ====================
    
    def get_food_menu(self) -> Dict[str, Any]:
        """Get food menu with all items"""
        try:
            response = self.session.get(
                f"{self.base_url}/food/menu",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "items": []}
    
    def place_food_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place a food order"""
        try:
            response = self.session.post(
                f"{self.base_url}/food/orders",
                json=order_data,
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_user_food_orders(self, user_id: str) -> Dict[str, Any]:
        """Get all food orders for user"""
        try:
            response = self.session.get(
                f"{self.base_url}/food/orders/user/{user_id}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "orders": []}
    
    def get_food_order(self, order_id: str) -> Dict[str, Any]:
        """Get specific food order details"""
        try:
            response = self.session.get(
                f"{self.base_url}/food/orders/{order_id}",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is responsive"""
        try:
            response = self.session.get(
                f"{self.base_url}/health/firebase",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


@st.cache_resource
def get_api_client() -> APIClient:
    """Get singleton API client"""
    return APIClient()
