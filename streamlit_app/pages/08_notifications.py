"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Notifications Page
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Notifications - Smart Stadium", page_icon="🔔", layout="wide")

if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

st.markdown("# 🔔 Notifications")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()

st.success("✅ **Event Starting Soon!** Cricket Tournament starts in 2 hours")
st.warning("⚠️ **Gate Alert** - Gate A has congestion. Use Gate B instead")
st.info("ℹ️ **Order Ready** - Your food order is ready for pickup at Booth 3")

st.divider()

st.markdown("### Notification History")
st.write("No more notifications")

if st.button("🏠 Back to Home"):
    st.switch_page("pages/02_home.py")
