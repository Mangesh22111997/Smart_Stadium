# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



"""
Smart Stadium System - Main Streamlit Application
Multi-page portal for Customer, Admin, and Security
"""

import streamlit as st
st.set_page_config(
    page_title="🏟️ Smart Stadium System",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.session_manager import SessionManager
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts
from utils.i18n import language_selector
import os

# Initialize session
SessionManager.init_session()

# Apply Global Language Selector
language_selector()

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()

# Header
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("# 🏟️ Smart Stadium System")
    st.markdown("*Your premier event management platform*")

with col2:
    if SessionManager.is_logged_in():
        st.info(f"👤 {SessionManager.get_username()}", icon="✅")

st.divider()

# Main landing content
st.info("👋 Welcome! Use the sidebar to navigate through the system.")

st.markdown("""
### 🚀 Key Features:
*   **Smart Ticketing**: AI-driven gate assignments to avoid crowds.
*   **Predictive Analytics**: Real-time monitoring of stadium congestion.
*   **Food Ordering**: Skip the line with our intelligent booth allocation.
*   **Emergency SOS**: Instant response coordination for a safe experience.
""")

# Footer
st.markdown("""
---
<div style='text-align: center'>
    <p>🏟️ Smart Stadium System | Building a Smarter Event Experience</p>
    <p style='font-size: 12px; color: gray;'>Version 1.0 | Firebase Backend | Real-time Crowd Analytics</p>
</div>
""", unsafe_allow_html=True)
