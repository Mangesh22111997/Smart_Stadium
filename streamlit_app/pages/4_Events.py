"""
Events Discovery Page - Browse and Book Events
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Events - Smart Stadium", page_icon="🎉", layout="wide")

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

st.markdown("# 🎉 Discover Events")
st.markdown("*Explore upcoming events at Smart Stadium*")

# Logout button
if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/1_Login.py")

st.divider()

# Search and filter
col1, col2, col3 = st.columns(3)
with col1:
    search_query = st.text_input("🔍 Search events", placeholder="Event name...")
with col2:
    date_filter = st.date_input("📅 From date")
with col3:
    category = st.selectbox("📂 Category", ["All", "Sports", "Concert", "Workshop", "Conference"])

st.markdown("---")

# Fetch events from backend API
api_client = get_api_client()
events_response = api_client.list_events(limit=50)

if "error" in events_response and events_response.get("events") is None:
    st.error(f"❌ Failed to fetch events: {events_response.get('error')}")
    events = []
else:
    events = events_response.get("events", [])

# Apply filters
if search_query:
    events = [e for e in events if search_query.lower() in e.get("event_name", "").lower()]

if category != "All":
    events = [e for e in events if e.get("venue_type") == category]

# Display results
if not events:
    st.info("📭 No events found matching your criteria. Check back soon!")
else:
    st.markdown(f"**Found {len(events)} events**")
    st.markdown("---")
    
    # Display events
    for event in events:
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        
        with col1:
            st.markdown(f"### {event.get('event_name', 'Unnamed Event')}")
            st.write(f"📅 **Date:** {event.get('event_date', 'TBD')} at {event.get('start_time', '00:00')}")
            st.write(f"📍 **Venue:** {event.get('venue_type', 'TBD')}")
            st.write(f"💺 **Available:** {event.get('available_seats', 0)} / {event.get('seating_capacity', 0)} seats")
            st.write(f"💰 **Price:** ₹{event.get('price_per_ticket', 500)} per ticket")
            
            # Additional info
            info_cols = st.columns(3)
            with info_cols[0]:
                st.metric("🚗 Parking", "Yes" if event.get("parking_available") else "No")
            with info_cols[1]:
                st.metric("🚪 Gates", event.get("number_of_gates", 0))
            with info_cols[2]:
                availability_pct = (event.get('available_seats', 0) / max(event.get('seating_capacity', 1), 1)) * 100
                st.metric("Availability", f"{availability_pct:.0f}%")
        
        with col2:
            st.markdown("")
            st.markdown("")
            availability_pct = (event.get('available_seats', 0) / max(event.get('seating_capacity', 1), 1)) * 100
            if availability_pct > 50:
                st.success(f"{availability_pct:.0f}% Available")
            elif availability_pct > 10:
                st.warning(f"{availability_pct:.0f}% Left")
            else:
                st.error("Almost Full")
        
        with col3:
            st.markdown("")
            st.markdown("")
            if event.get('available_seats', 0) > 0:
                if st.button("🎟️ Book Now", use_container_width=True, key=f"book_{event.get('event_id', '')}"):
                    st.session_state["selected_event"] = event
                    st.switch_page("pages/5_Bookings.py")
            else:
                st.error("Sold Out!")
        
        st.markdown("---")
