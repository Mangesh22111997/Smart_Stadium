# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Gates Management Page
"""

import streamlit as st
st.set_page_config(page_title="Gates - Admin", page_icon="🚪", layout="wide")

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()


if not SessionManager.is_logged_in() or not SessionManager.is_admin():
    st.error("❌ Admin access required")
    st.stop()

st.markdown("# 🚪 Gate Management")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()

gates = ['Gate A', 'Gate B', 'Gate C', 'Gate D', 'Gate E']

for i, gate in enumerate(gates):
    col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])
    
    with col1:
        st.markdown(f"### {gate}")
    with col2:
        status = st.selectbox(f"Status", ["Open", "Closed", "Restricted"], key=f"gate_status_{i}")
    with col3:
        crowd = st.slider(f"Crowd %", 0, 100, 45, key=f"gate_crowd_{i}")
    with col4:
        if st.button("Update", key=f"gate_update_{i}"):
            st.success(f"✅ {gate} updated")

if st.button("📊 Back to Dashboard"):
    st.switch_page("pages/09_admin_dashboard.py")
