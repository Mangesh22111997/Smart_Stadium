"""
Events Discovery Page - Browse and Book Events
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image

st.set_page_config(page_title="Events - Smart Stadium", page_icon="🎉", layout="wide")

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/00_login.py")
    st.stop()

# Apply Background
add_background_image()

# Additional Page styling
st.markdown("""
<style>
    .event-card:hover {
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .book-btn {
        position: absolute;
        bottom: 20px;
        right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None
if "show_event_details" not in st.session_state:
    st.session_state.show_event_details = False

# Header
col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
with col1:
    st.markdown("# 🎉 Discover Events")
    st.markdown("*Explore upcoming events at Smart Stadium*")
with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/02_home.py")

st.divider()

# Search bar
search_query = st.text_input(
    "🔍 Search for events",
    placeholder="Enter event name, artist, or category...",
    key="search_events"
)

# Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    date_filter = st.date_input("📅 From date", key="event_date")
with col2:
    category = st.selectbox("📂 Category", ["All", "Sports", "Concert", "Workshop", "Conference"], key="event_category")
with col3:
    price_range = st.select_slider("💰 Price Range", [0, 500, 1000, 1500, 2000, 5000], value=[0, 5000])
with col4:
    availability_filter = st.selectbox("🎟️ Availability", ["Any", "Plenty", "Limited", "Last Few"], key="availability")

st.divider()

# Fetch events from backend API
api_client = get_api_client()
events_response = api_client.list_events(limit=50)

if "error" in events_response and events_response.get("events") is None:
    st.error(f"❌ Failed to fetch events: {events_response.get('error')}")
    events = []
else:
    events = events_response.get("events", [])

# Apply filters
filtered_events = events.copy()

if search_query:
    filtered_events = [e for e in filtered_events if search_query.lower() in e.get("event_name", "").lower()]

if category != "All":
    filtered_events = [e for e in filtered_events if e.get("venue_type") == category]

# Price filter
filtered_events = [e for e in filtered_events if price_range[0] <= e.get("price_per_ticket", 0) <= price_range[1]]

# Availability filter
if availability_filter == "Plenty":
    filtered_events = [e for e in filtered_events if e.get("available_seats", 0) / max(e.get("seating_capacity", 1), 1) > 0.5]
elif availability_filter == "Limited":
    filtered_events = [e for e in filtered_events if 0.1 < e.get("available_seats", 0) / max(e.get("seating_capacity", 1), 1) <= 0.5]
elif availability_filter == "Last Few":
    filtered_events = [e for e in filtered_events if 0 < e.get("available_seats", 0) / max(e.get("seating_capacity", 1), 1) <= 0.1]

# Display results
if not filtered_events:
    st.info("📭 No events found matching your criteria. Check back soon!")
else:
    st.markdown(f"### 📊 Showing {len(filtered_events)} events")
    st.divider()
    
    # Display events in a grid/list
    for event in filtered_events:
        col1, col2, col3 = st.columns([0.15, 0.6, 0.25], gap="medium")
        
        with col1:
            # Event date display
            event_date = event.get('event_date', 'TBA')
            parts = event_date.split('-') if event_date else ['', '', '']
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                        padding: 15px; border-radius: 8px; text-align: center;'>
                <strong style='font-size: 20px;'>{parts[2] if len(parts) > 2 else '  '}</strong><br>
                <small>{parts[1] if len(parts) > 1 else 'Month'}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            ### {event.get('event_name', 'Unnamed Event')}
            **⏰ Time:** {event.get('start_time', '00:00')} - {event.get('end_time', '23:59')}  
            **📍 Venue:** {event.get('venue_type', 'Stadium')}  
            **🎟️ Tickets:** {event.get('available_seats', 0)} available  
            **💰 Price:** ₹{event.get('price_per_ticket', 500)} per ticket  
            **📊 Capacity:** {event.get('seating_capacity', 0)} seats
            """)
            
            # Additional details
            try:
                with st.expander("ℹ️ More Details"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**🚪 Gates:** {event.get('number_of_gates', 0)}")
                        st.write(f"**🚗 Parking:** {'✅ Available' if event.get('parking_available') else '❌ Not Available'}")
                    with col_b:
                        st.write(f"**🍔 Food Courts:** {'✅ Available' if event.get('food_available', True) else '❌ Not Available'}")
                        st.write(f"**📱 WiFi:** {'✅ Available' if event.get('wifi_available', True) else '❌ Not Available'}")
            except:
                pass
        
        with col3:
            # Availability status
            availability_pct = (event.get('available_seats', 0) / max(event.get('seating_capacity', 1), 1)) * 100
            
            if availability_pct > 50:
                st.success(f"✅ {availability_pct:.0f}% Available")
            elif availability_pct > 10:
                st.warning(f"⚠️ {availability_pct:.0f}% Left")
            else:
                st.error(f"🔴 Almost Full")
            
            # Book button
            if event.get('available_seats', 0) > 0:
                if st.button("🎟️ Book Now", use_container_width=True, key=f"book_{event.get('event_id', '')}"):
                    st.session_state["selected_event"] = event
                    st.switch_page("pages/07_event_booking.py")
            else:
                st.error("❌ Sold Out!")
        
        st.divider()

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    🏟️ Smart Stadium | Secure Booking | Real-time Availability
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    🏟️ Smart Stadium | Secure Booking | Real-time Availability
</div>
""", unsafe_allow_html=True)
