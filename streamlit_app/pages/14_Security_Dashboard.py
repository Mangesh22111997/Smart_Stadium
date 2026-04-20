"""
Security Monitoring Dashboard
Real-time crowd and gate monitoring
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Security Dashboard - Smart Stadium", page_icon="📊", layout="wide")

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

# Initialize session state
if "view_mode" not in st.session_state:
    st.session_state.view_mode = None
if "editing_gate" not in st.session_state:
    st.session_state.editing_gate = None

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
st.markdown("## 🚪 Real-Time Gate Status")

api_client = get_api_client()
gates_response = api_client.get_all_gates()
gates = gates_response.get("gates", {})

if gates:
    # Create metrics for each gate
    gate_cols = st.columns(len(gates) if len(gates) <= 5 else 5)
    
    for idx, (gate_key, gate_data) in enumerate(gates.items()):
        col_idx = idx % 5
        with gate_cols[col_idx]:
            crowd_pct = gate_data.get("crowd_percentage", 0)
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
    st.markdown("### Gate Occupancy")
    gate_names = [g.get("name", k) for k, g in gates.items()]
    gate_crowds = [g.get("crowd_percentage", 0) for g in gates.values()]
    
    fig1 = go.Figure(data=[
        go.Bar(x=gate_names, y=gate_crowds, marker_color=["red" if c > 80 else "orange" if c > 50 else "green" for c in gate_crowds])
    ])
    fig1.update_layout(yaxis_title="Crowd %", xaxis_title="Gates", height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Traffic Flow Trend")
    times = ["14:00", "14:15", "14:30", "14:45", "15:00", "15:15"]
    avg_crowd = [30, 45, 60, 75, 82, 78]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=times, y=avg_crowd, mode='lines+markers', name='Average Crowd'))
    fig2.update_layout(yaxis_title="Crowd %", xaxis_title="Time", height=400)
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
