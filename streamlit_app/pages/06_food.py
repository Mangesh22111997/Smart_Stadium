# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Food Ordering Page - Order food and beverages
"""

import streamlit as st
st.set_page_config(page_title="Food - Smart Stadium", page_icon="🍔", layout="wide")

from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.ui_helper import add_background_image, inject_accessibility_enhancements, render_keyboard_shortcuts, inject_main_content_start, inject_main_content_end
import time

# Apply Background and Accessibility Enhancements
add_background_image()
inject_accessibility_enhancements()

# Sidebar shortcuts
with st.sidebar:
    render_keyboard_shortcuts()

@st.cache_data(ttl=600, show_spinner=False)
def fetch_menu_cached():
    """Fetch food menu. Cached 10 min — menu rarely changes during an event."""
    return get_api_client().get_food_menu()


if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

# Apply Background
add_background_image()

st.markdown("# 🍔 Food & Beverage Ordering")
st.markdown("*Order food items for pickup at convenient locations*")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()
inject_main_content_start()

# Initialize session state for cart
if "food_cart" not in st.session_state:
    st.session_state.food_cart = []
if "cart_total" not in st.session_state:
    st.session_state.cart_total = 0

# Get menu from API (CACHED)
api_client = get_api_client()
menu_response = fetch_menu_cached()

if "error" in menu_response and not menu_response.get("items"):
    # Use default menu if API fails
    menu_items = [
        {"id": "1", "name": "Veggie Burger", "category": "Burgers", "price": 250, "description": "Fresh veggie burger"},
        {"id": "2", "name": "Chicken Burger", "category": "Burgers", "price": 320, "description": "Grilled chicken burger"},
        {"id": "3", "name": "Margherita Pizza", "category": "Pizza", "price": 400, "description": "Classic cheese pizza"},
        {"id": "4", "name": "Pepperoni Pizza", "category": "Pizza", "price": 450, "description": "Pizza with pepperoni"},
        {"id": "5", "name": "Fries", "category": "Snacks", "price": 150, "description": "Crispy French fries"},
        {"id": "6", "name": "Nachos", "category": "Snacks", "price": 180, "description": "Cheese nachos with salsa"},
        {"id": "7", "name": "Coke", "category": "Beverages", "price": 100, "description": "Cold coke"},
        {"id": "8", "name": "Lassi", "category": "Beverages", "price": 80, "description": "Traditional yogurt drink"},
        {"id": "9", "name": "Chocolate Cake", "category": "Desserts", "price": 200, "description": "Moist chocolate cake"},
        {"id": "10", "name": "Ice Cream", "category": "Desserts", "price": 150, "description": "Vanilla ice cream"},
    ]
else:
    menu_items = menu_response.get("items", [])

# Display menu by category
st.markdown("## 📋 Menu")

categories = list(set([item.get("category", "Other") for item in menu_items]))
selected_category = st.selectbox("Filter by category:", ["All"] + sorted(categories))

if selected_category == "All":
    display_items = menu_items
else:
    display_items = [item for item in menu_items if item.get("category") == selected_category]

# Display menu items in columns
cols = st.columns(3)

for idx, item in enumerate(display_items):
    col = cols[idx % 3]
    
    with col:
        with st.container(border=True):
            st.markdown(f"### {item.get('name', 'Item')}")
            st.write(f"*{item.get('category', 'Food')}*")
            st.write(item.get("description", ""))
            
            col_a, col_b = st.columns([0.6, 0.4])
            with col_a:
                st.markdown(f"**₹{item.get('price', 0)}**")
            with col_b:
                if st.button("➕ Add", key=f"add_{item.get('id', 'item')}_{idx}"):
                    # Map item to cart format with default quantity 1
                    cart_item = {
                        "item_id": str(item.get('id') or item.get('item_id')),
                        "name": item.get('name'),
                        "quantity": 1,
                        "unit_price": float(item.get('price', 0))
                    }
                    st.session_state.food_cart.append(cart_item)
                    st.session_state.cart_total += cart_item.get('unit_price', 0)
                    st.success("✅ Added to cart!")

st.divider()
inject_main_content_start()

# Shopping Cart
st.markdown("## 🛒 Your Cart")

if not st.session_state.food_cart:
    st.info("Your cart is empty. Add items from the menu above!")
else:
    # Display cart items
    for idx, item in enumerate(st.session_state.food_cart):
        col_a, col_b, col_c = st.columns([0.6, 0.2, 0.2])
        
        with col_a:
            st.write(f"{item.get('name', 'Item')} - ₹{item.get('unit_price', 0)}")
        
        with col_b:
            st.write(f"₹{item.get('unit_price', 0)}")
        
        with col_c:
            if st.button("❌ Remove", key=f"remove_{idx}"):
                st.session_state.cart_total -= item.get('unit_price', 0)
                st.session_state.food_cart.pop(idx)
                st.rerun()
    
    st.divider()
inject_main_content_start()
    
    # Total and checkout
    col_a, col_b = st.columns([0.6, 0.4])
    
    with col_a:
        st.markdown(f"### **Total: ₹{st.session_state.cart_total}**")
    
    with col_b:
        st.write("")  # Spacing
    
    st.divider()
inject_main_content_start()
    
    # Checkout / Selection Form
    if st.session_state.get("in_booking_flow"):
        st.markdown("### 🛒 Confirm Your Selection")
        st.info("💡 You'll finalize payment for these items on the Booking page.")
        if st.button("✅ Confirm Selection & Return", use_container_width=True):
            st.switch_page("pages/07_event_booking.py")
    else:
        st.markdown("### 🛍️ Checkout")
        
        with st.form("food_order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                delivery_zone = st.selectbox(
                    "Pickup Location:",
                    ["Pillar 1", "Pillar 2", "Pillar 3", "Pillar 4", "Center Booth"]
                )
            
            with col2:
                preferred_time = st.selectbox(
                    "Preferred Pickup Time:",
                    ["ASAP (15-20 min)", "20-30 min", "30-45 min", "45+ min"]
                )
            
            special_requests = st.text_area(
                "Special Requests (Optional):",
                placeholder="e.g., No onions, extra sauce, etc."
            )
            
            # Terms
            agree_terms = st.checkbox("I agree to the terms & conditions")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.form_submit_button("✅ Place Order", use_container_width=True):
                    if not agree_terms:
                        st.error("❌ Please accept the terms & conditions")
                    else:
                        # Create order via API
                        user_id = SessionManager.get_user_id()
                        
                        order_data = {
                            "user_id": user_id,
                            "items": st.session_state.food_cart,
                            "delivery_zone": delivery_zone,
                            "total_price": st.session_state.cart_total,
                            "special_requests": special_requests,
                            "status": "confirmed"
                        }
                        
                        response = api_client.place_food_order(order_data)
                        
                        if "error" in response:
                            st.error(f"❌ Order failed: {response.get('error')}")
                        else:
                            order_id = response.get('order_id') or response.get('id', 'N/A')
                            # Show custom success animation from helper
                            from utils.animation_helper import show_success_animation
                            show_success_animation("✅ Order placed successfully!")
                            st.info(f"📦 **Order ID:** {order_id}")
                            st.info(f"📍 **Pickup at:** {delivery_zone}")
                            st.info(f"⏱️ **Ready in:** {preferred_time}")
                            st.info(f"💰 **Total Amount:** ₹{st.session_state.cart_total}")
                            
                            # Clear cart
                            st.session_state.food_cart = []
                            st.session_state.cart_total = 0
                            
                            # Handle Booking Flow Redirection
                            if st.session_state.get("in_booking_flow"):
                                st.session_state.booking_food_order_id = response.get('order_id') or response.get('id')
                                st.info("🔄 Returning to your booking...")
                                time.sleep(2)
                                st.switch_page("pages/07_event_booking.py")
            
            with col_b:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.food_cart = []
                    st.session_state.cart_total = 0
                    st.rerun()

st.divider()
inject_main_content_start()

# Order History
st.markdown("## 📜 Your Order History")

user_id = SessionManager.get_user_id()
orders_response = api_client.get_user_food_orders(user_id)
orders = orders_response.get("orders", []) if isinstance(orders_response, dict) else []

if not orders:
    st.info("No previous food orders yet.")
else:
    for order in orders:
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([0.5, 0.25, 0.25])
            
            with col_a:
                order_id_display = str(order.get('order_id') or order.get('id', 'N/A'))
                st.markdown(f"**Order ID:** {order_id_display[:12]}")
                st.write(f"Total: ₹{order.get('total_price', 0)}")
            
            with col_b:
                st.write(f"Pickup: {order.get('delivery_zone', 'N/A')}")
            
            with col_c:
                status = order.get('status', 'unknown')
                if status == "confirmed":
                    st.success(f"✅ {status.title()}")
                elif status == "ready":
                    st.info(f"🟡 {status.title()}")
                elif status == "picked_up":
                    st.success(f"✅ {status.title()}")
                else:
                    st.info(f"ℹ️ {status.title()}")

st.divider()
inject_main_content_start()

col1, col2 = st.columns(2)
with col1:
    if st.button("🎉 Browse Events", use_container_width=True):
        st.switch_page("pages/03_events.py")
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/02_home.py")

