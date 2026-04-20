"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Admin Dashboard - Main Admin Portal
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
import datetime

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

# Check if logged in and is admin
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

if not SessionManager.is_admin():
    st.error("❌ Admin access required")
    st.switch_page("pages/02_home.py")
    st.stop()

api_client = get_api_client()

# Header with logout
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.markdown(f"# 📊 Admin Dashboard")
    st.markdown(f"Admin: {SessionManager.get_username()} | Type: {SessionManager.get_admin_type().title()}")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        api_client.logout(SessionManager.get_session_token())
        SessionManager.logout()
        st.switch_page("pages/00_login.py")

st.divider()

# Navigation tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🎉 Events",
    "👥 Users",
    "🚪 Gates",
    "⚙️ Settings"
])

# ==================== DASHBOARD TAB ====================
with tab1:
    st.markdown("## 📊 Overview Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", "1,234", "+12%")
    with col2:
        st.metric("🎉 Active Events", "8", "+2")
    with col3:
        st.metric("🎟️ Tickets Sold", "5,678", "+34%")
    with col4:
        st.metric("💰 Revenue", "₹45.2L", "+18%")
    
    st.divider()
    
    # Crowd analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Crowd per Gate")
        crowd_data = pd.DataFrame({
            'Gate': ['Gate A', 'Gate B', 'Gate C', 'Gate D', 'Gate E'],
            'Crowd': [450, 320, 280, 510, 190]
        })
        fig = px.bar(crowd_data, x='Gate', y='Crowd', color='Crowd',
                     color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Revenue Trend")
        revenue_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=30),
            'Revenue': [1000 + i*50 for i in range(30)]
        })
        fig = px.line(revenue_data, x='Date', y='Revenue', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent activity
    st.markdown("### 📝 Recent Activity")
    activities = pd.DataFrame({
        'Time': ['14:30', '14:15', '14:00', '13:45'],
        'Activity': ['User Booked Ticket', 'Food Order Placed', 'Emergency SOS', 'Gate Alert Issued'],
        'User': ['john_doe', 'jane_smith', 'admin_user', 'System']
    })
    st.table(activities)

# ==================== EVENTS TAB ====================
with tab2:
    st.markdown("## 🎉 Event Management")
    
    # Create new event
    if st.button("➕ Create New Event", use_container_width=True, key="create_event_btn"):
        st.session_state["show_event_form"] = True
    
    if st.session_state.get("show_event_form", False):
        st.markdown("### Create Event")
        with st.form("create_event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                event_name = st.text_input("Event Name *")
                event_date = st.date_input("Event Date")
                start_time = st.time_input("Start Time")
            
            with col2:
                end_time = st.time_input("End Time")
                venue_type = st.selectbox("Venue Type", ["Stadium", "Auditorium", "Hall"])
                seating_capacity = st.number_input("Seating Capacity", min_value=100, step=100)
            
            num_gates = st.number_input("Number of Gates", min_value=1, max_value=10)
            parking_available = st.checkbox("Parking Available")
            parking_capacity = st.number_input("Parking Capacity", min_value=0, step=10)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Create Event", use_container_width=True):
                    st.success("✅ Event created successfully!")
                    st.session_state["show_event_form"] = False
            with col2:
                st.form_submit_button("❌ Cancel", use_container_width=True)
    
    st.divider()
    
    # List events
    st.markdown("### Active Events")
    events_df = pd.DataFrame({
        'Event Name': ['Cricket Tournament', 'Music Festival', 'Tech Conference'],
        'Date': ['2024-06-15', '2024-07-20', '2024-08-10'],
        'Capacity': [5000, 8000, 1500],
        'Booked': [2300, 3400, 450],
        'Status': ['Active', 'Active', 'Scheduled']
    })
    st.dataframe(events_df, use_container_width=True)

# ==================== USERS TAB ====================
with tab3:
    st.markdown("## 👥 User Management")
    
    # Fetch users from backend
    with st.spinner("📋 Loading users..."):
        users_response = api_client.get_all_users(SessionManager.get_session_token())
    
    if "users" in users_response:
        users_df = pd.DataFrame(users_response.get("users", []))
        st.dataframe(users_df, use_container_width=True)
    elif "detail" in users_response:
        st.error(f"❌ {users_response.get('detail')}")
    else:
        st.info("No users found or backend unavailable")

# ==================== GATES TAB ====================
with tab4:
    st.markdown("## 🚪 Gate Management")
    
    col1, col2, col3 = st.columns(3)
    
    gates = ['Gate A', 'Gate B', 'Gate C', 'Gate D', 'Gate E']
    
    for i, gate in enumerate(gates):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"### {gate}")
            status = st.selectbox(f"Status - {gate}", ["Open", "Closed", "Restricted"], key=f"gate_{i}")
            crowd = st.slider(f"Crowd %", 0, 100, 45, key=f"crowd_{i}")
            
            if st.button(f"Update {gate}", use_container_width=True, key=f"update_{i}"):
                st.success(f"✅ {gate} updated")

# ==================== SETTINGS TAB ====================
with tab5:
    st.markdown("## ⚙️ Admin Settings")
    
    st.markdown("### Permissions")
    admin_type = SessionManager.get_admin_type()
    permissions = SessionManager._session_state.get(SessionManager.PERMISSIONS, {})
    
    st.write(f"**Admin Type:** {admin_type}")
    st.write("**Permissions:**")
    for perm, value in permissions.items():
        st.write(f"- {perm.replace('_', ' ').title()}: {'✅' if value else '❌'}")
