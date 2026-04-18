"""
Smart Stadium System - Streamlit Frontend
Main entry point with multi-page navigation & Authentication
"""

import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json
from datetime import datetime
from auth_utils import (
    customer_signup, 
    customer_signin, 
    admin_signin,
    get_all_users_count,
    get_all_admins_count
)

# Page configuration
st.set_page_config(
    page_title="Smart Stadium System",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .main {
        padding: 0px 0px;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    .header-title {
        font-size: 28px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .header-buttons {
        display: flex;
        gap: 10px;
    }
    
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-label {
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
        display: block;
    }
    
    .form-input {
        width: 100%;
        padding: 12px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 16px;
        transition: border-color 0.3s;
    }
    
    .form-input:focus {
        border-color: #667eea;
        outline: none;
    }
    
    .submit-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
        width: 100%;
    }
    
    .submit-btn:hover {
        transform: translateY(-2px);
    }
    
    .divider {
        text-align: center;
        margin: 30px 0;
        color: #999;
    }
    
    .admin-section {
        background: #fff3cd;
        border-left: 5px solid #ff9800;
        padding: 30px;
        border-radius: 10px;
        margin-top: 50px;
    }
    
    .admin-warning {
        color: #ff6b35;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .admin-form {
        background: white;
        padding: 20px;
        border-radius: 8px;
    }
    
    .feature-section {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 40px;
    }
    
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #667eea;
    }
    
    .feature-icon {
        font-size: 40px;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-weight: 700;
        font-size: 18px;
        color: #333;
        margin-bottom: 10px;
    }
    
    .feature-description {
        color: #666;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    
    .status-active {
        color: #00cc44;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ff9800;
        font-weight: bold;
    }
    
    .status-critical {
        color: #ff4444;
        font-weight: bold;
    }
    
    .tab-button {
        background: none;
        border: none;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        border-bottom: 3px solid transparent;
        color: #999;
        transition: all 0.3s;
    }
    
    .tab-button.active {
        color: #667eea;
        border-bottom-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = f"{API_BASE_URL}/api/v1/orchestration"

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    # Check backend
    backend_status = check_backend()
    
    if not backend_status:
        # Show error page if backend is down
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error("⚠️ **Backend Server Unavailable**")
            st.markdown("""
            The Smart Stadium backend is not running. 
            Please ensure the server is started at `http://127.0.0.1:8000`
            
            To start the backend:
            ```bash
            python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
            ```
            """)
        return
    
    # Initialize session state
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    
    # Show landing page or dashboard based on login state
    if not st.session_state.logged_in:
        show_landing_page()
    else:
        if st.session_state.user_type == "customer":
            show_customer_dashboard()
        elif st.session_state.user_type == "admin":
            show_admin_dashboard()

def show_landing_page():
    """Show landing page with professional login UI"""
    
    # ============================================================================
    # HEADER WITH LOGO AND LOGIN BUTTONS
    # ============================================================================
    
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px;'>
            <span style='font-size: 36px;'>🏟️</span>
            <span style='font-size: 20px; font-weight: bold; color: #0066cc;'>Smart Stadium</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        col_signin, col_signup = st.columns(2)
        with col_signin:
            if st.button("🔐 Sign In", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()
        with col_signup:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
    
    st.markdown("---")
    
    # ============================================================================
    # HERO SECTION
    # ============================================================================
    
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px;'>
        <h1 style='color: #333; font-size: 48px; margin-bottom: 15px;'>
            Welcome to Smart Stadium
        </h1>
        <p style='color: #666; font-size: 20px; margin-bottom: 30px;'>
            Real-time Crowd Management, Gate Operations & Emergency Response Platform
        </p>
        <p style='color: #999; font-size: 16px;'>
            Track your event journey in real-time with instant updates and smart routing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # MAIN LOGIN / SIGNUP SECTION
    # ============================================================================
    
    col1_main, col2_main = st.columns([1, 2])
    
    with col2_main:
        # Login Form
        if not st.session_state.show_signup:
            st.markdown("""
            <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
                <h2 style='color: #333; margin-bottom: 30px; text-align: center;'>👤 Customer Login</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("customer_login"):
                email = st.text_input(
                    "📧 Email Address",
                    placeholder="john.doe@example.com",
                    help="Enter your registered email address"
                )
                password = st.text_input(
                    "🔐 Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Your secure password"
                )
                
                st.markdown("---")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button(
                        "✓ Login",
                        use_container_width=True,
                        type="primary"
                    )
                with col_btn2:
                    st.form_submit_button(
                        "Clear Form",
                        use_container_width=True,
                        type="secondary"
                    )
                
                if submitted:
                    if email and password:
                        success, message, user_data = customer_signin(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_type = "customer"
                            st.session_state.user_email = user_data['email']
                            st.session_state.user_id = user_data['user_id']
                            st.session_state.user_name = user_data['name']
                            st.success(f"✓ Welcome {user_data['name']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please fill in all fields")
        
        # Sign Up Form
        else:
            st.markdown("""
            <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
                <h2 style='color: #333; margin-bottom: 30px; text-align: center;'>📝 Create Your Account</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("customer_signup"):
                name = st.text_input(
                    "👤 Full Name",
                    placeholder="Rajesh Kumar"
                )
                email = st.text_input(
                    "📧 Email Address",
                    placeholder="rajesh@example.com"
                )
                phone = st.text_input(
                    "📱 Phone Number",
                    placeholder="+91-9876543210"
                )
                password = st.text_input(
                    "🔐 Password",
                    type="password",
                    placeholder="Enter a strong password (min 6 characters)"
                )
                confirm_password = st.text_input(
                    "🔐 Confirm Password",
                    type="password",
                    placeholder="Re-enter your password"
                )
                
                agree_tc = st.checkbox("I agree to Terms & Conditions")
                
                st.markdown("---")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button(
                        "✓ Create Account",
                        use_container_width=True,
                        type="primary"
                    )
                with col_btn2:
                    st.form_submit_button(
                        "Clear Form",
                        use_container_width=True,
                        type="secondary"
                    )
                
                if submitted:
                    if all([name, email, phone, password, confirm_password, agree_tc]):
                        if password == confirm_password:
                            success, message = customer_signup(name, email, phone, password)
                            if success:
                                st.success(f"✓ {message}")
                                st.info("📧 You can now sign in with your credentials!")
                                st.session_state.show_signup = False
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.error("❌ Please fill in all fields and agree to T&C")
    
    with col1_main:
        # Features list on the side
        st.markdown("""
        <div style='background: #f8f9fa; padding: 30px; border-radius: 15px; height: 100%;'>
            <h3 style='color: #333; margin-bottom: 20px;'>✨ Customer Features</h3>
            
            <div style='margin-bottom: 15px;'>
                <p style='margin: 0; color: #667eea; font-weight: 600;'>🎯 Smart Gate Assignment</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; color: #666;'>Optimal route based on preferences</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <p style='margin: 0; color: #667eea; font-weight: 600;'>⏱️ Entry Time Estimate</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; color: #666;'>Real-time queue predictions</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <p style='margin: 0; color: #667eea; font-weight: 600;'>🍔 Food Ordering</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; color: #666;'>Order ahead for convenience</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <p style='margin: 0; color: #667eea; font-weight: 600;'>📱 Live Notifications</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; color: #666;'>Real-time updates & alerts</p>
            </div>
            
            <div style='margin-bottom: 15px;'>
                <p style='margin: 0; color: #667eea; font-weight: 600;'>🗺️ Journey Tracking</p>
                <p style='margin: 5px 0 0 0; font-size: 14px; color: #666;'>View your complete event timeline</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # FEATURES SHOWCASE
    # ============================================================================
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style='text-align: center; color: #333; margin-bottom: 40px;'>Why Choose Smart Stadium?</h2>
    """, unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div style='background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-top: 4px solid #667eea;'>
            <p style='font-size: 40px; margin-bottom: 15px;'>⚡</p>
            <p style='font-weight: 700; font-size: 18px; color: #333; margin-bottom: 10px;'>Real-Time Updates</p>
            <p style='color: #666; font-size: 14px; line-height: 1.6;'>Get instant notifications about gate assignments and queue status.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div style='background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-top: 4px solid #764ba2;'>
            <p style='font-size: 40px; margin-bottom: 15px;'>🎯</p>
            <p style='font-weight: 700; font-size: 18px; color: #333; margin-bottom: 10px;'>Smart Routing</p>
            <p style='color: #666; font-size: 14px; line-height: 1.6;'>AI-optimized routing reduces wait times and crowds.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div style='background: white; padding: 25px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-top: 4px solid #ff6b6b;'>
            <p style='font-size: 40px; margin-bottom: 15px;'>🔒</p>
            <p style='font-weight: 700; font-size: 18px; color: #333; margin-bottom: 10px;'>Safe & Secure</p>
            <p style='color: #666; font-size: 14px; line-height: 1.6;'>Emergency response and crowd safety monitoring.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================================
    # ADMIN LOGIN SECTION - BOTTOM WITH WARNING
    # ============================================================================
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: #fff3cd; border-left: 5px solid #ff9800; padding: 30px; border-radius: 10px; margin-bottom: 30px;'>
        <div style='color: #ff6b35; font-weight: bold; font-size: 20px; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;'>
            <span>⚠️ ADMIN ACCESS ONLY</span>
        </div>
        <p style='color: #333; margin: 10px 0;'>
            <strong>⛔ Restricted Area:</strong> This section is exclusively for authorized staff members and administrators. 
            Unauthorized access attempts are monitored and logged.
        </p>
        <p style='color: #666; margin: 10px 0; font-size: 14px;'>
            • For staff management access<br>
            • For emergency operations<br>
            • For analytics and reporting
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin Login Form
    with st.expander("👮 Admin / Staff Portal", expanded=False):
        ad_col1, ad_col2 = st.columns([2, 1])
        
        with ad_col1:
            with st.form("admin_login"):
                staff_id = st.text_input(
                    "Staff ID",
                    placeholder="STAFF-001",
                    help="Your authorized staff identifier"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    help="Your secure staff password"
                )
                
                st.markdown("---")
                
                col_admin_btn1, col_admin_btn2 = st.columns(2)
                with col_admin_btn1:
                    admin_submit = st.form_submit_button(
                        "✓ Login as Admin",
                        use_container_width=True,
                        type="primary"
                    )
                with col_admin_btn2:
                    st.form_submit_button(
                        "Clear",
                        use_container_width=True,
                        type="secondary"
                    )
                
                if admin_submit:
                    if staff_id and password:
                        success, message, admin_data = admin_signin(staff_id, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_type = "admin"
                            st.session_state.user_email = admin_data['email']
                            st.session_state.user_id = admin_data['staff_id']
                            st.session_state.user_name = admin_data['name']
                            st.success(f"✓ Welcome {admin_data['name']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please enter staff ID and password")
        
        with ad_col2:
            st.markdown("""
            <div style='background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 10px;'>
                <p style='color: #ff6b35; font-weight: bold; margin: 0 0 10px 0;'>🔒 Demo Credentials</p>
                <p style='margin: 0; font-size: 13px;'><strong>Staff ID:</strong> STAFF-001</p>
                <p style='margin: 5px 0; font-size: 13px;'><strong>Password:</strong> staff123</p>
                <p style='margin: 10px 0 0 0; font-size: 12px; color: #666;'>Or use: STAFF-002 / admin456</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================================
    # FOOTER WITH STATS
    # ============================================================================
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        registered_users = get_all_users_count()
        st.metric("👥 Registered Users", registered_users, "Active")
    
    with col2:
        st.metric("📊 Total Events", "156", "This Month")
    
    with col3:
        st.metric("🚪 Total Gates", "12", "Operational")
    
    with col4:
        system_health = "99.2%"
        st.metric("💚 System Health", system_health, "Excellent")

def show_customer_dashboard():
    """Show customer-facing dashboard"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.caption(f"📧 {st.session_state.user_email}")
        st.caption(f"🆔 {st.session_state.user_id}")
        
        selected_page = option_menu(
            menu_title="Customer Menu",
            options=["My Journey", "Gate Info", "Food Ordering", "Notifications", "Alerts"],
            icons=["map", "door-open", "cup-straw", "bell", "exclamation-triangle"],
            menu_icon="list",
            default_index=0
        )
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_name = None
            st.rerun()
    
    # Main content
    if selected_page == "My Journey":
        show_customer_journey()
    elif selected_page == "Gate Info":
        show_gate_info()
    elif selected_page == "Food Ordering":
        show_food_ordering()
    elif selected_page == "Notifications":
        show_notifications()
    elif selected_page == "Alerts":
        show_emergency_alerts()

def show_admin_dashboard():
    """Show admin/staff dashboard"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👮 {st.session_state.user_name}")
        st.caption(f"📧 {st.session_state.user_email}")
        st.caption(f"🆔 {st.session_state.user_id}")
        
        selected_page = option_menu(
            menu_title="Admin Menu",
            options=["Dashboard", "Crowd Monitor", "Users", "Emergencies", "Analytics", "Settings"],
            icons=["graph-up", "people-fill", "person-lines-fill", "fire", "bar-chart", "gear"],
            menu_icon="shield-lock",
            default_index=0
        )
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_name = None
            st.rerun()
    
    # Main content
    if selected_page == "Dashboard":
        show_admin_dashboard_main()
    elif selected_page == "Crowd Monitor":
        show_crowd_monitor()
    elif selected_page == "Users":
        show_user_management()
    elif selected_page == "Emergencies":
        show_emergency_management()
    elif selected_page == "Analytics":
        show_admin_analytics()
    elif selected_page == "Settings":
        show_settings()

# ============================================================================
# CUSTOMER PAGES
# ============================================================================

def show_customer_journey():
    """Show user's current journey status"""
    st.markdown("## 📍 My Journey Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "Ready to Enter ✓", "On Time")
    with col2:
        st.metric("Assigned Gate", "Gate-A", "Capacity: 67%")
    with col3:
        st.metric("Entry Time", "15 mins", "Wait time")
    
    st.divider()
    
    # Journey details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Booking Details")
        st.markdown(f"""
        - **Name**: {st.session_state.user_name}
        - **Email**: {st.session_state.user_email}
        - **User ID**: {st.session_state.user_id}
        - **Phone**: Available in Profile
        - **Event**: Soccer Match - Finals
        - **Date**: 2024-12-20
        - **Arrival Time**: 14:30
        - **Commute Mode**: Drive
        - **Parking**: Yes
        """)
    
    with col2:
        st.markdown("### 🚪 Gate Assignment")
        st.markdown("""
        - **Gate**: Gate-A (Main Entrance)
        - **Current Capacity**: 67% (800/1200)
        - **Estimated Wait**: 15 minutes
        - **Alternative Gates**: Gate-B (45%), Gate-D (52%)
        - **Last Updated**: 2 minutes ago
        - **Status**: ✓ Optimized
        """)
    
    st.divider()
    
    # Journey events
    st.markdown("### 📝 Journey Timeline")
    
    events = [
        {"time": "14:15", "event": "Ticket Booked", "status": "✓"},
        {"time": "14:20", "event": "Gate Assignment", "status": "✓"},
        {"time": "14:22", "event": "Notification Sent", "status": "✓"},
        {"time": "14:25", "event": "Estimated Entry", "status": "⏱"},
    ]
    
    for event in events:
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.markdown(f"**{event['time']}**")
        with col2:
            st.markdown(event['event'])
        with col3:
            st.markdown(f"<span class='{'status-active' if event['status'] == '✓' else 'status-warning'}'>{event['status']}</span>", unsafe_allow_html=True)

def show_gate_info():
    """Show gate information and real-time status"""
    st.markdown("## 🚪 Gate Information")
    
    import plotly.express as px
    
    # Gate utilization chart
    gates_data = {
        "Gate": ["Gate-A", "Gate-B", "Gate-C", "Gate-D", "Gate-E"],
        "Capacity": [67, 45, 82, 52, 38],
        "Users": [800, 540, 985, 625, 456]
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(gates_data, x="Gate", y="Capacity", title="Gate Utilization (%)", 
                     color="Capacity", color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Your Gate (Gate-A)")
        st.progress(67/100)
        st.markdown(f"""
        - **Capacity**: 67% (800/1200)
        - **Status**: ⚠️ MEDIUM
        - **Wait Time**: 15 mins
        - **Avg Processing**: 5 mins/user
        """)
    
    st.divider()
    
    # Gate details table
    st.markdown("### 🏢 All Gates Status")
    
    gates_info = {
        "Gate": ["Gate-A", "Gate-B", "Gate-C", "Gate-D", "Gate-E"],
        "Status": ["OPEN", "OPEN", "CROWDED", "OPEN", "OPEN"],
        "Users": [800, 540, 985, 625, 456],
        "Capacity": [1200, 1200, 1200, 1200, 1200],
        "Utilization": ["67%", "45%", "82%", "52%", "38%"],
        "Wait Time": ["15 min", "8 min", "22 min", "10 min", "5 min"]
    }
    
    st.dataframe(gates_info, use_container_width=True, hide_index=True)

def show_food_ordering():
    """Show food ordering interface"""
    st.markdown("## 🍔 Food Ordering")
    
    # Food menu
    col1, col2, col3 = st.columns(3)
    
    food_items = [
        {"name": "Margherita Pizza", "price": 250, "emoji": "🍕"},
        {"name": "Burger", "price": 150, "emoji": "🍔"},
        {"name": "Fries", "price": 80, "emoji": "🍟"},
        {"name": "Soft Drink", "price": 50, "emoji": "🥤"},
        {"name": "Popcorn", "price": 100, "emoji": "🍿"},
        {"name": "Ice Cream", "price": 60, "emoji": "🍦"},
    ]
    
    order_items = []
    
    for i, item in enumerate(food_items):
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3
        
        with col:
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;'>
                <p style='font-size: 40px;'>{item['emoji']}</p>
                <p style='font-weight: bold;'>{item['name']}</p>
                <p>₹{item['price']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            qty = st.number_input(
                f"Qty - {item['name']}", 
                min_value=0, 
                max_value=5, 
                value=0,
                key=f"qty_{item['name']}"
            )
            
            if qty > 0:
                order_items.append({"item": item["name"], "qty": qty, "price": item["price"]})
    
    st.divider()
    
    # Order summary
    if order_items:
        st.markdown("### 📋 Order Summary")
        
        total = 0
        for order in order_items:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(order["item"])
            with col2:
                st.markdown(f"x {order['qty']}")
            with col3:
                st.markdown(f"₹{order['price']}")
            with col4:
                st.markdown(f"₹{order['price'] * order['qty']}")
            total += order['price'] * order['qty']
        
        st.divider()
        st.metric("Total Amount", f"₹{total}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Place Order", use_container_width=True, type="primary"):
                st.success(f"✓ Order placed! Total: ₹{total}")
                st.markdown("Pick up from **Booth-03** in 15 minutes")
        with col2:
            st.button("Cancel", use_container_width=True)
    else:
        st.info("👆 Select items to place an order")

def show_notifications():
    """Show notifications"""
    st.markdown("## 🔔 Notifications")
    
    notifications = [
        {"type": "info", "title": "Gate Assignment", "message": "You have been assigned to Gate-A", "time": "5 min ago"},
        {"type": "success", "title": "Entry Permission", "message": "You can proceed to enter now", "time": "3 min ago"},
        {"type": "info", "title": "Food Ready", "message": "Your food order is ready at Booth-03", "time": "2 min ago"},
    ]
    
    for notif in notifications:
        icon = "ℹ️" if notif["type"] == "info" else "✓"
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
            <p><strong>{icon} {notif['title']}</strong></p>
            <p>{notif['message']}</p>
            <p style='color: gray; font-size: 12px;'>{notif['time']}</p>
        </div>
        """, unsafe_allow_html=True)

def show_emergency_alerts():
    """Show emergency alerts"""
    st.markdown("## ⚠️ Emergency Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Current Status")
        st.success("**No Active Emergencies**")
        st.markdown("Your area is safe. Continue enjoying the event.")
    
    with col2:
        st.markdown("### 📍 Nearby Exits")
        st.markdown("""
        - **Exit-3** (45m away)
        - **Exit-5** (60m away)  
        - **Exit-1** (85m away)
        """)
    
    st.divider()
    
    st.markdown("### 🆘 Emergency Contact")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 Call Staff", use_container_width=True):
            st.info("Staff has been notified. Help arriving soon.")
    with col2:
        if st.button("🚨 Emergency SOS", use_container_width=True, type="secondary"):
            st.error("🚨 Emergency triggered! Authorities have been notified.")

# ============================================================================
# ADMIN/STAFF PAGES
# ============================================================================

def show_admin_dashboard_main():
    """Show main admin dashboard"""
    st.markdown("## 📊 System Overview")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "4,850", "+120 this hour")
    with col2:
        st.metric("Active Gates", "12/12", "All operational")
    with col3:
        st.metric("Avg Wait Time", "18 min", "-2 min")
    with col4:
        st.metric("System Health", "99.2%", "+0.8%")
    
    st.divider()
    
    # Charts
    import plotly.graph_objects as go
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Crowd over time
        st.markdown("### 📈 Crowd Level Over Time")
        times = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00"]
        users = [800, 1200, 1600, 2100, 2800, 3500, 4200]
        
        fig = go.Figure(data=go.Scatter(x=times, y=users, mode='lines+markers'))
        fig.update_layout(title="Users in Stadium", xaxis_title="Time", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gate utilization
        st.markdown("### 🚪 Gate Utilization")
        gates = ["A", "B", "C", "D", "E"]
        utilization = [67, 45, 82, 52, 38]
        
        fig = go.Figure(data=go.Bar(x=gates, y=utilization, marker_color=["#ff4444" if u > 80 else "#ff9800" if u > 60 else "#00cc44" for u in utilization]))
        fig.update_layout(title="Gate Capacity (%)", xaxis_title="Gate", yaxis_title="Utilization %")
        st.plotly_chart(fig, use_container_width=True)

def show_crowd_monitor():
    """Show real-time crowd monitoring"""
    st.markdown("## 👥 Real-Time Crowd Monitoring")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🎯 Gate Status")
        
        gates = [
            {"gate": "A", "capacity": 67, "users": 800},
            {"gate": "B", "capacity": 45, "users": 540},
            {"gate": "C", "capacity": 82, "users": 985},
            {"gate": "D", "capacity": 52, "users": 625},
            {"gate": "E", "capacity": 38, "users": 456},
        ]
        
        for gate in gates:
            color = "🔴" if gate["capacity"] > 80 else "🟡" if gate["capacity"] > 60 else "🟢"
            st.markdown(f"{color} **Gate-{gate['gate']}**: {gate['users']}/{1200} ({gate['capacity']}%)")
            st.progress(gate["capacity"]/100)
    
    with col2:
        st.markdown("### ⚠️ Alerts")
        st.error("Gate-C Overcrowded")
        st.warning("Move users to Gate-B")
    
    with col3:
        st.markdown("### ⚡ Actions")
        if st.button("🔄 Redistribute Users"):
            st.success("Redistribution started")

def show_user_management():
    """Show user management interface"""
    st.markdown("## 👥 User Management")
    
    tab1, tab2, tab3 = st.tabs(["View Users", "Reassign", "Actions"])
    
    with tab1:
        st.markdown("### 📋 Active Users")
        
        users_data = {
            "User ID": ["U001", "U002", "U003", "U004"],
            "Name": ["Rahul Sharma", "Priya Singh", "Amit Kumar", "Neha Patel"],
            "Gate": ["A", "C", "B", "D"],
            "Status": ["✓ Entered", "⏳ In Queue", "✓ Entered", "⏳ In Queue"],
            "Time": ["10:25", "10:45", "10:30", "10:50"]
        }
        
        st.dataframe(users_data, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### 🔄 Reassign User")
        user_id = st.text_input("User ID to Reassign")
        new_gate = st.selectbox("New Gate", ["Gate-A", "Gate-B", "Gate-D", "Gate-E"])
        
        if st.button("Confirm Reassignment", use_container_width=True, type="primary"):
            st.success(f"✓ User {user_id} reassigned to {new_gate}")
    
    with tab3:
        st.markdown("### ⚙️ Bulk Actions")
        action = st.selectbox("Select Action", ["Trigger Evacuation", "Send Alert", "Update Status"])
        
        if action == "Trigger Evacuation":
            location = st.selectbox("Location", ["Gate-A", "Gate-B", "Gate-C"])
            if st.button("Confirm", use_container_width=True):
                st.error(f"🚨 Evacuation initiated for {location}")

def show_emergency_management():
    """Show emergency management"""
    st.markdown("## 🚨 Emergency Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Active Emergencies")
        st.success("No active emergencies")
    
    with col2:
        st.markdown("### 📞 Quick Actions")
        if st.button("📢 Send Announcement"):
            st.info("Announcement sent to all zones")

def show_admin_analytics():
    """Show admin analytics"""
    st.markdown("## 📊 Analytics & Reports")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Performance", "Trends"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Daily Metrics")
            st.metric("Total Users", "4,850")
            st.metric("Food Orders", "420")
            st.metric("Avg Entry Time", "18 min")
        
        with col2:
            st.markdown("### ⚡ Performance")
            st.metric("System Uptime", "99.2%")
            st.metric("API Response Time", "145ms")
            st.metric("Alerts Triggered", "3")
    
    with tab2:
        st.markdown("### 🎯 Department Performance")
        st.bar_chart({"Gates": [90, 85, 92, 88], "Food": [75, 80, 78], "Emergency": [100, 100, 99]})
    
    with tab3:
        st.markdown("### 📊 Trends")
        st.line_chart({"Crowd": [100, 150, 200, 280, 300, 280, 250, 180], "Food Orders": [20, 35, 50, 65, 70, 60, 45, 30]})

def show_settings():
    """Show settings page"""
    st.markdown("## ⚙️ Settings")
    
    with st.expander("🔔 Alert Thresholds"):
        st.slider("Gate Overcrowding Alert (%)", 60, 90, 75)
        st.slider("Entry Time Threshold (min)", 10, 60, 30)
    
    with st.expander("📊 System Configuration"):
        st.number_input("Max Users per Gate", 1000, 2000, 1200)
        st.number_input("Emergency Response (sec)", 30, 300, 120)
    
    with st.expander("🔐 Security"):
        if st.button("Rotate API Keys"):
            st.success("✓ API keys rotated")

if __name__ == "__main__":
    main()
