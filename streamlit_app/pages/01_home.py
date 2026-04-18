"""
Home Page - Customer Dashboard
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image
from utils.i18n import t, language_selector
import hashlib

st.set_page_config(page_title="Home - Smart Stadium", page_icon="🏠", layout="wide")

# Add Language Selector in Sidebar
language_selector()

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# Apply Background
add_background_image()

# Initialize session state
if "show_profile_menu" not in st.session_state:
    st.session_state.show_profile_menu = False
if "show_notifications" not in st.session_state:
    st.session_state.show_notifications = False

api_client = get_api_client()
username = SessionManager.get_username()
user_id = SessionManager.get_user_id()
user_id_short = (hashlib.md5(user_id.encode()).hexdigest()[:8]).upper()

# Header with Profile and Notifications
col1, col2, col3 = st.columns([0.7, 0.15, 0.15])

with col1:
    st.markdown(f"""
    <div style='padding: 20px; background: rgba(255, 255, 255, 0.95); border-radius: 10px;'>
        <h2 style='color: #667eea; margin: 0;'>🏟️ {t("welcome")}</h2>
        <p style='color: #666; margin: 5px 0 0 0; font-size: 14px;'>{username}!</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Notifications Bell
    if st.button("🔔", key="notif_bell", help="Notifications"):
        st.session_state.show_notifications = not st.session_state.show_notifications

with col2:
    # Profile Dropdown
    if st.button("👤", key="profile_menu", help="Profile Menu"):
        st.session_state.show_profile_menu = not st.session_state.show_profile_menu

st.divider()

# Profile Menu Dropdown
if st.session_state.show_profile_menu:
    with st.container():
        st.markdown("### 👤 Profile Menu")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **User ID:**  
            `{user_id_short}`
            """)
        with col2:
            st.markdown(f"""
            **Username:**  
            {username}
            """)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 My Bookings", use_container_width=True, key="menu_bookings"):
                st.switch_page("pages/03_bookings.py")
        with col2:
            if st.button("⚙️ Settings", use_container_width=True, key="menu_settings"):
                st.info("Settings page coming soon!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Edit Profile", use_container_width=True, key="menu_profile"):
                st.info("Profile editor coming soon!")
        with col2:
            if st.button("🚪 Logout", use_container_width=True, key="menu_logout"):
                api_client.logout(SessionManager.get_session_token())
                SessionManager.logout()
                st.success("✅ Logged out successfully!")
                st.switch_page("pages/1_Login.py")

# Notifications Section
if st.session_state.show_notifications:
    with st.container():
        st.markdown("### 🔔 Recent Notifications")
        
        st.info("📢 Your next event 'Music Festival 2026' starts in 5 days!")
        st.info("🎟️ Your booking confirmation has been sent to your email")
        st.success("✅ New events added: Rock Show, Comedy Night")
        
        st.divider()

# Main Content
st.markdown("""
<div class='content-card'>
    <h3 style='color: #667eea;'>🎯 Quick Actions</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='event-card'>
        <h4 style='margin-top: 0; color: #667eea;'>🎉 Discover Events</h4>
        <p>Find and book your next favorite event</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Browse →", use_container_width=True, key="discover_btn"):
        st.switch_page("pages/02_events.py")

with col2:
    st.markdown("""
    <div class='event-card'>
        <h4 style='margin-top: 0; color: #667eea;'>🗺️ Stadium Maps</h4>
        <p>Explore gates and venue layout</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Maps →", use_container_width=True, key="maps_btn"):
        st.switch_page("pages/04_maps.py")

with col3:
    st.markdown("""
    <div class='event-card'>
        <h4 style='margin-top: 0; color: #667eea;'>🍔 Food Ordering</h4>
        <p>Order food and beverages</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Order Now →", use_container_width=True, key="food_btn"):
        st.switch_page("pages/05_food.py")

st.divider()

# ==================== AVAILABLE EVENTS SECTION ====================
st.markdown("""
<div class='content-card'>
    <h3 style='color: #667eea;'>📅 Explore Upcoming Events</h3>
    <p style='color: #666;'>Find and book the best experiences at Smart Stadium</p>
</div>
""", unsafe_allow_html=True)

# Search and Filter
search_query = st.text_input(
    "🔍 Search Events",
    placeholder="Search by name, category or artist...",
    key="home_search"
)

# Fetch all events
try:
    events_response = api_client.list_events(limit=20)
    events = events_response.get("events", []) if isinstance(events_response, dict) else []
    
    # Filter events
    if search_query:
        events = [e for e in events if search_query.lower() in e.get("event_name", "").lower() or 
                  search_query.lower() in e.get("venue_type", "").lower()]

    if not events:
        st.info("📭 No events found matching your search.")
    else:
        # Display Events in a list
        for idx, event in enumerate(events):
            with st.container():
                col1, col2, col3 = st.columns([0.15, 0.6, 0.25])
                
                with col1:
                    # Event date display
                    event_date = event.get('event_date', 'TBA')
                    parts = event_date.split('-') if event_date else ['', '', '']
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                                padding: 10px; border-radius: 8px; text-align: center;'>
                        <strong style='font-size: 18px;'>{parts[2] if len(parts) > 2 else '  '}</strong><br>
                        <small>{parts[1] if len(parts) > 1 else 'Month'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"#### {event.get('event_name', 'Unnamed Event')}")
                    st.markdown(f"📍 {event.get('venue_type', 'Stadium')} • 💰 ₹{event.get('price_per_ticket', 0)}")
                
                with col3:
                    if st.button("🎟️ Book Now", key=f"home_book_{event.get('event_id', 'e')}_{idx}", use_container_width=True):
                        # Redirect to dedicated booking page
                        st.session_state["selected_event"] = event
                        st.switch_page("pages/06_event_booking.py")
                
                st.divider()
except Exception as e:
    st.error(f"⚠️ Could not load events: {str(e)}")

st.divider()

st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px; padding: 20px;'>
    🏟️ Smart Stadium System | Your Premier Event Management Platform
</div>
""", unsafe_allow_html=True)
