"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Bookings API Routes - Manage ticket bookings with server-side authentication
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List
from app.models.ticket import TicketBookingRequest, TicketResponse, TicketListResponse
from app.services.ticket_service import TicketService
from app.utils.auth_middleware import verify_token

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_booking(
    booking: TicketBookingRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Create a new event booking for the authenticated user.
    Uses TicketService for Firebase RTDB integration.
    """
    # Ensure user is booking for themselves unless admin
    if booking.user_id != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You can only book tickets for your own account"
        )
        
    try:
        result = await TicketService.book_ticket(booking)
        return {
            "ticket_id": result["ticket_id"],
            "user_id": result["user_id"],
            "event_id": result["event_id"],
            "assigned_gate": result["assigned_gate"],
            "message": "Booking confirmed!"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/user/{user_id}", response_model=Dict[str, Any])
async def get_user_bookings(
    user_id: str, 
    current_user: dict = Depends(verify_token)
):
    """
    Get all bookings for a specific user.
    """
    if current_user.get("uid") != user_id and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    try:
        tickets = await TicketService.get_user_tickets(user_id)
        return {"bookings": tickets, "total": len(tickets)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{ticket_id}/cancel", response_model=Dict[str, Any])
async def cancel_booking(
    ticket_id: str, 
    current_user: dict = Depends(verify_token)
):
    """
    Cancel an existing booking.
    """
    try:
        ticket = await TicketService.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        
        if ticket.get("user_id") != current_user.get("uid") and not current_user.get("is_admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
        success = await TicketService.cancel_ticket(ticket_id)
        if success:
            return {"message": "Booking cancelled successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cancellation failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
