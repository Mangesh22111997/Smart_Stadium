"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
API Client — communicates with the FastAPI backend.
Reads API_BASE_URL from environment so it works both locally and on Cloud Run.
"""

import os
import requests
import streamlit as st
from requests.exceptions import ConnectionError, Timeout
from typing import Optional, Dict, Any

# Cloud Run: set via --set-env-vars API_BASE_URL=https://stadium-backend-xxx.run.app
# Local dev: falls back to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 10


class APIClient:
    """Handles all HTTP communication with the FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    # ── Internal helpers ───────────────────────────────────────────────────

    def _safe_call(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with consistent timeout and error handling.
        Shows a Streamlit warning on connection failure (offline-safe).

        Returns parsed JSON on success, {"error": reason} on any failure.
        """
        try:
            response = getattr(self.session, method)(url, timeout=TIMEOUT, **kwargs)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, Timeout):
            st.warning("⚠️ Cannot reach the server. Check your connection and refresh.", icon="🔌")
            return {"error": "connection_failed"}
        except requests.HTTPError as e:
            return {"error": f"http_{e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _auth_header(self, token: str) -> Dict[str, str]:
        """Return an Authorization Bearer header dict."""
        return {"Authorization": f"Bearer {token}"}

    # ── Authentication ─────────────────────────────────────────────────────

    def signup(self, username: str, email: str, password: str,
               phone: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user account."""
        return self._safe_call("post", f"{self.base_url}/auth/signup", json={
            "username": username, "email": email, "password": password,
            "phone": phone, "name": name,
        })

    def signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return session token."""
        return self._safe_call("post", f"{self.base_url}/auth/signin", json={
            "username": username, "password": password,
        })

    def logout(self, session_token: str) -> Dict[str, Any]:
        """Invalidate user session."""
        return self._safe_call("post", f"{self.base_url}/auth/logout",
                               json={"session_token": session_token})

    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Check whether a session token is still valid."""
        return self._safe_call("get",
                               f"{self.base_url}/auth/verify-session/{session_token}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch a user's public profile."""
        return self._safe_call("get", f"{self.base_url}/auth/profile/{user_id}")

    # ── Admin auth ─────────────────────────────────────────────────────────

    def admin_signup(self, username: str, email: str, password: str,
                     admin_name: str, admin_type: str,
                     phone: Optional[str] = None) -> Dict[str, Any]:
        """Register a new admin account."""
        return self._safe_call("post", f"{self.base_url}/auth/admin/signup", json={
            "username": username, "email": email, "password": password,
            "admin_name": admin_name, "admin_type": admin_type, "phone": phone,
        })

    def admin_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin and return session token."""
        return self._safe_call("post", f"{self.base_url}/auth/admin/signin", json={
            "username": username, "password": password,
        })

    def security_signin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate security staff."""
        return self._safe_call("post", f"{self.base_url}/auth/security/signin", json={
            "username": username, "password": password,
        })

    def get_all_users(self, session_token: str) -> Dict[str, Any]:
        """Get all users — admin only. Token sent in Authorization header."""
        return self._safe_call("get", f"{self.base_url}/auth/users/all",
                               headers=self._auth_header(session_token))

    # ── Events ─────────────────────────────────────────────────────────────

    def list_events(self, limit: int = 50) -> Dict[str, Any]:
        """Fetch the event catalogue."""
        return self._safe_call("get", f"{self.base_url}/events/list",
                               params={"limit": limit})

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Fetch full details for a single event."""
        return self._safe_call("get", f"{self.base_url}/events/{event_id}")

    def create_event(self, event_data: Dict[str, Any], session_token: str) -> Dict[str, Any]:
        """Admin: create a new event."""
        return self._safe_call("post", f"{self.base_url}/events/create",
                               json=event_data,
                               headers=self._auth_header(session_token))

    # ── Bookings ───────────────────────────────────────────────────────────

    def create_booking(self, booking_data: Dict[str, Any],
                       session_token: str) -> Dict[str, Any]:
        """Create a ticket booking for the authenticated user."""
        return self._safe_call("post", f"{self.base_url}/bookings/create",
                               json=booking_data,
                               headers=self._auth_header(session_token))

    def get_user_bookings(self, user_id: str, session_token: str) -> Dict[str, Any]:
        """Fetch all bookings belonging to a user."""
        return self._safe_call("get", f"{self.base_url}/bookings/user/{user_id}",
                               headers=self._auth_header(session_token))

    def cancel_booking(self, ticket_id: str, session_token: str) -> Dict[str, Any]:
        """Cancel a confirmed booking."""
        return self._safe_call("post", f"{self.base_url}/bookings/{ticket_id}/cancel",
                               headers=self._auth_header(session_token))

    # ── Gates ──────────────────────────────────────────────────────────────

    def get_all_gates(self) -> Dict[str, Any]:
        """Get live status of all gates."""
        return self._safe_call("get", f"{self.base_url}/gates/all")

    def get_gate_crowd(self, gate_name: str) -> Dict[str, Any]:
        """Get crowd percentage at a specific gate."""
        return self._safe_call("get", f"{self.base_url}/gates/{gate_name}/crowd")

    # ── Food ordering ──────────────────────────────────────────────────────

    def get_food_menu(self) -> Dict[str, Any]:
        """Fetch the full food menu."""
        return self._safe_call("get", f"{self.base_url}/food/menu")

    def place_food_order(self, order_data: Dict[str, Any],
                         session_token: str) -> Dict[str, Any]:
        """Place a food/beverage order."""
        return self._safe_call("post", f"{self.base_url}/food/orders",
                               json=order_data,
                               headers=self._auth_header(session_token))

    def get_user_food_orders(self, user_id: str) -> Dict[str, Any]:
        """Fetch all food orders for a user."""
        return self._safe_call("get", f"{self.base_url}/food/orders/user/{user_id}")

    # ── Health ─────────────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        """Verify that the backend API is reachable."""
        return self._safe_call("get", f"{self.base_url}/health")


@st.cache_resource
def get_api_client() -> APIClient:
    """Return the singleton API client (cached for the Streamlit session)."""
    return APIClient()
