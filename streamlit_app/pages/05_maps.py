import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.maps_helper import StadiumMapHelper

st.set_page_config(page_title="Maps - Smart Stadium", page_icon="🗺️", layout="wide")

if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/00_login.py")
    st.stop()

st.markdown("# 🗺️ Stadium Maps & Navigation")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/00_login.py")

st.divider()

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["Stadium Map", "Gate Details", "Parking", "Directions"])

with tab1:
    st.markdown("## 📍 Full Stadium Map")
    st.markdown("View the complete stadium layout with all gates, parking, and transit options")
    
    # Show stadium map
    if highlighted_gate and highlighted_gate != "None":
        lat, lng = StadiumMapHelper.GATES[highlighted_gate]
    else:
        lat, lng = StadiumMapHelper.STADIUM_LAT, StadiumMapHelper.STADIUM_LNG
    
    embed_url = StadiumMapHelper.get_embed_url(lat, lng)
    st.components.v1.iframe(embed_url, width=1200, height=500)
    
    st.markdown("""
    **Legend:**
    - 🔵 Blue Marker: Stadium Center
    - 🟢 Green Markers: Available Gates
    - 🔴 Red Marker: Highlighted Gate
    - 🟠 Orange Markers: Parking Areas
    - 🟣 Purple Markers: Metro Stations
    - 🔷 Blue Markers: Bus Stops
    """)

with tab2:
    st.markdown("## 🚪 Gate Detailed View")
    
    selected_gate = st.selectbox(
        "Select a gate to view details:",
        ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]
    )
    
    # Gate coordinates (from StadiumMapHelper)
    gate_coords = {
        "Gate A": (28.5250, 77.1850),
        "Gate B": (28.5260, 77.1860),
        "Gate C": (28.5240, 77.1870),
        "Gate D": (28.5230, 77.1860),
        "Gate E": (28.5240, 77.1840),
    }
    
    gate_lat, gate_lng = gate_coords[selected_gate]
    
    # Show gate map
    embed_url = StadiumMapHelper.get_embed_url(gate_lat, gate_lng, zoom=18)
    st.components.v1.iframe(embed_url, width=1200, height=500)
    
    # Gate info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gate Status", "🟢 Open")
    with col2:
        st.metric("Current Queue", "45 people")
    with col3:
        st.metric("Avg Wait Time", "3-5 mins")
    
    st.write(f"**Nearby Parking:** {['Parking North', 'Parking East'][hash(selected_gate) % 2]}")

with tab3:
    st.markdown("## 🅿️ Parking Availability")
    
    # Mock parking utilization
    parking_utilization = {
        "Parking North": 65,
        "Parking South": 45,
        "Parking East": 82,
        "Parking West": 30,
    }
    
    selected_parking = st.selectbox("Select Parking Zone:", list(StadiumMapHelper.PARKING.keys()))
    p_lat, p_lng = StadiumMapHelper.PARKING[selected_parking]
    
    embed_url = StadiumMapHelper.get_embed_url(p_lat, p_lng)
    st.components.v1.iframe(embed_url, width=1200, height=500)
    
    st.markdown("### Parking Status")
    col1, col2 = st.columns(2)
    
    with col1:
        for parking, utilization in list(parking_utilization.items())[:2]:
            if utilization > 80:
                st.error(f"🔴 {parking}: {utilization}% Full")
            elif utilization > 50:
                st.warning(f"🟡 {parking}: {utilization}% Full")
            else:
                st.success(f"🟢 {parking}: {100-utilization}% Available")
    
    with col2:
        for parking, utilization in list(parking_utilization.items())[2:]:
            if utilization > 80:
                st.error(f"🔴 {parking}: {utilization}% Full")
            elif utilization > 50:
                st.warning(f"🟡 {parking}: {utilization}% Full")
            else:
                st.success(f"🟢 {parking}: {100-utilization}% Available")

with tab4:
    st.markdown("## 🧭 Get Directions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        starting_point = st.selectbox(
            "Starting from:",
            [
                "Metro Station A",
                "Metro Station B",
                "Bus Stop 1",
                "Bus Stop 2",
                "Bus Stop 3",
                "Parking North",
                "Parking South",
                "Parking East",
                "Parking West",
            ]
        )
    
    with col2:
        destination = st.selectbox(
            "Going to:",
            ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]
        )
    
    st.divider()
    
    # Get estimates
    estimates = StadiumMapHelper.get_commute_estimates(starting_point)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Estimated Time", estimates.get("estimated_time", "N/A"))
    with col2:
        st.metric("Distance", estimates.get("distance", "N/A"))
    with col3:
        st.metric("Mode", estimates.get("travel_mode", "N/A"))
    with col4:
        st.metric("Crowd Level", estimates.get("crowding", "N/A"))
    
    st.divider()
    
    # Directions text
    st.markdown("### Turn-by-Turn Directions")
    st.write(StadiumMapHelper.get_directions_text(starting_point, "Stadium"))
    
    # Recommendation
    st.info(f"ℹ️ **Recommendation:** Leave {estimates.get('travel_mode')} at least {estimates.get('estimated_time')} before the event starts.")

st.divider()

col1, col2 = st.columns(2)
with col1:
    if st.button("🎉 Browse Events", use_container_width=True):
        st.switch_page("pages/03_events.py")
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/02_home.py")
