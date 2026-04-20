# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Emergency Response Center
Manage emergency situations and coordinated response
"""

import streamlit as st
st.set_page_config(page_title="Emergency Response - Smart Stadium", page_icon="🚨", layout="wide")

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts
from datetime import datetime

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()


# Check security access
if not SessionManager.is_logged_in():
    st.error("❌ Unauthorized")
    st.switch_page("pages/13_security_login.py")
    st.stop()

if SessionManager.get_user_role() not in ["security", "moderator", "superadmin"]:
    st.error("❌ Access denied")
    st.switch_page("pages/00_login.py")
    st.stop()

st.markdown("# 🚨 Emergency Response Center")
st.markdown("Coordinate emergency response and crowd management")

# Navigation
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("← Back to Dashboard"):
        st.switch_page("pages/14_security_dashboard.py")
with col2:
    if st.button("📞 Emergency Contacts"):
        st.session_state.show_contacts = st.session_state.get("show_contacts", False)
        if not st.session_state.show_contacts:
            st.session_state.show_contacts = True
        else:
            st.session_state.show_contacts = False
        st.rerun()
with col3:
    if st.button("📢 Public Announcements"):
        st.session_state.show_announcements = st.session_state.get("show_announcements", False)
        if not st.session_state.show_announcements:
            st.session_state.show_announcements = True
        else:
            st.session_state.show_announcements = False
        st.rerun()
with col4:
    if st.button("🚪 Logout"):
        SessionManager.logout()
        st.switch_page("pages/00_login.py")

st.divider()

# SOS Coordinator
st.markdown("## 🆘 SOS Coordination Center")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Active Emergencies")
    
    emergencies = [
        {"id": "1", "type": "Medical", "location": "Gate A", "status": "In Progress", "time": "5 mins ago"},
        {"id": "2", "type": "Structural", "location": "Stands B", "status": "Resolved", "time": "2 hours ago"},
    ]
    
    for emergency in emergencies:
        status_color = "green" if emergency["status"] == "Resolved" else "red"
        with st.container(border=True):
            col_a, col_b = st.columns([0.7, 0.3])
            with col_a:
                st.markdown(f"**{emergency['type']} Emergency**")
                st.write(f"Location: {emergency['location']}")
                st.write(f"Reported: {emergency['time']}")
            with col_b:
                if emergency["status"] == "In Progress":
                    st.error(emergency["status"])
                    if st.button("✅ Mark Resolved", key=f"resolve_{emergency['id']}"):
                        st.success("Emergency marked as resolved!")
                        st.rerun()
                else:
                    st.success(emergency["status"])

with col2:
    st.markdown("### Report New Emergency")
    
    with st.form("emergency_form"):
        emergency_type = st.selectbox("Emergency Type", [
            "Medical Emergency",
            "Fire/Smoke",
            "Structural Damage",
            "Security Threat",
            "Crowd Crush",
            "Lost Child",
            "Other"
        ])
        
        location = st.text_input("Location", placeholder="e.g., Gate A, Section 5")
        severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
        description = st.text_area("Description", placeholder="Detailed description of the emergency")
        
        affected_people = st.number_input("Estimated People Affected", min_value=0, value=0)
        
        if st.form_submit_button("🚨 ACTIVATE EMERGENCY PROTOCOL"):
            st.error("### ⚠️ EMERGENCY PROTOCOL ACTIVATED")
            st.write(f"**Type:** {emergency_type}")
            st.write(f"**Location:** {location}")
            st.write(f"**Severity:** {severity}")
            st.write(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
            st.balloons()

st.divider()

# Gate Control
st.markdown("## 🚪 Gate Control & Evacuation")

st.write("**Select gates to control during emergency:**")

col1, col2, col3 = st.columns(3)

gates = ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]
selected_gates = []

for idx, gate in enumerate(gates):
    col = [col1, col2, col3][idx % 3]
    with col:
        if st.checkbox(gate, key=f"gate_select_{gate}"):
            selected_gates.append(gate)

if selected_gates:
    st.markdown(f"**Selected gates:** {', '.join(selected_gates)}")
    
    action = st.radio("Gate Action", ["Open for Entry", "Close for Evacuation", "Restrict Flow", "Emergency Exit"])
    
    if st.button("🎯 Apply Action to Selected Gates"):
        st.success(f"✅ {action} initiated for: {', '.join(selected_gates)}")

st.divider()

# Public Announcements
if st.session_state.get("show_announcements"):
    st.markdown("## 📢 Public Address System")
    
    with st.form("announcement_form"):
        
        announcement_type = st.selectbox("Announcement Type", [
            "General Info",
            "Emergency Instructions",
            "All-Clear (Resume Normal)",
            "Evacuation Order",
            "Shelter In Place",
            "Custom Message"
        ])
        
        message = st.text_area(
            "Message to Broadcast",
            placeholder="Enter the announcement message...",
            height=100
        )
        
        zones = st.multiselect(
            "Broadcast to Zones",
            ["All Zones", "Gate Areas", "Stands", "Food Courts", "Restrooms"]
        )
        
        if st.form_submit_button("📣 Broadcast Announcement"):
            st.success("✅ Announcement broadcast to selected zones!")
            st.info(f"Message: {message}")
            st.info(f"Zones: {', '.join(zones) if zones else 'All'}")

st.divider()

# Emergency Contacts (if shown)
if st.session_state.get("show_contacts"):
    st.markdown("## 📞 Emergency Contacts")
    
    contacts = {
        "Medical": "+1-234-567-8900",
        "Fire Department": "+1-234-567-8901",
        "Police": "+1-234-567-8902",
        "Management Head": "+1-234-567-8903",
        "Operations Lead": "+1-234-567-8904",
        "Local Authorities": "+1-234-567-8905",
    }
    
    col1, col2 = st.columns(2)
    
    for idx, (contact_type, number) in enumerate(contacts.items()):
        col = col1 if idx % 2 == 0 else col2
        with col:
            with st.container(border=True):
                st.write(f"**{contact_type}**")
                st.write(f"📞 {number}")
                if st.button(f"Call {contact_type}", key=f"call_{contact_type}"):
                    st.info(f"Dialing {number}...")

st.divider()

st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Stay calm. All emergency procedures are in effect. Coordinate with your team.
</div>
""", unsafe_allow_html=True)
