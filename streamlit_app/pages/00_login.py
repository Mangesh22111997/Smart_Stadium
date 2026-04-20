"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Login Page - Customer and Admin Portal Entry
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image
import time

st.set_page_config(page_title="Login - Smart Stadium", page_icon="🔐", layout="centered")

# Apply Background
add_background_image()

# Check if already logged in
if SessionManager.is_logged_in():
    st.success("✅ You're already logged in!")
    st.info(f"Logged in as: {SessionManager.get_username()}")
    if st.button("Return to Home"):
        st.switch_page("pages/02_home.py")
    st.stop()

st.markdown("# 🔐 Smart Stadium Login")
st.markdown("*Log in to your account*")
st.divider()

# Tabs for customer and admin login
tab1, tab2, tab3 = st.tabs(["👤 Customer Login", "👨‍💼 Admin Login", "🔒 Security Staff"])

api_client = get_api_client()

# ==================== CUSTOMER LOGIN ====================
with tab1:
    st.markdown("### Customer Portal")
    
    with st.form("customer_login_form"):
        username = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="cust_username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="cust_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("🔓 Login", use_container_width=True)
        with col2:
            st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit_btn:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                with st.spinner("🔄 Authenticating..."):
                    result = api_client.signin(username, password)
                
                if "user_id" in result:
                    # Login successful
                    SessionManager.login_user(
                        user_id=result.get("user_id"),
                        username=result.get("username"),
                        email=result.get("email"),
                        session_token=result.get("session_token"),
                        user_type="customer"
                    )
                    st.success("✅ Login successful!")
                    st.balloons()
                    time.sleep(1)
                    st.switch_page("pages/02_home.py")
                else:
                    st.error(f"❌ {result.get('detail', 'Login failed')}")
    
    st.markdown("---")
    st.markdown("### New to Smart Stadium?")
    if st.button("📋 Create Account", use_container_width=True, key="cust_signup_btn"):
        st.switch_page("pages/01_signup.py")
    
    with st.expander("📋 Demo Credentials"):
        st.markdown("""
        **Test Customer Accounts:**
        - Username: `customer_demo`
        - Password: `Customer@2026`
        
        Or create a new account!
        """)

# ==================== ADMIN LOGIN ====================
with tab2:
    st.markdown("### Admin Portal")
    
    with st.form("admin_login_form"):
        admin_username = st.text_input(
            "Admin Username",
            placeholder="Enter your admin username",
            key="admin_username"
        )
        admin_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="admin_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("🔓 Admin Login", use_container_width=True)
        with col2:
            st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit_btn:
            if not admin_username or not admin_password:
                st.error("❌ Please enter both username and password")
            else:
                with st.spinner("🔄 Authenticating admin..."):
                    result = api_client.admin_signin(admin_username, admin_password)
                
                if "admin_id" in result:
                    # Admin login successful
                    SessionManager.login_admin(
                        admin_id=result.get("admin_id"),
                        username=result.get("username"),
                        email=result.get("email"),
                        session_token=result.get("session_token"),
                        admin_type=result.get("admin_type"),
                        permissions=result.get("permissions", {})
                    )
                    st.success("✅ Admin login successful!")
                    st.balloons()
                    time.sleep(1)
                    st.switch_page("pages/09_admin_dashboard.py")
                else:
                    st.error(f"❌ {result.get('detail', 'Login failed')}")
    
    st.markdown("---")
    st.warning("⚠️ Only authorized administrators can access this portal")
    
    with st.expander("📋 Demo Admin Credentials"):
        st.markdown("""
        **Super Admin:**
        - Username: `admin_super`
        - Password: `AdminPass@2026`
        
        **Events Admin:**
        - Username: `admin_events`
        - Password: `EventsAdmin@2026`
        
        **Ops Admin:**
        - Username: `admin_ops`
        - Password: `OpsAdmin@2026`
        
        📖 Full credentials guide: See **ADMIN_CREDENTIALS.md**
        """)

# ==================== SECURITY STAFF LOGIN ====================
with tab3:
    st.markdown("### 🔒 Security Staff Portal")
    st.info("🔐 Access restricted to authorized security personnel only")
    
    if st.button("🔑 Go to Security Staff Login →", use_container_width=True):
        st.switch_page("pages/13_security_login.py")
    
    st.divider()
    
    with st.expander("📋 Test Credentials (For Demo)"):
        st.markdown("""
        **Entrance Gate Operator:**
        - Username: `security_gate1`
        - Password: `GateSecurity@2026`
        
        **Flow Coordinator:**
        - Username: `security_flow`
        - Password: `FlowCoordinator@2026`
        
        **Incident Manager:**
        - Username: `security_incident`  
        - Password: `IncidentMgr@2026`
        
        **Emergency Responder:**
        - Username: `security_emergency`
        - Password: `Emergency@2026`
        
        📖 Full credentials guide: See **ADMIN_CREDENTIALS.md**
        """)
    
    st.warning("🔒 All security activities are logged and monitored")

# Backend status check
st.divider()
with st.expander("🔧 System Status"):
    try:
        health = api_client.health_check()
        if health.get("status") == "healthy":
            st.success(f"✅ Backend: {health.get('database', 'Connected')}")
        else:
            st.warning(f"⚠️ Backend Status: {health.get('status', 'Unknown')}")
    except Exception as e:
        st.error(f"❌ Backend Connection Error: {str(e)}")
