# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Ticket Bookings Page
"""

import streamlit as st
st.set_page_config(page_title="Bookings - Smart Stadium", page_icon="🎟️", layout="wide")

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts, inject_main_content_start, inject_main_content_end

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()


# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

st.markdown("# 🎟️ Ticket Bookings")
st.markdown("*Manage your event bookings and tickets*")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()
inject_main_content_start()

st.divider()
inject_main_content_start()

# Booking History Section
st.markdown("## 📜 Your Booking History")
st.markdown("*View and manage your previous ticket reservations*")
    
st.divider()
inject_main_content_start()
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
    # Sort bookings by date (newest first)
    bookings.sort(key=lambda x: x.get('booking_date', ''), reverse=True)
    
    for booking in bookings:
        with st.container():
            # Use columns for a better layout
            col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
            
            with col1:
                st.markdown(f"#### 🎟️ Ticket: {booking.get('ticket_id', 'N/A')[:12]}")
                st.write(f"**Event ID:** `{booking.get('event_id', 'N/A')}`")
                st.write(f"**Tickets:** {booking.get('num_tickets', 1)}")
                st.write(f"**Total Paid:** ₹{booking.get('total_price', 0)}")
            
            with col2:
                st.write(f"**🚪 Gate:** {booking.get('assigned_gate', 'TBD')}")
                st.write(f"**🚗 Arrival:** {booking.get('commute_mode', 'N/A').title()}")
                
                food_id = booking.get('food_order_id')
                if food_id and str(food_id).strip() and str(food_id) != "None":
                    st.success(f"🍔 **Food Order ID:** `{food_id}`")
                else:
                    st.info("🍔 No food pre-ordered")
            
            with col3:
                status = booking.get('status', 'unknown')
                if status == "confirmed":
                    st.success(f"✅ {status.title()}")
                elif status == "cancelled":
                    st.error(f"❌ {status.title()}")
                else:
                    st.info(f"ℹ️ {status.title()}")
                
                # Map link
                st.markdown("[📍 Open Stadium Map](https://www.google.com/maps/search/stadium)")
                
                if status == "confirmed":
                    if st.button("❌ Cancel", key=f"cancel_{booking.get('ticket_id')}", use_container_width=True):
                        api_client.cancel_booking(booking.get('ticket_id'), user_id)
                        st.rerun()
            
            st.divider()
inject_main_content_start()

st.divider()
inject_main_content_start()

col1, col2 = st.columns(2)
with col1:
    if st.button("🎉 Browse Events", use_container_width=True):
        st.switch_page("pages/03_events.py")
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/02_home.py")

