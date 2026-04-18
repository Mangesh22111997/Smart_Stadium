"""
Ticket Bookings Page
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client

st.set_page_config(page_title="Bookings - Smart Stadium", page_icon="🎟️", layout="wide")

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/1_Login.py")
    st.stop()

st.markdown("# 🎟️ Ticket Bookings")
st.markdown("*Manage your event bookings and tickets*")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/1_Login.py")

st.divider()

# Check if booking from events page
if "selected_event" in st.session_state:
    event = st.session_state["selected_event"]
    event_id = event.get('event_id')
    
    st.markdown(f"## Booking: {event.get('event_name', 'Event')}")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📍 **Venue:** {event.get('venue_type', 'TBD')}")
            st.write(f"📅 **Date:** {event.get('event_date', 'TBD')} at {event.get('start_time', '00:00')}")
        
        st.divider()
        
        max_available = event.get('available_seats', 0)
        if max_available == 0:
            st.error("❌ No tickets available")
            st.stop()
        
        num_tickets = st.number_input(
            "Number of Tickets",
            min_value=1,
            max_value=min(10, max_available),
            value=1
        )
        
        price_per_ticket = event.get('price_per_ticket', 500)
        total_price = num_tickets * price_per_ticket
        st.write(f"💰 **Total Price:** ₹{total_price}")
        
        st.markdown("### Travel Preferences")
        commute_mode = st.selectbox("Commute Mode", ["Public Transport", "Car", "Bike", "Walking"])
        parking_required = st.checkbox("Parking Required", value=False)
        departure_pref = st.selectbox("Preferred Time", ["Morning", "Afternoon", "Evening"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Confirm Booking", use_container_width=True):
                # Create booking via API
                api_client = get_api_client()
                user_id = SessionManager.get_user_id()
                session_token = SessionManager.get_session_token()
                
                booking_data = {
                    "event_id": event_id,
                    "num_tickets": int(num_tickets),
                    "commute_mode": commute_mode,
                    "parking_required": parking_required,
                    "departure_preference": departure_pref
                }
                
                response = api_client.create_booking(booking_data, user_id, session_token)
                
                if "error" in response:
                    st.error(f"❌ Booking failed: {response.get('error')}")
                else:
                    st.success("✅ Booking confirmed!")
                    st.info(f"🎟️ **Ticket ID:** {response.get('ticket_id', 'N/A')}")
                    st.info(f"🚪 **Assigned Gate:** {response.get('assigned_gate', 'TBD')}")
                    st.info(f"📝 **Confirmation Number:** {response.get('confirmation_number', 'N/A')}")
                    st.balloons()
                    
                    # Clear selected event
                    del st.session_state["selected_event"]
                    st.session_state.refresh_bookings = True
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                del st.session_state["selected_event"]
                st.rerun()
else:
    st.info("📭 No booking in progress. Select an event from the Events page to book.")
    
st.divider()
st.markdown("## Your Booking History")

# Fetch user's previous bookings
api_client = get_api_client()
user_id = SessionManager.get_user_id()
session_token = SessionManager.get_session_token()

bookings_response = api_client.get_user_bookings(user_id, session_token)
bookings = bookings_response.get("bookings", [])

if not bookings:
    st.info("📋 No previous bookings yet. Book your first ticket!")
else:
    for booking in bookings:
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
            
            with col1:
                st.markdown(f"**Ticket ID:** {booking.get('ticket_id', 'N/A')[:12]}")
                st.write(f"Event: {booking.get('event_id', 'N/A')}")
                st.write(f"Tickets: {booking.get('num_tickets', 0)}")
                st.write(f"Total: ₹{booking.get('total_price', 0)}")
            
            with col2:
                st.write(f"Gate: {booking.get('assigned_gate', 'TBD')}")
                st.write(f"Mode: {booking.get('commute_mode', 'N/A')}")
            
            with col3:
                status = booking.get('status', 'unknown')
                if status == "confirmed":
                    st.success(f"✅ {status.title()}")
                elif status == "cancelled":
                    st.error(f"❌ {status.title()}")
                else:
                    st.info(f"ℹ️ {status.title()}")
                
                if status == "confirmed":
                    if st.button("Cancel Booking", key=f"cancel_{booking.get('ticket_id')}"):
                        api_client.cancel_booking(booking.get('ticket_id'), user_id)
                        st.rerun()

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("🎉 Browse Events", use_container_width=True):
        st.switch_page("pages/4_Events.py")
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/3_Home.py")
