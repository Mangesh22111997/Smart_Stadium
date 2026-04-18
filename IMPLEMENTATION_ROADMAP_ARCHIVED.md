# 🚀 Smart Stadium - Complete Implementation Roadmap

## 📊 7-PHASE BUILD PLAN

### Phase 1: Backend API Endpoints
### Phase 2: Connect Events to Database  
### Phase 3: Bookings System
### Phase 4: Security Portal
### Phase 5: Google Maps Integration
### Phase 6: Food Ordering
### Phase 7: UI Polish & Optimization

---

# ⚙️ PHASE 1: BACKEND API ENDPOINTS (FastAPI)

## What to Add
We need to add 5 new endpoints to `app/routes/` for:
1. List events
2. Create booking
3. Get user bookings
4. Update gate status
5. Get crowd data

## Implementation

### Step 1.1: Create `app/routes/events_routes.py`

```python
"""
Events API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.config.firebase_config import get_db_connection

router = APIRouter(prefix="/events", tags=["events"])

class EventCreate(BaseModel):
    event_name: str
    event_date: str
    start_time: str
    end_time: str
    venue_type: str
    seating_capacity: int
    number_of_gates: int
    parking_available: bool
    parking_capacity: int
    nearby_metro_count: int
    nearby_bus_stops: int

class EventResponse(BaseModel):
    event_id: str
    event_name: str
    event_date: str
    start_time: str
    venue_type: str
    seating_capacity: int
    available_seats: int
    price_per_ticket: Optional[int] = 500

@router.post("/create", status_code=201)
async def create_event(event: EventCreate, session_token: str = Query(...)):
    """Admin: Create new event"""
    try:
        db = get_db_connection()
        
        # Verify admin status (TODO: validate from session_token)
        
        event_data = {
            "event_name": event.event_name,
            "event_date": event.event_date,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "venue_type": event.venue_type,
            "seating_capacity": event.seating_capacity,
            "available_seats": event.seating_capacity,
            "number_of_gates": event.number_of_gates,
            "parking_available": event.parking_available,
            "parking_capacity": event.parking_capacity,
            "nearby_metro_count": event.nearby_metro_count,
            "nearby_bus_stops": event.nearby_bus_stops,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        # Store in Firebase
        result = db.child("events").push(event_data)
        
        return {
            "event_id": result["name"],
            "message": "Event created successfully",
            "event_data": event_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_events(limit: int = Query(50)):
    """Get all upcoming events"""
    try:
        db = get_db_connection()
        events_ref = db.child("events").get()
        
        if events_ref.val() is None:
            return {"events": []}
        
        events = []
        for event_id, event_data in events_ref.val().items():
            if event_data and event_data.get("status") != "completed":
                events.append({
                    "event_id": event_id,
                    **event_data
                })
        
        # Sort by date
        events.sort(key=lambda x: x.get("event_date", ""))
        
        return {"events": events[:limit], "total": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{event_id}")
async def get_event_details(event_id: str):
    """Get specific event details"""
    try:
        db = get_db_connection()
        event = db.child("events").child(event_id).get().val()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "event_id": event_id,
            **event
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{event_id}/status")
async def update_event_status(event_id: str, status: str, session_token: str = Query(...)):
    """Update event status (admin only)"""
    try:
        db = get_db_connection()
        db.child("events").child(event_id).update({"status": status})
        
        return {"message": f"Event status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 1.2: Create `app/routes/bookings_routes.py`

```python
"""
Bookings API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.config.firebase_config import get_db_connection

router = APIRouter(prefix="/bookings", tags=["bookings"])

class BookingCreate(BaseModel):
    event_id: str
    num_tickets: int
    commute_mode: str
    parking_required: bool
    departure_preference: str

class BookingResponse(BaseModel):
    ticket_id: str
    user_id: str
    event_id: str
    num_tickets: int
    total_price: int
    assigned_gate: str
    confirmation_number: str

@router.post("/create", status_code=201)
async def create_booking(
    booking: BookingCreate,
    user_id: str = Query(...),
    session_token: str = Query(...)
):
    """Create new booking"""
    try:
        db = get_db_connection()
        
        # Get event details
        event = db.child("events").child(booking.event_id).get().val()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check availability
        available = event.get("available_seats", 0)
        if available < booking.num_tickets:
            raise HTTPException(status_code=400, detail=f"Only {available} seats available")
        
        # Calculate total price
        price_per_ticket = event.get("price_per_ticket", 500)
        total_price = price_per_ticket * booking.num_tickets
        
        # Assign gate (simple round-robin for now)
        num_gates = event.get("number_of_gates", 5)
        gate_num = available % num_gates + 1
        assigned_gate = f"Gate {chr(64 + gate_num)}"  # Gate A, B, C, etc.
        
        # Create booking record
        booking_data = {
            "user_id": user_id,
            "event_id": booking.event_id,
            "num_tickets": booking.num_tickets,
            "total_price": total_price,
            "assigned_gate": assigned_gate,
            "commute_mode": booking.commute_mode,
            "parking_required": booking.parking_required,
            "departure_preference": booking.departure_preference,
            "booking_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # Store booking
        result = db.child("bookings").push(booking_data)
        ticket_id = result["name"]
        
        # Update available seats
        new_available = available - booking.num_tickets
        db.child("events").child(booking.event_id).update({
            "available_seats": new_available
        })
        
        return {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "event_id": booking.event_id,
            "num_tickets": booking.num_tickets,
            "total_price": total_price,
            "assigned_gate": assigned_gate,
            "confirmation_number": ticket_id[:12].upper(),
            "message": "Booking confirmed!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_bookings(user_id: str, session_token: str = Query(...)):
    """Get all bookings for user"""
    try:
        db = get_db_connection()
        bookings_ref = db.child("bookings").get()
        
        if bookings_ref.val() is None:
            return {"bookings": []}
        
        user_bookings = []
        for ticket_id, booking_data in bookings_ref.val().items():
            if booking_data and booking_data.get("user_id") == user_id:
                user_bookings.append({
                    "ticket_id": ticket_id,
                    **booking_data
                })
        
        return {"bookings": user_bookings, "total": len(user_bookings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ticket_id}/cancel")
async def cancel_booking(ticket_id: str, user_id: str = Query(...)):
    """Cancel a booking"""
    try:
        db = get_db_connection()
        booking = db.child("bookings").child(ticket_id).get().val()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Update booking status
        db.child("bookings").child(ticket_id).update({"status": "cancelled"})
        
        # Restore available seats
        event_id = booking.get("event_id")
        event = db.child("events").child(event_id).get().val()
        new_available = event.get("available_seats", 0) + booking.get("num_tickets", 1)
        db.child("events").child(event_id).update({"available_seats": new_available})
        
        return {"message": "Booking cancelled successfully", "refund": booking.get("total_price")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 1.3: Create `app/routes/gates_routes.py`

```python
"""
Gates Management API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from app.config.firebase_config import get_db_connection

router = APIRouter(prefix="/gates", tags=["gates"])

class GateUpdate(BaseModel):
    status: str  # "open", "closed", "restricted"
    crowd_percentage: int

@router.get("/all")
async def get_all_gates():
    """Get status of all gates"""
    try:
        db = get_db_connection()
        gates_ref = db.child("gates").get()
        
        if gates_ref.val() is None:
            # Initialize default gates
            default_gates = {}
            for i in range(1, 6):
                gate_name = f"Gate {chr(64 + i)}"
                default_gates[gate_name.lower()] = {
                    "name": gate_name,
                    "status": "open",
                    "crowd_percentage": 0,
                    "capacity": 500
                }
            return {"gates": default_gates}
        
        return {"gates": gates_ref.val()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{gate_name}")
async def update_gate(gate_name: str, update: GateUpdate, session_token: str = Query(...)):
    """Update gate status (admin/security only)"""
    try:
        db = get_db_connection()
        
        gate_data = {
            "status": update.status,
            "crowd_percentage": update.crowd_percentage,
            "updated_at": datetime.now().isoformat()
        }
        
        db.child("gates").child(gate_name.lower()).update(gate_data)
        
        # If crowd > 80%, send alert
        if update.crowd_percentage > 80:
            db.child("alerts").push({
                "type": "congestion",
                "gate": gate_name,
                "crowd": update.crowd_percentage,
                "timestamp": datetime.now().isoformat()
            })
        
        return {"message": f"{gate_name} updated", "data": gate_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{gate_name}/crowd")
async def get_gate_crowd(gate_name: str):
    """Get current crowd at specific gate"""
    try:
        db = get_db_connection()
        gate = db.child("gates").child(gate_name.lower()).get().val()
        
        if not gate:
            raise HTTPException(status_code=404, detail="Gate not found")
        
        return {
            "gate": gate_name,
            "crowd_percentage": gate.get("crowd_percentage", 0),
            "status": gate.get("status"),
            "updated_at": gate.get("updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 1.4: Update `app/main.py` to Register Routes

```python
# Add these imports at the top
from app.routes import events_routes, bookings_routes, gates_routes

# Add after other route registrations (around line where you include auth_routes)
app.include_router(events_routes.router)
app.include_router(bookings_routes.router)
app.include_router(gates_routes.router)
```

---

## ✅ PHASE 1 CHECKLIST
- [ ] Create events_routes.py with 4 endpoints
- [ ] Create bookings_routes.py with 4 endpoints  
- [ ] Create gates_routes.py with 2 endpoints
- [ ] Update main.py to register routes
- [ ] Test all endpoints at http://localhost:8000/docs

**Estimated Time:** 45 minutes

---

# 📱 PHASE 2: CONNECT EVENTS PAGE TO FIREBASE

## Update `streamlit_app/pages/4_Events.py`

```python
"""
Events Discovery Page - Now with Real Backend Data
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
import pandas as pd

st.set_page_config(page_title="Events - Smart Stadium", page_icon="🎉", layout="wide")

if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

st.markdown("# 🎉 Discover Events")
st.markdown("*Explore upcoming events at Smart Stadium*")

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

# Fetch events from backend
api_client = get_api_client()

with st.spinner("📡 Loading events..."):
    try:
        # Call new /events/list endpoint
        response = api_client.session.get(
            f"{api_client.base_url}/events/list",
            params={"limit": 50},
            timeout=10
        ).json()
        
        events = response.get("events", [])
        
        if not events:
            st.info("No events found. Check back soon!")
        else:
            st.success(f"✅ Found {len(events)} events")
            
            # Display events
            for event in events:
                col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                
                with col1:
                    st.markdown(f"### {event.get('event_name', 'Unnamed Event')}")
                    st.write(f"📅 **Date:** {event.get('event_date')} at {event.get('start_time')}")
                    st.write(f"📍 **Venue:** {event.get('venue_type')}")
                    st.write(f"💺 **Available:** {event.get('available_seats', 0)} / {event.get('seating_capacity', 0)} seats")
                    st.write(f"💰 **Price:** ₹{event.get('price_per_ticket', 500)} per ticket")
                
                with col2:
                    st.markdown("")
                    st.markdown("")
                    availability = (event.get('available_seats', 0) / event.get('seating_capacity', 1)) * 100
                    st.metric("Avail %", f"{availability:.0f}%")
                
                with col3:
                    st.markdown("")
                    st.markdown("")
                    if event.get('available_seats', 0) > 0:
                        if st.button("🎟️ Book Now", use_container_width=True, key=f"book_{event['event_id']}"):
                            st.session_state["selected_event"] = event
                            st.switch_page("pages/5_Bookings.py")
                    else:
                        st.button("❌ Sold Out", use_container_width=True, disabled=True)
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"❌ Failed to load events: {str(e)}")
        st.info("Make sure the backend is running at http://localhost:8000")

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    All events fetched from Live Database ✅
</div>
""", unsafe_allow_html=True)
```

### Also Update `utils/api_client.py` to Add Events Methods

```python
# Add this method to APIClient class in utils/api_client.py

def list_events(self, limit: int = 50) -> Dict[str, Any]:
    """Get all upcoming events"""
    try:
        response = self.session.get(
            f"{self.base_url}/events/list",
            params={"limit": limit},
            timeout=TIMEOUT
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_event_details(self, event_id: str) -> Dict[str, Any]:
    """Get specific event details"""
    try:
        response = self.session.get(
            f"{self.base_url}/events/{event_id}",
            timeout=TIMEOUT
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def create_booking(self, event_id: str, num_tickets: int, 
                  commute_mode: str, parking_required: bool,
                  departure_preference: str, user_id: str,
                  session_token: str) -> Dict[str, Any]:
    """Create new booking"""
    try:
        response = self.session.post(
            f"{self.base_url}/bookings/create",
            json={
                "event_id": event_id,
                "num_tickets": num_tickets,
                "commute_mode": commute_mode,
                "parking_required": parking_required,
                "departure_preference": departure_preference
            },
            params={
                "user_id": user_id,
                "session_token": session_token
            },
            timeout=TIMEOUT
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

---

## ✅ PHASE 2 CHECKLIST
- [ ]Update pages/4_Events.py to fetch real events
- [ ] Add methods to api_client.py
- [ ] Test Events page loads real data
- [ ] Verify booking button passes event data

**Estimated Time:** 30 minutes

---

# 🎟️ PHASE 3: BOOKINGS SYSTEM

## Update `streamlit_app/pages/5_Bookings.py`

```python
"""
Ticket Bookings Page - With Real API Integration
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from datetime import datetime

st.set_page_config(page_title="Bookings - Smart Stadium", page_icon="🎟️", layout="wide")

if not SessionManager.is_logged_in():
    st.error("❌ Please log in first")
    st.switch_page("pages/1_Login.py")
    st.stop()

st.markdown("# 🎟️ Ticket Bookings")

if st.button("🚪 Logout"):
    api_client = get_api_client()
    api_client.logout(SessionManager.get_session_token())
    SessionManager.logout()
    st.switch_page("pages/1_Login.py")

st.divider()

api_client = get_api_client()

# Check if booking from events page
if "selected_event" not in st.session_state or st.session_state["selected_event"] is None:
    st.info("No event selected. Go to Events page to book.")
    if st.button("🎉 Browse Events"):
        st.switch_page("pages/4_Events.py")
    st.stop()

event = st.session_state["selected_event"]

st.markdown(f"## Booking: {event.get('event_name')}")

with st.form("booking_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📍 **Venue:** {event.get('venue_type')}")
        st.write(f"📅 **Date:** {event.get('event_date')} at {event.get('start_time')}")
    
    with col2:
        st.write(f"💺 **Available:** {event.get('available_seats', 0)} seats")
        st.write(f"💰 **Price:** ₹{event.get('price_per_ticket', 500)}/ticket")
    
    st.divider()
    
    num_tickets = st.number_input(
        "Number of Tickets",
        min_value=1,
        max_value=min(10, event.get('available_seats', 0)),
        value=1
    )
    
    total_price = num_tickets * event.get('price_per_ticket', 500)
    st.metric("💰 Total Price", f"₹{total_price}")
    
    st.markdown("### Seat Preferences")
    commute_mode = st.selectbox("Commute Mode", ["Public Transport", "Car", "Bike", "Walking"])
    parking_required = st.checkbox("Parking Required")
    departure_pref = st.selectbox("Departure Preference", ["Morning", "Afternoon", "Evening"])
    
    col1, col2 = st.columns(2)
    with col1:
        submit_btn = st.form_submit_button("✅ Confirm Booking", use_container_width=True)
    with col2:
        cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
    
    if submit_btn:
        with st.spinner("📝 Processing your booking..."):
            result = api_client.create_booking(
                event_id=event.get('event_id'),
                num_tickets=num_tickets,
                commute_mode=commute_mode,
                parking_required=parking_required,
                departure_preference=departure_pref,
                user_id=SessionManager.get_user_id(),
                session_token=SessionManager.get_session_token()
            )
        
        if "ticket_id" in result:
            st.success(f"✅ Booking Confirmed!")
            st.balloons()
            
            # Display confirmation
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🎟️ **Ticket ID:** {result['ticket_id']}")
                st.info(f"📋 **Confirmation:** {result['confirmation_number']}")
            with col2:
                st.info(f"🚪 **Assigned Gate:** {result['assigned_gate']}")
                st.info(f"💰 **Total:** ₹{result['total_price']}")
            
            st.markdown("---")
            st.success("Remember your ticket ID for entry!")
            
            if st.button("🏠 Back to Home"):
                st.session_state["selected_event"] = None
                st.switch_page("pages/3_Home.py")
        else:
            st.error(f"❌ Booking failed: {result.get('detail', 'Unknown error')}")

# Show booking history
st.divider()
st.markdown("## 📜 Your Booking History")

with st.spinner("Loading your bookings..."):
    try:
        bookings_response = api_client.session.get(
            f"{api_client.base_url}/bookings/user/{SessionManager.get_user_id()}",
            params={"session_token": SessionManager.get_session_token()},
            timeout=10
        ).json()
        
        bookings = bookings_response.get("bookings", [])
        
        if not bookings:
            st.info("No booking history yet.")
        else:
            for booking in bookings:
                with st.expander(f"🎟️ {booking.get('event_id')} - {booking.get('booking_date', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tickets:** {booking.get('num_tickets')}")
                        st.write(f"**Gate:** {booking.get('assigned_gate')}")
                    with col2:
                        st.write(f"**Total:** ₹{booking.get('total_price')}")
                        st.write(f"**Status:** {booking.get('status')}")
    except Exception as e:
        st.warning(f"Could not load booking history: {str(e)}")
```

---

## ✅ PHASE 3 CHECKLIST
- [ ] Update pages/5_Bookings.py with API integration
- [ ] Test booking creation with real data
- [ ] Verify ticket confirmation displays
- [ ] Test booking history retrieval

**Estimated Time:** 30 minutes

---

# 🔐 PHASE 4: SECURITY PORTAL (3 New Pages)

[Continuing in next message due to length...]

Would you like me to continue with:
1. **Security Portal implementation** (3 pages)?
2. **Google Maps integration** module?
3. **Food Ordering system** backend?
4. **Start implementing Phase 1** right now?

What should I prioritize?
