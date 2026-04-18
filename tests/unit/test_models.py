
import pytest
from pydantic import ValidationError
from app.models.ticket import TicketBookingRequest
from uuid import uuid4

def test_valid_ticket_request():
    """Test that a valid ticket request passes validation."""
    user_id = uuid4()
    event_id = uuid4()
    req = TicketBookingRequest(
        user_id=user_id,
        event_id=event_id,
        commute_mode="metro",
        parking_required=False,
        departure_preference="immediate"
    )
    assert req.commute_mode == "metro"
    assert req.user_id == user_id

def test_invalid_commute_mode():
    """Test that an invalid commute mode is rejected."""
    with pytest.raises(ValidationError):
        TicketBookingRequest(
            user_id=uuid4(),
            event_id=uuid4(),
            commute_mode="spaceship", # Invalid
            parking_required=False
        )

def test_missing_required_field():
    """Test that missing required fields trigger validation error."""
    with pytest.raises(ValidationError):
        TicketBookingRequest(
            user_id=uuid4(),
            # event_id missing
            commute_mode="metro"
        )
