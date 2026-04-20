"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Events API Routes - Manage stadium events
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
    price_per_ticket: int = 500

@router.post("/create", status_code=201)
async def create_event(event: EventCreate, session_token: str = Query(...)):
    """Admin: Create new event"""
    try:
        db = get_db_connection()
        
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
            "price_per_ticket": event.price_per_ticket,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
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
