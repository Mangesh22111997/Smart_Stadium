"""
Smart Stadium System - Main Streamlit Application
Multi-page portal for Customer, Admin, and Security
"""

import streamlit as st
from streamlit_option_menu import option_menu
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

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

# Custom CSS
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .main {
        background: transparent;
    }
    .stContainer {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin: 20px auto;
        max-width: 1200px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

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
        "🔐 Login": "pages/1_Login",
        "📋 Signup": "pages/2_Signup",
        "🏠 Home": "pages/3_Home",
        "🎉 Events": "pages/4_Events",
        "🎟️ Bookings": "pages/5_Bookings",
        "🗺️ Maps": "pages/6_Maps",
        "🍔 Food": "pages/7_Food",
        "🔔 Notifications": "pages/8_Notifications",
        "📊 Dashboard": "pages/9_Admin_Dashboard",
        "👥 Users": "pages/10_Users",
        "🚪 Gates": "pages/11_Gates",
        "⚙️ Settings": "pages/12_Settings",
    }
    
    if selected in page_map:
        # Import the selected page
        selected_page = __import__(page_map[selected].replace("/", ".").replace("pages.", ""), fromlist=[""])
        # This will be handled by Streamlit's built-in multipage routing

st.divider()

# Footer
st.markdown("""
---
<div style='text-align: center'>
    <p>🏟️ Smart Stadium System | Building a Smarter Event Experience</p>
    <p style='font-size: 12px; color: gray;'>Version 1.0 | Firebase Backend | Real-time Crowd Analytics</p>
</div>
""", unsafe_allow_html=True)
