"""
Tests for EmergencyService — SOS routing and safe exit logic.
"""

import pytest
from app.services.emergency_service import EmergencyService
from app.models.emergency import EmergencyCreateRequest


@pytest.mark.unit
def test_nearest_exit_returned_for_all_zones():
    """Every seat zone should have a designated safe exit."""
    zones = ["A", "B", "C", "D"]
    for zone in zones:
        exit_id = EmergencyService.get_nearest_safe_exit(zone)
        assert exit_id is not None, f"No safe exit for zone {zone}"
        assert len(exit_id) > 0


@pytest.mark.unit
def test_emergency_create_stores_record(mock_firebase):
    """Creating an emergency should persist it and return an ID."""
    mock_firebase.push.return_value = {"name": "EMG001"}

    request = EmergencyCreateRequest(
        user_id="user123",
        zone="A",
        emergency_type="medical",
        description="Attendee needs medical assistance"
    )
    result = EmergencyService.create_emergency(request)
    assert result is not None
    assert mock_firebase.push.called


@pytest.mark.unit
def test_emergency_type_validation():
    """Invalid emergency types should raise a ValueError."""
    with pytest.raises((ValueError, Exception)):
        EmergencyCreateRequest(
            user_id="user123",
            zone="A",
            emergency_type="INVALID_TYPE",
            description="Test"
        )
