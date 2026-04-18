"""
Smart Stadium System - Main Streamlit Application
Multi-page portal for Customer, Admin, and Security
"""

import streamlit as st
from streamlit_option_menu import option_menu
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image
import base64
import os

# Page configuration
st.set_page_config(
    page_title="🏟️ Smart Stadium System",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session
SessionManager.init_session()

# Dynamic page configuration based on login status
if SessionManager.is_logged_in():
    if SessionManager.is_admin():
        pages = {
            "🏠 Home": "home",
            "📊 Dashboard": "dashboard",
            "🎉 Events": "events",
            "👥 Users": "users",
            "🚪 Gates": "gates",
            "🍔 Food": "food",
            "⚙️ Settings": "settings",
        }
    else:
        pages = {
            "🏠 Home": "home",
            "🎉 Events": "events",
            "🎟️ Bookings": "bookings",
            "🗺️ Maps": "maps",
            "🍔 Food": "food",
            "🔔 Notifications": "notifications",
        }
else:
    pages = {
        "🔐 Login": "login",
        "📋 Signup": "signup",
    }

# Apply Background Image
add_background_image()

# Header
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.markdown("# 🏟️ Smart Stadium System")
    st.markdown("*Your premier event management platform*")

with col2:
    if SessionManager.is_logged_in():
        st.info(f"👤 {SessionManager.get_username()}", icon="✅")

st.divider()

# Navigation
if pages:
    selected = option_menu(
        menu_title=None,
        options=list(pages.keys()),
        icons=["house", "list", "people", "gear"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0px", "background-color": "#f0f2f6"},
            "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px"},
            "nav-link-selected": {"background-color": "#667eea", "color": "white"},
        }
    )
    
    # Route to appropriate page
    page_map = {
        "🔐 Login": "1_Login",
        "📋 Signup": "2_Signup",
        "🏠 Home": "3_Home",
        "🎉 Events": "4_Events",
        "🎟️ Bookings": "5_Bookings",
        "🗺️ Maps": "6_Maps",
        "🍔 Food": "7_Food",
        "🔔 Notifications": "8_Notifications",
        "📊 Dashboard": "9_Admin_Dashboard",
        "👥 Users": "10_Users",
        "🚪 Gates": "11_Gates",
        "⚙️ Settings": "12_Settings",
        "🔒 Security Login": "13_Security_Login",
        "🚨 Security Dashboard": "14_Security_Dashboard",
        "🚀 Emergency Response": "15_Emergency_Response",
    }
    
    if selected in page_map:
        # Import the selected page dynamically using importlib
        import importlib.util
        import sys
        import os
        
        page_name = page_map[selected]
        page_path = os.path.join(os.path.dirname(__file__), "pages", f"{page_name}.py")
        
        if os.path.exists(page_path):
            spec = importlib.util.spec_from_file_location(page_name, page_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[page_name] = module
            spec.loader.exec_module(module)

st.divider()

# Footer
st.markdown("""
---
<div style='text-align: center'>
    <p>🏟️ Smart Stadium System | Building a Smarter Event Experience</p>
    <p style='font-size: 12px; color: gray;'>Version 1.0 | Firebase Backend | Real-time Crowd Analytics</p>
</div>
""", unsafe_allow_html=True)
