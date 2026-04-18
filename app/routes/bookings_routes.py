"""
Bookings API Routes - Manage ticket bookings
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
    food_order_id: Optional[str] = None

@router.post("/create", status_code=201)
async def create_booking(
    booking: BookingCreate,
    user_id: str = Query(...),
    session_token: str = Query(...)
):
    """Create new booking"""
    try:
        db = get_db_connection()
        
        event = db.child("events").child(booking.event_id).get().val()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        available = event.get("available_seats", 0)
        if available < booking.num_tickets:
            raise HTTPException(status_code=400, detail=f"Only {available} seats available")
        
        price_per_ticket = event.get("price_per_ticket", 500)
        total_price = price_per_ticket * booking.num_tickets
        
        num_gates = event.get("number_of_gates", 5)
        gate_num = available % num_gates + 1
        assigned_gate = f"Gate {chr(64 + gate_num)}"
        
        booking_data = {
            "user_id": user_id,
            "event_id": booking.event_id,
            "num_tickets": booking.num_tickets,
            "total_price": total_price,
            "assigned_gate": assigned_gate,
            "commute_mode": booking.commute_mode,
            "parking_required": booking.parking_required,
            "departure_preference": booking.departure_preference,
            "food_order_id": booking.food_order_id,
            "booking_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        result = db.child("bookings").push(booking_data)
        ticket_id = result["name"]
        
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
                # Ensure all fields are present for consistency
                user_bookings.append({
                    "ticket_id": ticket_id,
                    "food_order_id": booking_data.get("food_order_id"),
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
        
        db.child("bookings").child(ticket_id).update({"status": "cancelled"})
        
        event_id = booking.get("event_id")
        event = db.child("events").child(event_id).get().val()
        new_available = event.get("available_seats", 0) + booking.get("num_tickets", 1)
        db.child("events").child(event_id).update({"available_seats": new_available})
        
        return {"message": "Booking cancelled successfully", "refund": booking.get("total_price")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
