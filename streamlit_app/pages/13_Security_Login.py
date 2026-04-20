"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Security Staff Login Page
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Security Login - Smart Stadium", page_icon="🔐", layout="centered")

# Redirect if already logged in
if SessionManager.is_logged_in() and SessionManager.is_security():
    st.switch_page("pages/14_security_dashboard.py")

st.markdown("# 🔐 Security Staff Login")
st.markdown("*Access the security monitoring dashboard*")

st.divider()

# Login form
with st.form("security_login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    security_role = st.selectbox(
        "Select Your Role",
        ["Entrance Gate Operator", "Flow Coordinator", "Incident Manager", "Emergency Responder"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        login_button = st.form_submit_button("🔓 Login", use_container_width=True)
    with col2:
        back_button = st.form_submit_button("← Back", use_container_width=True)
    
    if login_button:
        if not username or not password:
            st.error("❌ Please fill in all fields")
        else:
            api_client = get_api_client()
            
            # Attempt security login with the new security endpoint
            response = api_client.security_signin(username, password)
            
            if "error" in response:
                st.error(f"❌ Login failed: {response.get('error')}")
            elif "session_token" not in response:
                st.error("❌ Invalid credentials")
            else:
                # Store session using login_security
                staff_id = response.get("staff_id")
                email = response.get("email")
                role = response.get("role")
                permissions = response.get("permissions", {})
                session_token = response.get("session_token")
                
                SessionManager.login_security(staff_id, username, email, session_token, role, permissions)
                
                st.success("✅ Login successful!")
                st.info(f"Welcome, {response.get('name', 'Staff')}!")
                st.balloons()
                
                st.switch_page("pages/14_security_dashboard.py")
    
    if back_button:
        st.switch_page("pages/00_login.py")

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    📞 Need help? Contact your supervisor or the main control room.
</div>
""", unsafe_allow_html=True)
