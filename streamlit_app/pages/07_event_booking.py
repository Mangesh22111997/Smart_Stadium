
import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image
from utils.animation_helper import show_success_animation
import time

st.set_page_config(page_title="Book Event - Smart Stadium", page_icon="🎟️", layout="wide")

# Check if logged in
if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

# Apply Background
add_background_image()

# Initialize session state for booking flow
if "booking_food_order_id" not in st.session_state:
    st.session_state.booking_food_order_id = None

api_client = get_api_client()

# Check if we have a selected event
if "selected_event" not in st.session_state or st.session_state.selected_event is None:
    st.warning("⚠️ No event selected. Please select an event from the Home or Events page.")
    if st.button("🏠 Go to Home"):
        st.switch_page("pages/02_home.py")
    st.stop()

event = st.session_state.selected_event
event_id = event.get('event_id')

# Header
st.markdown(f"# 🎟️ Booking: {event.get('event_name', 'Unnamed Event')}")
st.divider()

col1, col2 = st.columns([0.6, 0.4])

with col1:
    with st.container():
        st.markdown("### 📋 Event Information")
        st.markdown(f"""
        **📅 Date:** {event.get('event_date', 'TBA')}  
        **⏰ Time:** {event.get('start_time', '00:00')} - {event.get('end_time', '23:59')}  
        **📍 Venue:** {event.get('venue_type', 'Stadium')}
        
        **Event Summary:**  
        {event.get('description', 'Join us for this exciting event at Smart Stadium!')}
        
        **📍 Venue on Map:**  
        [View Location on Google Maps](https://www.google.com/maps/search/stadium)
        """)
        
        st.divider()
        
        # Food Section
        st.markdown("### 🍔 Food & Beverages")
        
        # Check if we have a pending food order from the flow
        if st.session_state.get("booking_food_order_id"):
            st.success(f"✅ Food order linked: **{st.session_state.booking_food_order_id}**")
            if st.button("🔄 Change Food Order"):
                st.session_state.in_booking_flow = True
                st.switch_page("pages/06_food.py")
        else:
            st.info("💡 You can pre-order food and have it ready when you arrive!")
            if st.button("🍔 Browse Food Menu", use_container_width=True):
                st.session_state.in_booking_flow = True
                st.switch_page("pages/06_food.py")

with col2:
    with st.container():
        st.markdown("### 🎫 Reservation")
        
        available_seats = event.get('available_seats', 0)
        if available_seats <= 0:
            st.error("❌ Sold Out!")
            if st.button("🏠 Back to Home", use_container_width=True):
                st.switch_page("pages/02_home.py")
            st.stop()
            
        with st.container(border=True):
            st.markdown("### 🎫 Ticket Details")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Event:** {st.session_state.selected_event.get('event_name')}")
                st.write(f"**Location:** {st.session_state.selected_event.get('venue_type')}")
            with col2:
                st.write(f"**Date:** {st.session_state.selected_event.get('event_date')}")
                st.write(f"**Time:** {st.session_state.selected_event.get('start_time')}")
            
            st.divider()
            
            num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=min(10, available_seats), value=1)
            
            st.divider()
            st.markdown("#### Travel & Arrival")
            commute_mode = st.selectbox("How will you arrive?", ["metro", "bus", "private", "cab"])
            
            # Parking enabled only for private/cab
            # This now reruns instantly because it's outside the form
            is_driving = commute_mode in ["private", "cab"]
            parking_required = st.checkbox(
                "Need Parking?", 
                value=False, 
                disabled=not is_driving,
                help="Parking is only available for private vehicles or cabs."
            )
            
            departure_pref = st.selectbox("Departure Preference", ["early", "immediate", "delayed"])

        # Food Section
        st.markdown("### 🍔 Food & Beverages")
        
        # Check if we have a pending food order from the flow
        if st.session_state.get("food_cart"):
            st.success(f"✅ Food items selected!")
            with st.expander("View Selection"):
                for item in st.session_state.food_cart:
                    st.write(f"- {item.get('name')} (x{item.get('quantity', 1)})")
                st.write(f"**Food Total:** ₹{st.session_state.cart_total}")
            
            if st.button("🔄 Change Food Order"):
                st.session_state.in_booking_flow = True
                st.switch_page("pages/06_food.py")
        else:
            st.info("💡 You can pre-order food and have it ready when you arrive!")
            if st.button("🍔 Browse Food Menu", use_container_width=True):
                st.session_state.in_booking_flow = True
                st.switch_page("pages/06_food.py")

        # Final Confirmation Form
        with st.form("event_booking_form_final"):
            price_per_ticket = event.get('price_per_ticket', 500)
            st.info(f"💰 Total Amount: ₹{num_tickets * price_per_ticket + st.session_state.get('cart_total', 0)}")
            
            if st.form_submit_button("✅ Confirm & Pay", use_container_width=True):
                # 1. Place Food Order first if items are in cart
                final_food_order_id = None
                if st.session_state.get("food_cart"):
                    with st.spinner("🍔 Placing food order..."):
                        food_order_data = {
                            "user_id": SessionManager.get_user_id(),
                            "items": st.session_state.food_cart,
                            "delivery_zone": "Center Booth", # Default for pre-orders
                            "total_price": st.session_state.cart_total,
                            "status": "confirmed"
                        }
                        food_resp = api_client.place_food_order(food_order_data)
                        if isinstance(food_resp, dict) and "error" not in food_resp:
                            final_food_order_id = food_resp.get("order_id") or food_resp.get("id")
                            if final_food_order_id:
                                st.session_state.booking_food_order_id = final_food_order_id
                        else:
                            st.warning(f"⚠️ Food order could not be linked: {food_resp.get('error', 'Unknown error')}")

                # 2. Create ticket booking
                with st.spinner("🔄 Processing booking..."):
                    user_id = SessionManager.get_user_id()
                    token = SessionManager.get_session_token()
                    
                    booking_data = {
                        "event_id": str(event_id),
                        "num_tickets": int(num_tickets),
                        "commute_mode": commute_mode,
                        "parking_required": parking_required if is_driving else False,
                        "departure_preference": departure_pref,
                        "food_order_id": final_food_order_id
                    }
                    
                    response = api_client.create_booking(booking_data, user_id, token)
                    
                    if "error" in response:
                        st.error(f"❌ Booking failed: {response.get('error')}")
                    else:
                        show_success_animation("🎉 Booking Confirmed!")
                        
                        # Store result for confirmation display
                        st.session_state.last_booking = response
                        
                        # Clear state
                        st.session_state.booking_food_order_id = None
                        st.session_state.food_cart = []
                        st.session_state.cart_total = 0
                        st.session_state.selected_event = None
                        st.session_state.in_booking_flow = False
                        
                        time.sleep(2)
                        st.switch_page("pages/04_bookings.py")

if st.button("← Back"):
    st.switch_page("pages/02_home.py")
