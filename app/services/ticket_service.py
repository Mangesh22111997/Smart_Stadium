"""
Ticket Service - Business logic for ticket booking
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from app.models.ticket import Ticket, TicketBookingRequest, TicketUpdateRequest

# ============================================================================
# IN-MEMORY TICKET DATABASE
# ============================================================================

tickets_db: Dict[UUID, Ticket] = {}


# ============================================================================
# TICKET SERVICE CLASS
# ============================================================================

class TicketService:
    """
    Service class for managing ticket bookings
    """

    @staticmethod
    def book_ticket(request: TicketBookingRequest) -> Ticket:
        """
        Book a new ticket
        
        Args:
            request: TicketBookingRequest with booking details
            
        Returns:
            Created Ticket object
        """
        ticket_id = uuid4()
        ticket = Ticket(
            ticket_id=ticket_id,
            user_id=request.user_id,
            event_id=request.event_id,
            commute_mode=request.commute_mode,
            parking_required=request.parking_required,
            departure_preference=request.departure_preference,
            booking_date=datetime.now(),
            status="confirmed"
        )
        tickets_db[ticket_id] = ticket
        
        print(f"✅ Ticket booked: {ticket_id} for user {request.user_id}")
        return ticket

    @staticmethod
    def get_ticket(ticket_id: UUID) -> Optional[Ticket]:
        """
        Get ticket by ID
        
        Args:
            ticket_id: UUID of the ticket
            
        Returns:
            Ticket object or None if not found
        """
        return tickets_db.get(ticket_id)

    @staticmethod
    def list_all_tickets() -> List[Ticket]:
        """
        Get all tickets
        
        Returns:
            List of Ticket objects
        """
        return list(tickets_db.values())

    @staticmethod
    def get_user_tickets(user_id: UUID) -> List[Ticket]:
        """
        Get all tickets for a specific user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of Ticket objects for that user
        """
        return [
            ticket for ticket in tickets_db.values()
            if ticket.user_id == user_id
        ]

    @staticmethod
    def update_ticket(ticket_id: UUID, request: TicketUpdateRequest) -> Optional[Ticket]:
        """
        Update ticket details
        
        Args:
            ticket_id: UUID of the ticket
            request: TicketUpdateRequest with updated fields
            
        Returns:
            Updated Ticket object or None if not found
        """
        if ticket_id not in tickets_db:
            return None
        
        ticket = tickets_db[ticket_id]
        
        # Update only provided fields
        if request.commute_mode is not None:
            ticket.commute_mode = request.commute_mode
        if request.parking_required is not None:
            ticket.parking_required = request.parking_required
        if request.departure_preference is not None:
            ticket.departure_preference = request.departure_preference
        
        print(f"✅ Ticket updated: {ticket_id}")
        return ticket

    @staticmethod
    def cancel_ticket(ticket_id: UUID) -> bool:
        """
        Cancel a ticket
        
        Args:
            ticket_id: UUID of the ticket
            
        Returns:
            True if cancelled, False if not found
        """
        if ticket_id not in tickets_db:
            return False
        
        ticket = tickets_db[ticket_id]
        ticket.status = "cancelled"
        
        print(f"✅ Ticket cancelled: {ticket_id}")
        return True

    @staticmethod
    def get_tickets_by_commute_mode(commute_mode: str) -> List[Ticket]:
        """
        Get all tickets with a specific commute mode
        
        Args:
            commute_mode: Commute mode (metro, bus, private, cab)
            
        Returns:
            List of matching Ticket objects
        """
        return [
            ticket for ticket in tickets_db.values()
            if ticket.commute_mode == commute_mode and ticket.status != "cancelled"
        ]

    @staticmethod
    def get_tickets_by_departure_preference(preference: str) -> List[Ticket]:
        """
        Get all tickets with a specific departure preference
        
        Args:
            preference: Departure preference (early, immediate, delayed)
            
        Returns:
            List of matching Ticket objects
        """
        return [
            ticket for ticket in tickets_db.values()
            if ticket.departure_preference == preference and ticket.status != "cancelled"
        ]

    @staticmethod
    def get_parking_required_tickets() -> List[Ticket]:
        """
        Get all tickets that require parking
        
        Returns:
            List of Ticket objects requiring parking
        """
        return [
            ticket for ticket in tickets_db.values()
            if ticket.parking_required and ticket.status != "cancelled"
        ]

    @staticmethod
    def get_ticket_count() -> int:
        """
        Get total number of active tickets
        
        Returns:
            Count of tickets
        """
        return len([t for t in tickets_db.values() if t.status != "cancelled"])

    @staticmethod
    def clear_all():
        """
        Clear all tickets (for testing)
        """
        tickets_db.clear()
        print("✅ All tickets cleared from database")
