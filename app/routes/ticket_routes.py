"""
Ticket Routes - API endpoints for ticket booking
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List

from app.models.ticket import (
    TicketResponse,
    TicketBookingRequest,
    TicketUpdateRequest,
    TicketListResponse
)
from app.services.ticket_service import TicketService

# Create router
router = APIRouter(prefix="/tickets", tags=["Tickets"])

# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@router.post("/book", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def book_ticket(request: TicketBookingRequest) -> TicketResponse:
    """
    Book a new ticket
    
    - **user_id**: UUID of the user
    - **event_id**: UUID of the event
    - **commute_mode**: metro, bus, private, or cab
    - **parking_required**: Whether parking is needed
    - **departure_preference**: early, immediate, or delayed
    
    Returns: Booked ticket with ticket_id
    """
    ticket = TicketService.book_ticket(request)
    return TicketResponse(**ticket.dict())


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: UUID) -> TicketResponse:
    """
    Get ticket details by ID
    
    - **ticket_id**: UUID of the ticket
    
    Returns: Ticket details or 404 if not found
    """
    ticket = TicketService.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    return TicketResponse(**ticket.dict())


@router.get("", response_model=TicketListResponse)
async def list_tickets() -> TicketListResponse:
    """
    Get all tickets
    
    Returns: List of all tickets
    """
    tickets = TicketService.list_all_tickets()
    return TicketListResponse(
        total=len(tickets),
        tickets=[TicketResponse(**ticket.dict()) for ticket in tickets]
    )


@router.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(user_id: UUID) -> List[TicketResponse]:
    """
    Get all tickets for a specific user
    
    - **user_id**: UUID of the user
    
    Returns: List of tickets for that user
    """
    tickets = TicketService.get_user_tickets(user_id)
    return [TicketResponse(**ticket.dict()) for ticket in tickets]


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: UUID,
    request: TicketUpdateRequest
) -> TicketResponse:
    """
    Update ticket details
    
    - **ticket_id**: UUID of the ticket
    - **commute_mode**: (optional) metro, bus, private, or cab
    - **parking_required**: (optional) Whether parking is needed
    - **departure_preference**: (optional) early, immediate, or delayed
    
    Returns: Updated ticket or 404 if not found
    """
    ticket = TicketService.update_ticket(ticket_id, request)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    return TicketResponse(**ticket.dict())


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_ticket(ticket_id: UUID):
    """
    Cancel a ticket
    
    - **ticket_id**: UUID of the ticket
    
    Returns: 204 No Content or 404 if not found
    """
    cancelled = TicketService.cancel_ticket(ticket_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    return None


@router.get("/mode/{commute_mode}", response_model=List[TicketResponse])
async def get_tickets_by_mode(commute_mode: str) -> List[TicketResponse]:
    """
    Get all tickets with a specific commute mode
    
    - **commute_mode**: metro, bus, private, or cab
    
    Returns: List of tickets with matching mode
    """
    tickets = TicketService.get_tickets_by_commute_mode(commute_mode)
    return [TicketResponse(**ticket.dict()) for ticket in tickets]


@router.get("/parking/required", response_model=List[TicketResponse])
async def get_parking_tickets() -> List[TicketResponse]:
    """
    Get all tickets that require parking
    
    Returns: List of tickets needing parking
    """
    tickets = TicketService.get_parking_required_tickets()
    return [TicketResponse(**ticket.dict()) for ticket in tickets]
