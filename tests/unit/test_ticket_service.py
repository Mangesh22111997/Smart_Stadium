# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



import pytest
from app.services.ticket_service import TicketService
from app.models.ticket import TicketBookingRequest

@pytest.mark.asyncio
async def test_book_ticket_logic(mock_firebase):
    # Setup mock return values
    mock_firebase.push.return_value = {"name": "TICKET123"}
    
    request = TicketBookingRequest(
        user_id="user123",
        event_id="event456",
        commute_mode="metro",
        parking_required=False,
        departure_preference="immediate"
    )
    
    result = await TicketService.book_ticket(request)
    
    assert result["ticket_id"] == "TICKET123"
    assert "assigned_gate" in result
    assert result["user_id"] == "user123"
    assert mock_firebase.push.called

@pytest.mark.asyncio
async def test_get_user_tickets(mock_firebase):
    # Setup mock data in RTDB format
    mock_firebase.get.return_value.val.return_value = {
        "T1": {"user_id": "user123", "event_id": "E1"},
        "T2": {"user_id": "other", "event_id": "E1"}
    }
    
    tickets = await TicketService.get_user_tickets("user123")
    
    assert len(tickets) == 1
    assert tickets[0]["ticket_id"] == "T1"
