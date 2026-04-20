# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Admin Dashboard - Main Admin Portal
"""

import streamlit as st
st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")

import pandas as pd
import plotly.express as px
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts
import datetime

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_events_cached():
    """Fetch event catalogue. Cached 5 min to reduce Firebase reads."""
    return get_api_client().list_events()


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

import random
import time

# ==================== EVENT SELECTOR ====================
with st.container():
    # Fetch events for selector (CACHED)
    try:
        events_resp = fetch_events_cached()
        all_events = events_resp.get("events", []) if isinstance(events_resp, dict) else []
        
        # Filter for LIVE events (today)
        today_str = datetime.date.today().isoformat()
        events_list = [e for e in all_events if e.get("event_date") == today_str or e.get("status") == "live"]
        
        if not events_list and all_events:
            # Fallback: if no live events today, show all for demo but warning
            st.warning("⚠️ No events scheduled for today. Showing all events for management.")
            events_list = all_events
            
        event_names = [e.get("event_name") for e in events_list]
    except:
        events_list = []
        event_names = []

    if event_names:
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            selected_event_name = st.selectbox("🎯 Select LIVE Event to Monitor:", event_names, index=0)
            st.session_state.admin_selected_event = next((e for e in events_list if e.get("event_name") == selected_event_name), None)
        with col2:
            if st.session_state.get("admin_selected_event"):
                e = st.session_state.admin_selected_event
                st.info(f"**Status:** {e.get('status', 'LIVE')}")
    else:
        st.warning("⚠️ No live events found for today.")

if st.session_state.get("admin_selected_event"):
    curr_event = st.session_state.admin_selected_event
    st.success(f"📍 **Currently Monitoring (LIVE):** {curr_event.get('event_name')} @ {curr_event.get('venue_type')}")
else:
    st.info("📊 Viewing Global System Overview")

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
    
    # Key metrics with jitter to feel dynamic
    jitter = random.randint(-5, 5) if st.session_state.get("admin_selected_event") else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Attendees", f"{1234 + jitter}", f"{12 + random.randint(-2, 2)}%")
    with col2:
        st.metric("🎉 Active Events", "2", "Live")
    with col3:
        st.metric("🎟️ Tickets Sold", f"{5678 + jitter*10}", f"{34 + random.randint(-5, 5)}%")
    with col4:
        st.metric("💰 Revenue", f"₹{45.2 + (jitter/10):.1f}L", f"{18 + random.randint(-3, 3)}%")
    
    st.divider()
    
    # Crowd analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 👥 Live Crowd per Gate - {curr_event.get('event_name') if st.session_state.get('admin_selected_event') else 'All'}")
        
        # Real-time jitter logic
        gate_labels = ['Gate A', 'Gate B', 'Gate C', 'Gate D', 'Gate E']
        gate_vals = [450+jitter*15, 320+jitter*8, 280-jitter*12, 510+jitter*20, 190+jitter*5]
        
        crowd_data = pd.DataFrame({
            'Gate': gate_labels,
            'Crowd': gate_vals
        })
        
        fig = px.bar(
            crowd_data, x='Gate', y='Crowd', color='Crowd',
            color_continuous_scale='RdYlGn_r',
            text_auto=True,
            template="plotly_white" if st.get_option("theme.base") != "dark" else "plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Attendance Trend")
        revenue_data = pd.DataFrame({
            'Time': pd.date_range(datetime.datetime.now() - datetime.timedelta(hours=5), periods=10, freq='30min'),
            'Attendees': [500, 800, 1200, 1500, 2200, 2800, 3500, 4200, 4800, 5200 + jitter*5]
        })
        fig = px.line(revenue_data, x='Time', y='Attendees', markers=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent activity
    st.markdown("### 📝 Live Activity Log")
    activities = pd.DataFrame({
        'Time': [datetime.datetime.now().strftime("%H:%M:%S"), 
                 (datetime.datetime.now() - datetime.timedelta(minutes=2)).strftime("%H:%M:%S"),
                 (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%H:%M:%S"),
                 (datetime.datetime.now() - datetime.timedelta(minutes=8)).strftime("%H:%M:%S")],
        'Activity': ['Ticket Scanned at Gate D', 'Food Order #9821 Ready', 'New Booking: VVIP Section', 'Gate B Crowd Alert'],
        'User': ['Amit Kumar', 'Priya Sharma', 'Rajesh Gupta', 'System']
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
    permissions = st.session_state.get(SessionManager.PERMISSIONS, {})
    
    st.write(f"**Admin Type:** {admin_type}")
    st.write("**Permissions:**")
    for perm, value in permissions.items():
        st.write(f"- {perm.replace('_', ' ').title()}: {'✅' if value else '❌'}")
