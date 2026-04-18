"""
Smart Stadium System - Complete Redesigned Frontend
User Booking App + Admin/Staff Portal
"""

import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from auth_utils import (
    customer_signup, 
    customer_signin, 
    admin_signin,
    get_all_users_count,
    get_all_admins_count
)

# Page configuration
st.set_page_config(
    page_title="Smart Stadium System",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Background Image
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    [data-testid="stAppViewContainer"] {
        background-image: url('file:///g:/Mangesh/Hack2Skill_Google_Challenge_copilot/bkg_image/Gemini_Generated_Image_ylkdo2ylkdo2ylkd.png');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.4);
        z-index: -1;
    }
    
    .main {
        padding: 0px;
        background: rgba(255, 255, 255, 0.95);
        margin: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 40px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .card-header {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .metric-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 10px;
    }
    
    .status-low {
        color: #00cc44;
        font-weight: bold;
    }
    
    .status-medium {
        color: #ff9800;
        font-weight: bold;
    }
    
    .status-high {
        color: #ff4444;
        font-weight: bold;
    }
    
    .form-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .success-box {
        background: #d4edda;
        border-left: 4px solid #00cc44;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ff9800;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #ff4444;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(102, 126, 234, 0.9) !important;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(102, 126, 234, 0.95) !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.92);
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(8px);
    }
    
    [data-testid="stTabBar"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 10px;
        backdrop-filter: blur(8px);
    }
    
    .metric-box {
        background: rgba(248, 249, 250, 0.98);
        backdrop-filter: blur(8px);
    }
    
    .form-section {
        background: rgba(248, 249, 250, 0.98);
        backdrop-filter: blur(8px);
    }
    
    .success-box {
        background: rgba(212, 237, 218, 0.98);
        backdrop-filter: blur(8px);
    }
    
    .warning-box {
        background: rgba(255, 243, 205, 0.98);
        backdrop-filter: blur(8px);
    }
    
    .error-box {
        background: rgba(248, 215, 218, 0.98);
        backdrop-filter: blur(8px);
    }
    
    h1, h2, h3, h4, h5, h6 {
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def initialize_session_state():
    """Initialize all session state variables"""
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "booked_ticket" not in st.session_state:
        st.session_state.booked_ticket = None
    if "assigned_gate" not in st.session_state:
        st.session_state.assigned_gate = None

def main():
    initialize_session_state()
    
    backend_status = check_backend()
    
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        if st.session_state.user_type == "customer":
            show_user_app()
        elif st.session_state.user_type == "admin":
            show_admin_portal()

# ============================================================================
# AUTHENTICATION PAGE
# ============================================================================

def show_auth_page():
    """Show authentication/login page"""
    
    # Header
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        st.markdown("## 🏟️ Smart Stadium")
    with col3:
        col_signin, col_signup = st.columns(2)
        with col_signin:
            if st.button("🔐 Sign In", width='stretch'):
                st.session_state.show_signup = False
                st.rerun()
        with col_signup:
            if st.button("📝 Sign Up", width='stretch'):
                st.session_state.show_signup = True
                st.rerun()
    
    st.markdown("---")
    
    # Hero
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px;'>
        <h1 style='font-size: 48px; color: #333;'>Welcome to Smart Stadium</h1>
        <p style='font-size: 20px; color: #666; margin: 20px 0;'>
            Real-time Crowd Management & Event Experience Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Content
    col_left, col_right = st.columns([1, 2])
    
    with col_right:
        if not st.session_state.show_signup:
            # Customer Login
            st.markdown('<div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
            st.markdown("## 👤 Customer Login")
            
            with st.form("customer_login"):
                email = st.text_input("📧 Email Address", placeholder="your@email.com")
                password = st.text_input("🔐 Password", type="password", placeholder="••••••••")
                
                st.markdown("---")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("✓ Sign In", width='stretch', type="primary")
                with col_btn2:
                    st.form_submit_button("Clear", width='stretch')
                
                if submitted:
                    if email and password:
                        success, message, user_data = customer_signin(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_type = "customer"
                            st.session_state.user_email = user_data['email']
                            st.session_state.user_id = user_data['user_id']
                            st.session_state.user_name = user_data['name']
                            st.success(f"✓ Welcome {user_data['name']}!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Please fill all fields")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            # Customer Sign Up
            st.markdown('<div style="background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
            st.markdown("## 📝 Create Account")
            
            with st.form("customer_signup"):
                name = st.text_input("👤 Full Name", placeholder="Your Name")
                email = st.text_input("📧 Email", placeholder="your@email.com")
                phone = st.text_input("📱 Phone", placeholder="+91-9876543210")
                password = st.text_input("🔐 Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("🔐 Confirm", type="password")
                agree = st.checkbox("I agree to Terms & Conditions")
                
                st.markdown("---")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("✓ Register", width='stretch', type="primary")
                with col_btn2:
                    st.form_submit_button("Clear", width='stretch')
                
                if submitted:
                    if all([name, email, phone, password, confirm, agree]):
                        if password == confirm:
                            success, message = customer_signup(name, email, phone, password)
                            if success:
                                st.success(f"✓ {message}")
                                st.info("Sign in with your credentials now!")
                                st.session_state.show_signup = False
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("❌ Passwords don't match")
                    else:
                        st.error("❌ Fill all fields")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col_left:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 30px; border-radius: 15px;'>
            <h3 style='color: #333; margin-bottom: 20px;'>✨ Features</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: #667eea; font-weight: 600; margin: 0;'>🎯 Smart Gates</p>
                <p style='color: #666; font-size: 14px; margin: 5px 0 0 0;'>Optimal routing</p>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: #667eea; font-weight: 600; margin: 0;'>⏱️ Wait Times</p>
                <p style='color: #666; font-size: 14px; margin: 5px 0 0 0;'>Real-time predictions</p>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: #667eea; font-weight: 600; margin: 0;'>🍔 Food Order</p>
                <p style='color: #666; font-size: 14px; margin: 5px 0 0 0;'>Order ahead</p>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: #667eea; font-weight: 600; margin: 0;'>🚨 Emergency</p>
                <p style='color: #666; font-size: 14px; margin: 5px 0 0 0;'>Quick response</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Admin Login (Bottom)
    col_admin1, col_admin2 = st.columns([1, 3])
    
    with col_admin1:
        st.markdown("## 👮 Admin Portal")
    
    with col_admin2:
        with st.expander("🔓 Staff Login", expanded=False):
            with st.form("admin_login"):
                staff_id = st.text_input("Staff ID", placeholder="STAFF-001")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("✓ Login", width='stretch', type="primary")
                with col_btn2:
                    st.form_submit_button("Clear", width='stretch')
                
                if submitted:
                    if staff_id and password:
                        success, message, admin_data = admin_signin(staff_id, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_type = "admin"
                            st.session_state.user_email = admin_data['email']
                            st.session_state.user_id = admin_data['staff_id']
                            st.session_state.user_name = admin_data['name']
                            st.success("✓ Welcome Admin!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Enter credentials")
            
            st.markdown("""
            <div style='background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                <p style='color: #ff6b35; font-weight: bold; margin: 0 0 10px 0;'>🔒 Demo Credentials</p>
                <p style='margin: 5px 0; font-size: 13px;'><strong>STAFF-001</strong> / staff123</p>
                <p style='margin: 5px 0; font-size: 13px;'><strong>STAFF-002</strong> / admin456</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# USER BOOKING APP
# ============================================================================

def show_user_app():
    """Main user application"""
    
    # Header with logout
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        st.markdown("## 🏟️ Smart Stadium")
    with col3:
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.rerun()
    
    st.markdown("---")
    
    # User info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**👤 Name:** {st.session_state.user_name}")
    with col2:
        st.markdown(f"**📧 Email:** {st.session_state.user_email}")
    with col3:
        st.markdown(f"**🆔 ID:** {st.session_state.user_id}")
    with col4:
        st.markdown(f"**⏰ Login:** {datetime.now().strftime('%H:%M')}")
    
    st.markdown("---")
    
    # Navigation Menu
    selected = option_menu(
        menu_title="📋 Menu",
        options=[
            "Ticket Booking",
            "Gate Info",
            "Crowd Status",
            "Food Ordering",
            "My Journey",
            "Notifications",
            "Navigation",
            "Emergency"
        ],
        icons=[
            "ticket",
            "door-open",
            "people-fill",
            "cup-straw",
            "map",
            "bell",
            "compass",
            "fire"
        ],
        orientation="horizontal"
    )
    
    st.markdown("---")
    
    # Pages
    if selected == "Ticket Booking":
        user_ticket_booking()
    elif selected == "Gate Info":
        user_gate_info()
    elif selected == "Crowd Status":
        user_crowd_status()
    elif selected == "Food Ordering":
        user_food_ordering()
    elif selected == "My Journey":
        user_my_journey()
    elif selected == "Notifications":
        user_notifications()
    elif selected == "Navigation":
        user_navigation()
    elif selected == "Emergency":
        user_emergency()

# ============================================================================
# USER PAGES
# ============================================================================

def user_ticket_booking():
    """Ticket Booking Form"""
    st.markdown("## 🎟️ Book Your Ticket")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        with st.form("ticket_booking"):
            # Form fields
            event_id = st.selectbox(
                "🎭 Select Event",
                ["Soccer Match - Final", "Concert Event", "Cricket Match", "Sports Festival"]
            )
            
            commute_mode = st.radio(
                "🚗 Commute Mode",
                ["Metro", "Bus", "Private Vehicle", "Cab"],
                horizontal=True
            )
            
            parking = st.checkbox("🅿️ Parking Required")
            
            departure = st.radio(
                "⏰ Departure Preference",
                ["Early Entry", "Immediate", "Delayed Entry"],
                horizontal=True
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                num_tickets = st.number_input("🎫 Number of Tickets", min_value=1, max_value=5, value=1)
            with col_b:
                seat_preference = st.selectbox("💺 Seat Preference", ["Standard", "VIP", "Premium"])
            
            st.markdown("---")
            
            submitted = st.form_submit_button("✓ Book Ticket", width='stretch', type="primary")
            
            if submitted:
                ticket_id = f"TKT-{st.session_state.user_id}-{int(datetime.now().timestamp())}"
                gate_assignment = ["A", "B", "C", "D"][hash(ticket_id) % 4]
                
                st.session_state.booked_ticket = {
                    "ticket_id": ticket_id,
                    "event": event_id,
                    "commute": commute_mode,
                    "parking": parking,
                    "departure": departure,
                    "tickets": num_tickets,
                    "seat": seat_preference
                }
                st.session_state.assigned_gate = gate_assignment
                
                st.success("✓ Ticket Booked Successfully!")
                st.balloons()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Booking Info")
        
        if st.session_state.booked_ticket:
            st.markdown(f"""
            - **Ticket ID:** {st.session_state.booked_ticket['ticket_id']}
            - **Gate:** {st.session_state.assigned_gate}
            - **Commute:** {st.session_state.booked_ticket['commute']}
            - **Status:** ✓ Confirmed
            """)
        else:
            st.info("No active booking yet")
        
        st.markdown("</div>", unsafe_allow_html=True)

def user_gate_info():
    """Gate Information Display"""
    st.markdown("## 🚪 Your Gate Information")
    
    if st.session_state.assigned_gate:
        gate = st.session_state.assigned_gate
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Assigned Gate", f"Gate-{gate}", "Main Entrance")
        with col2:
            st.metric("Capacity", "67%", "800 of 1200")
        with col3:
            st.metric("Est. Wait", "15 min", "↓ Improving")
        
        st.markdown("---")
        
        st.markdown("""
        <div class="card">
            <div class="card-header">📝 Instructions</div>
            <p style='margin: 10px 0;'>
            • Arrive at <b>Gate {}</b> for entry<br>
            • Current wait time: <b>15 minutes</b><br>
            • Bring your ticket ID for verification<br>
            • Alternative gates: Gate B (45%), Gate D (52%)<br>
            • Follow staff instructions for safety
            </p>
        </div>
        """.format(gate), unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Gate Info", width='stretch'):
            st.rerun()
    
    else:
        st.warning("👆 Book a ticket first to see gate information")

def user_crowd_status():
    """Live Crowd Status Dashboard"""
    st.markdown("## 👥 Live Crowd Status")
    
    # Create sample data
    gates_data = {
        "Gate": ["A", "B", "C", "D", "E"],
        "Users": [800, 540, 985, 625, 456],
        "Capacity": [1200, 1200, 1200, 1200, 1200],
    }
    
    gates_data["Utilization"] = [int(gates_data["Users"][i]/gates_data["Capacity"][i]*100) for i in range(5)]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chart
        fig = px.bar(
            x=[f"Gate-{g}" for g in gates_data["Gate"]],
            y=gates_data["Utilization"],
            title="Gate Utilization (%)",
            color=gates_data["Utilization"],
            color_continuous_scale=["green", "yellow", "red"],
            labels={"x": "Gate", "y": "Utilization (%)"}
        )
        st.plotly_chart(fig, width='stretch')
    
    with col1:
        # Table
        st.markdown("### 📊 Gate Status")
        for i, gate in enumerate(gates_data["Gate"]):
            util = gates_data["Utilization"][i]
            status = "🟢 Low" if util < 50 else "🟡 Medium" if util < 75 else "🔴 High"
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.markdown(f"**Gate-{gate}**")
            with col_b:
                st.markdown(f"{status}")
            with col_c:
                st.markdown(f"{util}%")
            with col_d:
                st.progress(util/100)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ✨ Tips")
        st.markdown("""
        • Gate-B has lowest crowd
        • Avoid Gate-C (85% full)
        • Best entry: Gate-A (67%)
        • Refresh for updates
        """)
        st.markdown("</div>", unsafe_allow_html=True)

def user_food_ordering():
    """Food Ordering Interface"""
    st.markdown("## 🍔 Food Ordering")
    
    # Menu
    menu = {
        "🍕 Pizza": 250,
        "🍔 Burger": 150,
        "🍟 Fries": 80,
        "🥤 Soft Drink": 50,
        "🍿 Popcorn": 100,
        "🍦 Ice Cream": 60,
        "🥙 Sandwich": 120,
        "🍜 Noodles": 180,
    }
    
    st.markdown("### 📋 Menu")
    
    col1, col2, col3, col4 = st.columns(4)
    columns = [col1, col2, col3, col4]
    
    with st.form("food_order"):
        order_items = {}
        
        for idx, (item, price) in enumerate(menu.items()):
            col = columns[idx % 4]
            with col:
                qty = st.number_input(
                    f"{item}\n₹{price}",
                    min_value=0,
                    max_value=5,
                    value=0,
                    key=f"food_{item}"
                )
                if qty > 0:
                    order_items[item] = {"qty": qty, "price": price}
        
        st.markdown("---")
        
        # Delivery options
        col_a, col_b = st.columns(2)
        with col_a:
            delivery_type = st.radio("🚚 Delivery", ["Pickup Booth", "Delivery to Zone"], horizontal=True)
        with col_b:
            if delivery_type == "Pickup Booth":
                booth = st.selectbox("📍 Booth", ["Booth-1", "Booth-2", "Booth-3", "Booth-4"])
            else:
                zone = st.selectbox("📍 Zone", ["A", "B", "C", "D"])
        
        st.markdown("---")
        
        submitted = st.form_submit_button("✓ Place Order", width='stretch', type="primary")
        
        if submitted:
            if order_items:
                total = sum(item["qty"] * item["price"] for item in order_items.values())
                
                st.success(f"""
                ✓ ORDER CONFIRMED
                
                **Order ID:** ORD-{int(datetime.now().timestamp())}
                **Total:** ₹{total}
                **Pickup:** {booth if delivery_type == "Pickup Booth" else f"Zone-{zone}"}
                **Estimated Time:** 15 minutes
                
                You'll receive a notification when order is ready!
                """)
                st.balloons()
            else:
                st.error("❌ Select at least one item")

def user_my_journey():
    """Journey Status and History"""
    st.markdown("## 📍 My Journey")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "📍 In Progress", "Step 2 of 5")
    with col2:
        st.metric("Assigned Gate", f"Gate-{st.session_state.assigned_gate}" if st.session_state.assigned_gate else "Not Assigned", "Main Entrance")
    with col3:
        st.metric("Entry Time", "15 mins", "Estimated wait")
    
    st.markdown("---")
    
    st.markdown("### 📝 Timeline")
    
    timeline_events = [
        {"time": "14:15", "event": "✓ Ticket Booked", "status": "Complete"},
        {"time": "14:22", "event": "✓ Gate Assigned", "status": "Complete"},
        {"time": "14:25", "event": "⏱ Entry Permission", "status": "In Progress"},
        {"time": "14:40", "event": "→ Proceed to Gate", "status": "Pending"},
        {"time": "14:45", "event": "→ Entry Completed", "status": "Pending"},
    ]
    
    for event in timeline_events:
        col_time, col_event, col_status = st.columns([1, 2, 1])
        with col_time:
            st.markdown(f"**{event['time']}**")
        with col_event:
            st.markdown(event['event'])
        with col_status:
            if event['status'] == "Complete":
                st.markdown("✅ Done")
            elif event['status'] == "In Progress":
                st.markdown("🟡 Active")
            else:
                st.markdown("⏳ Pending")

def user_notifications():
    """Notifications Panel"""
    st.markdown("## 🔔 Notifications")
    
    notifications = [
        {"type": "info", "title": "Gate Assigned", "msg": "You're assigned to Gate-A for entry", "time": "5 min ago"},
        {"type": "success", "title": "Ready to Enter", "msg": "You can proceed to your assigned gate", "time": "2 min ago"},
        {"type": "info", "title": "Food Ready", "msg": "Your food order is ready at Booth-3", "time": "Just now"},
    ]
    
    for notif in notifications:
        icon = "ℹ️" if notif["type"] == "info" else "✓" if notif["type"] == "success" else "⚠️"
        st.markdown(f"""
        <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #667eea;'>
            <p style='margin: 0; font-weight: bold;'>{icon} {notif['title']}</p>
            <p style='margin: 8px 0 0 0; color: #666; font-size: 14px;'>{notif['msg']}</p>
            <p style='margin: 8px 0 0 0; color: #999; font-size: 12px;'>{notif['time']}</p>
        </div>
        """, unsafe_allow_html=True)

def user_navigation():
    """Navigation Instructions"""
    st.markdown("## 🧭 Navigation Instructions")
    
    if st.session_state.assigned_gate:
        gate = st.session_state.assigned_gate
        
        st.markdown(f"""
        <div class="card">
            <div class="card-header">📍 Route to Gate-{gate}</div>
            
            <p style='margin: 15px 0;'><b>Step 1:</b> From entrance, walk straight towards the main corridor</p>
            <p style='margin: 15px 0;'><b>Step 2:</b> Look for Gate-{gate} signage on your left</p>
            <p style='margin: 15px 0;'><b>Step 3:</b> Follow the colored lane markers (Blue lane)</p>
            <p style='margin: 15px 0;'><b>Step 4:</b> Proceed through Gate-{gate} for entry scanning</p>
            <p style='margin: 15px 0;'><b>Step 5:</b> Welcome to the arena!</p>
            
            <hr>
            
            <p style='margin: 10px 0;'><b>⏱ Estimated Walking Time:</b> 3-5 minutes</p>
            <p style='margin: 10px 0;'><b>📍 Current Crowds:</b> Moderate at Gate-{gate}</p>
            <p style='margin: 10px 0;'><b>💡 Tip:</b> Use side corridors to avoid main crowd if busy</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Book a ticket to see navigation instructions")

def user_emergency():
    """Emergency SOS"""
    st.markdown("## 🚨 Emergency & Safety")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Current Status")
        st.success("**No Active Emergencies**")
        st.markdown("Your area is safe. Enjoy the event!")
    
    with col2:
        st.markdown("### 📍 Nearby Exits")
        st.markdown("""
        - **Exit-1**: 45m away (Front)
        - **Exit-2**: 60m away (Right)
        - **Exit-3**: 75m away (Left)
        """)
    
    st.markdown("---")
    
    st.markdown("### 🆘 Emergency Actions")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("📞 Call Staff", width='stretch'):
            st.success("✓ Staff notified! Help arriving soon")
    
    with col_b:
        if st.button("🚨 Medical Emergency", width='stretch', help="Use for injuries"):
            st.error("🚨 Medical team dispatched to your location")
    
    with col_c:
        if st.button("🆘 Emergency SOS", width='stretch', type="secondary"):
            st.error("""
            🚨 EMERGENCY MODE ACTIVATED
            
            - Authorities notified
            - Evacuation route: Exit-1 (45m)
            - Follow emergency staff
            - Stay calm and orderly
            """)

# ============================================================================
# ADMIN PORTAL
# ============================================================================

def show_admin_portal():
    """Main admin/staff portal"""
    
    # Header
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        st.markdown("## 🏟️ Smart Stadium - Admin")
    with col2:
        st.markdown(f"### 👮 {st.session_state.user_name}")
    with col3:
        if st.button("🚪 Logout", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    selected = option_menu(
        menu_title="🛡️ Admin Menu",
        options=[
            "Crowd Dashboard",
            "Gate Control",
            "Crowd Redirection",
            "Emergency Panel",
            "Food Operations",
            "Staff Allocation",
            "Broadcast Message"
        ],
        icons=[
            "graph-up",
            "door-open",
            "arrow-left-right",
            "fire",
            "cup-straw",
            "people",
            "megaphone"
        ],
        orientation="horizontal"
    )
    
    st.markdown("---")
    
    # Pages
    if selected == "Crowd Dashboard":
        admin_crowd_dashboard()
    elif selected == "Gate Control":
        admin_gate_control()
    elif selected == "Crowd Redirection":
        admin_crowd_redirection()
    elif selected == "Emergency Panel":
        admin_emergency_panel()
    elif selected == "Food Operations":
        admin_food_operations()
    elif selected == "Staff Allocation":
        admin_staff_allocation()
    elif selected == "Broadcast Message":
        admin_broadcast()

# ============================================================================
# ADMIN PAGES
# ============================================================================

def admin_crowd_dashboard():
    """Crowd Monitoring Dashboard"""
    st.markdown("## 📊 Crowd Monitoring Dashboard")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "4,850", "+120 this hour")
    with col2:
        st.metric("Avg Gate Util", "58%", "↓ Improving")
    with col3:
        st.metric("Active Gates", "12/12", "All operational")
    with col4:
        st.metric("Critical Gates", "1", "Gate-C crowded")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Crowd Over Time")
        times = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30"]
        users = [800, 1200, 1800, 2500, 3200, 4100]
        
        fig = go.Figure(data=go.Scatter(x=times, y=users, mode='lines+markers', fill='tozeroy'))
        fig.update_layout(title="Users in Stadium", xaxis_title="Time", yaxis_title="Count", height=400)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("### 🚪 Gate Distribution")
        gates = ["A", "B", "C", "D", "E"]
        util = [67, 45, 85, 52, 38]
        colors = ["red" if u > 80 else "orange" if u > 60 else "green" for u in util]
        
        fig = go.Figure(data=go.Bar(x=gates, y=util, marker_color=colors))
        fig.update_layout(title="Gate Utilization (%)", xaxis_title="Gate", yaxis_title="%", height=400)
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    st.markdown("### 🎯 Gate Status Table")
    
    gate_data = {
        "Gate": ["A", "B", "C", "D", "E"],
        "Users": ["800/1200", "540/1200", "985/1200", "625/1200", "456/1200"],
        "Status": ["🟡 MEDIUM", "🟢 LOW", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"],
        "Wait": ["15 min", "8 min", "22 min", "12 min", "5 min"],
        "Action": ["Monitor", "Clear", "⚠️ URGENT", "Monitor", "Clear"],
    }
    
    st.dataframe(gate_data, width='stretch', hide_index=True)

def admin_gate_control():
    """Gate Control Panel"""
    st.markdown("## 🚪 Gate Control Panel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Control Individual Gates")
        
        gate = st.selectbox("Select Gate", ["A", "B", "C", "D", "E"], key="gate_select")
        
        current_status = "OPEN" if gate != "C" else "OPEN (CROWDED)"
        st.markdown(f"**Current Status:** {current_status}")
        
        action = st.radio("Action", ["Keep Open", "Pause Entry", "Close Gate"], horizontal=True)
        
        if st.button("✓ Apply", width='stretch', type="primary"):
            st.success(f"✓ Gate-{gate} {action} applied successfully!")
    
    with col2:
        st.markdown("### Quick Actions")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🟢 Open All Gates", width='stretch'):
                st.success("✓ All gates opened")
        
        with col_b:
            if st.button("🔴 Close All Gates", width='stretch'):
                st.warning("⚠️ All gates closed - Emergency mode")
        
        st.markdown("---")
        
        st.markdown("### Gate Status Overview")
        st.markdown("""
        - **Gate-A**: OPEN (67% capacity)
        - **Gate-B**: OPEN (45% capacity)
        - **Gate-C**: OPEN (85% capacity) ⚠️
        - **Gate-D**: OPEN (52% capacity)
        - **Gate-E**: OPEN (38% capacity)
        """)

def admin_crowd_redirection():
    """Crowd Redirection Control"""
    st.markdown("## 🔄 Crowd Redirection")
    
    st.markdown("### Manual User Redistribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        source_gate = st.selectbox("From (Source Gate)", ["A", "B", "C", "D", "E"], key="src_gate")
        num_users = st.slider("Number of Users to Redirect", 0, 500, 100, step=50)
    
    with col2:
        target_gate = st.selectbox("To (Target Gate)", ["A", "B", "C", "D", "E"], key="tgt_gate")
        st.markdown(f"**Target Capacity:** 45% → 52% estimated")
    
    st.markdown("---")
    
    if st.button("✓ Initiate Redirection", width='stretch', type="primary"):
        st.success(f"""
        ✓ Redirection Initiated
        
        - Moving {num_users} users from Gate-{source_gate} to Gate-{target_gate}
        - Estimated time: 8-10 minutes
        - Notifications sent to affected users
        """)
        st.balloons()

def admin_emergency_panel():
    """Emergency Monitoring"""
    st.markdown("## 🚨 Emergency Monitoring Panel")
    
    # Active emergencies
    st.markdown("### 🔴 Active Emergencies")
    
    emergencies = [
        {"id": "SOS-001", "type": "Medical", "location": "Zone-A (Gate-B)", "time": "2 min ago", "status": "Responded"},
        {"id": "SOS-002", "type": "Lost Person", "location": "Zone-C (Gate-D)", "time": "15 sec ago", "status": "In Progress"},
    ]
    
    for emerg in emergencies:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"**{emerg['id']}**")
        with col2:
            st.markdown(emerg['type'])
        with col3:
            st.markdown(emerg['location'])
        with col4:
            st.markdown(f"<span style='font-size: 12px; color: #666;'>{emerg['time']}</span>", unsafe_allow_html=True)
        with col5:
            st.button("✓ Resolve", key=emerg['id'])
    
    st.markdown("---")
    
    st.markdown("### 📞 Dispatch Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Send Medical Team", width='stretch'):
            st.info("✓ Medical team dispatched to Zone-A")
    
    with col2:
        if st.button("🚔 Send Security", width='stretch'):
            st.info("✓ Security team dispatched to Zone-C")

def admin_food_operations():
    """Food Operations Dashboard"""
    st.markdown("## 🍔 Food Operations Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Orders per Booth")
        
        booths = {
            "Booth": ["1", "2", "3", "4", "5"],
            "Pending": [12, 8, 25, 5, 10],
            "Completed": [45, 38, 52, 41, 39],
        }
        
        fig = go.Figure(data=[
            go.Bar(x=booths["Booth"], y=booths["Pending"], name="Pending"),
            go.Bar(x=booths["Booth"], y=booths["Completed"], name="Completed"),
        ])
        fig.update_layout(title="Orders Status", barmode='stack', height=400)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("### ⚠️ Crowded Booths")
        
        crowded = [
            {"booth": "3", "pending": 25, "wait": "18 min", "action": "🚨 Staff Alert"},
            {"booth": "1", "pending": 12, "wait": "8 min", "action": "Monitor"},
            {"booth": "5", "pending": 10, "wait": "7 min", "action": "OK"},
        ]
        
        for c in crowded:
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.markdown(f"**Booth-{c['booth']}**")
            with col_b:
                st.markdown(f"{c['pending']} pending")
            with col_c:
                st.markdown(f"Wait: {c['wait']}")
            with col_d:
                st.markdown(c['action'])

def admin_staff_allocation():
    """Staff Allocation Insights"""
    st.markdown("## 👥 Staff Allocation Insights")
    
    st.markdown("### 📍 Staff Per Gate (Current vs Recommended)")
    
    staff_data = {
        "Gate": ["A", "B", "C", "D", "E"],
        "Current": [8, 6, 12, 7, 5],
        "Recommended": [8, 6, 15, 7, 5],
        "Utilization": ["67%", "45%", "85% ⚠️", "52%", "38%"],
    }
    
    col_cols = st.columns(1)
    
    for gate, curr, rec, util in zip(staff_data["Gate"], staff_data["Current"], staff_data["Recommended"], staff_data["Utilization"]):
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a:
            st.markdown(f"**Gate-{gate}**")
        with col_b:
            st.markdown(f"{curr} staff")
        with col_c:
            st.markdown(f"→ {rec} needed")
        with col_d:
            st.markdown(util)
        with col_e:
            if rec > curr:
                st.warning(f"+{rec-curr}")
            else:
                st.success("✓")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Reallocation")
    
    if st.button("✓ Auto-Allocate Staff", width='stretch', type="primary"):
        st.success("""
        ✓ Staff reallocation completed
        
        - +3 staff assigned to Gate-C
        - Notifications sent to staff
        - New routes shared
        """)

def admin_broadcast():
    """Broadcast Notification System"""
    st.markdown("## 📢 Broadcast Notification System")
    
    with st.form("broadcast_form"):
        message_type = st.radio("Message Type", ["General", "Gate Specific", "Emergency"], horizontal=True)
        
        if message_type == "Gate Specific":
            target_gate = st.multiselect("Send to Gates", ["A", "B", "C", "D", "E"], default=["A"])
        
        message = st.text_area("📝 Message", placeholder="Type your message here...", height=100)
        
        priority = st.radio("Priority", ["Normal", "High", "Urgent"], horizontal=True)
        
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("✓ Send Message", width='stretch', type="primary")
        with col_btn2:
            st.form_submit_button("Cancel", width='stretch')
        
        if submitted:
            if message:
                recipient = f"All Users" if message_type == "General" else f"Gate(s): {', '.join(target_gate)}"
                st.success(f"""
                ✓ Message Broadcast Successfully
                
                **Recipients:** {recipient}
                **Priority:** {priority}
                **Time:** {datetime.now().strftime('%H:%M:%S')}
                **Status:** Delivered to all connected users
                """)
            else:
                st.error("❌ Please enter a message")

# ============================================================================
# MAIN RUNNER
# ============================================================================

if __name__ == "__main__":
    main()
