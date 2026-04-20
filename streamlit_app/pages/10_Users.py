"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Users Management Page
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Users - Admin", page_icon="👥", layout="wide")

if not SessionManager.is_logged_in() or not SessionManager.is_admin():
    st.error("❌ Admin access required")
    st.stop()

st.markdown("# 👥 User Management")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()

api_client = get_api_client()

with st.spinner("📋 Loading users..."):
    users_response = api_client.get_all_users(SessionManager.get_session_token())

if "users" in users_response:
    st.success(f"Found {len(users_response.get('users', []))} users")
    for user in users_response.get("users", []):
        with st.expander(f"👤 {user.get('username', 'N/A')} ({user.get('email', 'N/A')})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**User ID:** {user.get('user_id')}")
                st.write(f"**Username:** {user.get('username')}")
                st.write(f"**Email:** {user.get('email')}")
            with col2:
                st.write(f"**Created:** {user.get('created_at', 'N/A')}")
                st.write(f"**Status:** {'✅ Active' if user.get('is_active') else '❌ Inactive'}")
else:
    st.error(f"Failed to load users: {users_response.get('detail', 'Unknown error')}")

if st.button("📊 Back to Dashboard"):
    st.switch_page("pages/09_admin_dashboard.py")
