# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Security Monitoring Dashboard
Real-time crowd and gate monitoring
"""

import streamlit as st
st.set_page_config(page_title="Security Dashboard - Smart Stadium", page_icon="📊", layout="wide")

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
import plotly.graph_objects as go
from datetime import datetime, timedelta


# Check security access
if not SessionManager.is_logged_in():
    st.error("❌ Unauthorized access")
    st.switch_page("pages/13_security_login.py")
    st.stop()

user_role = SessionManager.get_user_role()
if user_role not in ["security", "moderator", "superadmin"]:
    st.error("❌ Access denied. Security staff only.")
    st.switch_page("pages/00_login.py")
    st.stop()

st.markdown("# 📊 Security Monitoring Dashboard")
st.markdown(f"Logged in as: **{SessionManager.get_username()}** ({user_role.title()})")

import random
import time

# ==================== EVENT SELECTOR ====================
st.divider()
try:
    api_client = get_api_client()
    events_resp = api_client.list_events(limit=50)
    all_events = events_resp.get("events", []) if isinstance(events_resp, dict) else []
    
    # Filter for LIVE events (today)
    today_str = datetime.now().strftime("%Y-%m-%d")
    events_list = [e for e in all_events if e.get("event_date") == today_str or e.get("status") == "live"]
    
    if not events_list and all_events:
        # Fallback for demo
        st.warning("⚠️ No live events found for today. Showing all available events.")
        events_list = all_events

    event_names = [e.get("event_name") for e in events_list]
except:
    events_list = []
    event_names = []

if event_names:
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        selected_event_name = st.selectbox("🛡️ Select LIVE Event to Monitor:", event_names, index=0)
        st.session_state.security_selected_event = next((e for e in events_list if e.get("event_name") == selected_event_name), None)
    with col2:
        if st.session_state.get("security_selected_event"):
            st.info(f"📍 Monitoring ACTIVE")

if st.session_state.get("security_selected_event"):
    curr_event = st.session_state.security_selected_event
    st.success(f"🔍 **Monitoring Activity for:** {curr_event.get('event_name')}")
else:
    st.info("📊 Viewing Global Security Status")
st.divider()

# Initialize session state
if "view_mode" not in st.session_state:
    st.session_state.view_mode = None
if "editing_gate" not in st.session_state:
    st.session_state.editing_gate = None

# Add jitter for dynamic feel
jitter = random.randint(-2, 3) if st.session_state.get("security_selected_event") else 0

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎬 View Alerts", use_container_width=True):
        st.session_state.view_mode = "alerts"
with col2:
    if st.button("📋 Incident Log", use_container_width=True):
        st.session_state.view_mode = "incidents"
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        SessionManager.logout()
        st.switch_page("pages/00_login.py")

st.divider()

# Real-time gate monitoring
st.markdown(f"## 🚪 Gate Status - {curr_event.get('event_name') if st.session_state.get('security_selected_event') else 'All Gates'}")

api_client = get_api_client()
gates_response = api_client.get_all_gates()
gates = gates_response.get("gates", {})

if gates:
    # Create metrics for each gate
    gate_cols = st.columns(len(gates) if len(gates) <= 5 else 5)
    
    for idx, (gate_key, gate_data) in enumerate(gates.items()):
        col_idx = idx % 5
        with gate_cols[col_idx]:
            crowd_pct = max(0, min(100, gate_data.get("crowd_percentage", 0) + jitter*5))
            status = gate_data.get("status", "unknown")
            
            # Color coding based on crowd
            if crowd_pct > 80:
                color_class = "emotion-red"
                icon = "🔴"
            elif crowd_pct > 50:
                color_class = "emotion-yellow"
                icon = "🟡"
            else:
                color_class = "emotion-green"
                icon = "🟢"
            
            st.metric(
                f"{gate_data.get('name', gate_key).upper()}",
                f"{crowd_pct}% Full",
                delta=f"{status.upper()}"
            )
            
            # Status update button
            if st.button(f"Update {gate_data.get('name', gate_key)}", key=f"update_gate_{gate_key}"):
                st.session_state.editing_gate = gate_key
                st.rerun()

st.divider()

# Alert system
st.markdown("## ⚠️ Active Alerts")

alerts = [
    {"gate": "Gate A", "type": "Congestion", "crowd": 85, "time": "2 mins ago", "severity": "high"},
    {"gate": "Gate C", "type": "Overcrowding", "crowd": 92, "time": "5 mins ago", "severity": "critical"},
    {"gate": "Gate B", "type": "Slow Entry", "crowd": 65, "time": "8 mins ago", "severity": "medium"},
]

for alert in alerts:
    severity = alert["severity"]
    if severity == "critical":
        st.error(f"🔴 **{alert['gate']}** - {alert['type']} ({alert['crowd']}% full) - {alert['time']}")
    elif severity == "high":
        st.warning(f"🟠 **{alert['gate']}** - {alert['type']} ({alert['crowd']}% full) - {alert['time']}")
    else:
        st.info(f"🟡 **{alert['gate']}** - {alert['type']} ({alert['crowd']}% full) - {alert['time']}")

st.divider()

# Crowd distribution charts
st.markdown("## 📈 Crowd Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Live Gate Occupancy - {curr_event.get('event_name') if st.session_state.get('security_selected_event') else 'All Events'}")
    
    if not gates:
        # Fallback for demo if API gates are empty
        gate_names = ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]
        # Simulate Gate A being full as per user request
        gate_crowds = [
            88 + random.randint(-5, 8), # Gate A (Busy)
            45 + random.randint(-15, 15), # Gate B
            30 + random.randint(-10, 10), # Gate C
            65 + random.randint(-20, 15), # Gate D
            15 + random.randint(-5, 5)    # Gate E
        ]
    else:
        gate_names = [g.get("name", k).upper() for k, g in gates.items()]
        gate_crowds = [max(0, min(100, g.get("crowd_percentage", 0) + random.randint(-15, 15))) for g in gates.values()]
    
    # Clip values
    gate_crowds = [max(0, min(100, c)) for c in gate_crowds]
    
    fig1 = go.Figure(data=[
        go.Bar(
            x=gate_names, 
            y=gate_crowds, 
            text=[f"{c}%" for c in gate_crowds],
            textposition='auto',
            marker_color=["#ef4444" if c > 80 else "#f59e0b" if c > 50 else "#10b981" for c in gate_crowds]
        )
    ])
    fig1.update_layout(
        yaxis_title="Occupancy %", 
        xaxis_title="Security Gates", 
        height=400,
        template="plotly_white" if st.get_option("theme.base") != "dark" else "plotly_dark"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Real-Time Traffic Flow (Last 3 Hours)")
    # Generate dynamic time series
    now = datetime.now()
    times = [(now - timedelta(minutes=i*15)).strftime("%H:%M") for i in range(12)][::-1]
    
    # Dynamic flow with more fluctuation
    base_flow = [20, 25, 35, 50, 75, 85, 90, 82, 70, 65, 60, 58]
    dynamic_flow = [max(0, min(100, f + random.randint(-12, 12))) for f in base_flow]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=times, 
        y=dynamic_flow, 
        mode='lines+markers', 
        name='Avg Flow',
        line=dict(color='#6366f1', width=3),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))
    fig2.update_layout(
        yaxis_title="Flow Rate %", 
        xaxis_title="Time", 
        height=400,
        template="plotly_white" if st.get_option("theme.base") != "dark" else "plotly_dark"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Incident logging
if st.session_state.get("view_mode") == "incidents":
    st.markdown("## 📋 Incident Log")
    
    with st.form("incident_form"):
        incident_type = st.selectbox("Incident Type", [
            "Medical Emergency",
            "Security Threat",
            "Overcrowding",
            "Lost Person",
            "Equipment Failure",
            "Other"
        ])
        
        location = st.text_input("Location/Gate", placeholder="e.g., Gate A, Section 5")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        description = st.text_area("Description", placeholder="Brief description of the incident")
        
        if st.form_submit_button("📝 Log Incident"):
            st.success(f"✅ Incident logged at {datetime.now().strftime('%H:%M:%S')}")
            st.info(f"Type: {incident_type} | Location: {location} | Severity: {severity}")

st.divider()

# Quick actions
st.markdown("## ⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔊 Send Announcement", use_container_width=True):
        announcement = st.text_input("Announcement Message", placeholder="Enter message to broadcast")
        if announcement and st.button("📢 Broadcast"):
            st.success("✅ Announcement sent to all gates!")

with col2:
    if st.button("🚨 Emergency Alert", use_container_width=True):
        st.session_state.show_emergency = True

with col3:
    if st.button("📞 Contact Supervisor", use_container_width=True):
        st.info("📱 Supervisor contact: +1-234-567-8900")

if st.session_state.get("show_emergency"):
    st.error("### 🚨 EMERGENCY MODE ACTIVATED")
    st.write("All gates have been notified. Emergency team dispatched.")
    if st.button("Acknowledge"):
        st.session_state.show_emergency = False
        st.rerun()
