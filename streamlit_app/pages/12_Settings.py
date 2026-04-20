"""
Admin Settings Page
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Settings - Admin", page_icon="⚙️", layout="wide")

if not SessionManager.is_logged_in() or not SessionManager.is_admin():
    st.error("❌ Admin access required")
    st.stop()

st.markdown("# ⚙️ Admin Settings")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()

st.markdown("## Account Information")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Username:** {SessionManager.get_username()}")
    st.write(f"**Email:** {SessionManager.get_email()}")
with col2:
    st.write(f"**Admin Type:** {SessionManager.get_admin_type()}")
    st.write(f"**User ID:** {SessionManager.get_user_id()}")

st.divider()

st.markdown("## Permissions")
permissions = st.session_state.get("permissions", {})
for perm, value in permissions.items():
    st.write(f"- {perm.replace('_', ' ').title()}: {'✅' if value else '❌'}")

if st.button("📊 Back to Dashboard"):
    st.switch_page("pages/09_admin_dashboard.py")
