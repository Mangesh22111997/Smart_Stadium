"""
Home Page - Customer Dashboard
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Home - Smart Stadium", page_icon="🏠", layout="wide")

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# Header with logout option
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
with col1:
    st.markdown(f"## 👋 Welcome, {SessionManager.get_username()}!")
with col3:
    if st.button("🚪 Logout", use_container_width=True):
        api_client = get_api_client()
        api_client.logout(SessionManager.get_session_token())
        SessionManager.logout()
        st.success("✅ Logged out successfully!")
        st.switch_page("pages/1_Login.py")

st.divider()

# Quick stats
api_client = get_api_client()
profile = api_client.get_user_profile(SessionManager.get_user_id())

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📧 Email", SessionManager.get_email())
with col2:
    st.metric("👤 User ID", SessionManager.get_user_id()[:8] + "...")
with col3:
    st.metric("🎟️ Bookings", "0")  # TODO: Fetch from backend
with col4:
    st.metric("🍔 Orders", "0")  # TODO: Fetch from backend

st.divider()

# Main content sections
st.markdown("## 🎯 Quick Links")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎉 Discover Events")
    st.write("Browse upcoming events and find something you love.")
    if st.button("Browse Events →", use_container_width=True, key="discover_btn"):
        st.switch_page("pages/4_Events.py")

with col2:
    st.markdown("### 🎟️ My Bookings")
    st.write("View and manage your ticket bookings.")
    if st.button("View Bookings →", use_container_width=True, key="bookings_btn"):
        st.switch_page("pages/5_Bookings.py")

with col3:
    st.markdown("### 🗺️ Stadium Maps")
    st.write("Explore stadium layout and find your gate.")
    if st.button("View Maps →", use_container_width=True, key="maps_btn"):
        st.switch_page("pages/6_Maps.py")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🍔 Food Ordering")
    st.write("Order food and beverages for delivery.")
    if st.button("Order Food →", use_container_width=True, key="food_btn"):
        st.switch_page("pages/7_Food.py")

with col2:
    st.markdown("### 🔔 Notifications")
    st.write("Check for important updates and alerts.")
    if st.button("Notifications →", use_container_width=True, key="notif_btn"):
        st.switch_page("pages/8_Notifications.py")

with col3:
    st.markdown("### 👤 Profile")
    st.write("Update your profile information.")
    if st.button("Edit Profile →", use_container_width=True, key="profile_btn"):
        st.info("Profile editor coming soon!")

st.divider()

# Featured events section
st.markdown("## ⭐ Featured Events")
st.info("📡 Featured events will appear here. Integrate with backend to fetch real events.")

st.divider()

# Footer
st.markdown("""
---
<div style='text-align: center; color: gray; font-size: 12px;'>
    Last updated: Today | Backend Status: Connected ✅
</div>
""", unsafe_allow_html=True)
