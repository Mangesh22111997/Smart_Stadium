"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Ticket Service - Business logic for ticket booking with Firebase RTDB integration
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

from app.models.ticket import Ticket, TicketBookingRequest, TicketUpdateRequest
from app.config.firebase_config import get_db_connection, Collections

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=10)

class TicketService:
    """
    Service class for managing ticket bookings in Firebase Realtime Database.
    All operations are non-blocking for the FastAPI event loop.
    """

    @staticmethod
    async def book_ticket(request: TicketBookingRequest) -> Dict[str, Any]:
        """
        Book a new ticket in Firebase RTDB
        
        Args:
            request: TicketBookingRequest with booking details
            
        Returns:
            Dictionary with ticket_id and confirmation data
        """
        loop = asyncio.get_event_loop()
        db = get_db_connection()
        
        # Prepare booking data
        booking_data = {
            "user_id": request.user_id,
            "event_id": request.event_id,
            "commute_mode": request.commute_mode,
            "parking_required": request.parking_required,
            "departure_preference": request.departure_preference,
            "booking_date": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        def _perform_write():
            # Push to Firebase
            result = db.child(Collections.TICKETS).push(booking_data)
            ticket_id = result["name"]
            
            # Logic for gate assignment (simplified)
            assigned_gate = f"Gate {chr(65 + (hash(ticket_id) % 5))}"
            db.child(Collections.TICKETS).child(ticket_id).update({"assigned_gate": assigned_gate})
            
            return {
                "ticket_id": ticket_id,
                "assigned_gate": assigned_gate,
                **booking_data
            }
            
        return await loop.run_in_executor(executor, _perform_write)

    @staticmethod
    async def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ticket by ID from Firebase RTDB
        """
        loop = asyncio.get_event_loop()
        db = get_db_connection()
        
        def _perform_read():
            ticket = db.child(Collections.TICKETS).child(ticket_id).get().val()
            if ticket:
                ticket["ticket_id"] = ticket_id
            return ticket
            
        return await loop.run_in_executor(executor, _perform_read)

    @staticmethod
    async def get_user_tickets(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tickets for a specific user from Firebase RTDB
        """
        loop = asyncio.get_event_loop()
        db = get_db_connection()
        
        def _perform_read():
            tickets_ref = db.child(Collections.TICKETS).get()
            if not tickets_ref.val():
                return []
                
            user_tickets = []
            for tid, data in tickets_ref.val().items():
                if data.get("user_id") == user_id:
                    data["ticket_id"] = tid
                    user_tickets.append(data)
            return user_tickets
            
        return await loop.run_in_executor(executor, _perform_read)

    @staticmethod
    async def cancel_ticket(ticket_id: str) -> bool:
        """
        Cancel a ticket in Firebase RTDB
        """
        loop = asyncio.get_event_loop()
        db = get_db_connection()
        
        def _perform_update():
            ticket = db.child(Collections.TICKETS).child(ticket_id).get().val()
            if not ticket:
                return False
            
            db.child(Collections.TICKETS).child(ticket_id).update({"status": "cancelled"})
            return True
            
        return await loop.run_in_executor(executor, _perform_update)
