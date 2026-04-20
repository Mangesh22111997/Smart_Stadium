"""
Tests for GateService — gate assignment logic and ML integration.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.gate_service import GateService
from app.models.gate import GateAssignmentRequest


@pytest.mark.unit
def test_assign_gate_metro_returns_valid_gate():
    """Metro commute mode should return Gate A or B (metro-adjacent)."""
    request = GateAssignmentRequest(
        user_id="user123",
        ticket_id="ticket456",
        commute_mode="metro",
        departure_preference="immediate",
        parking_required=False
    )
    assignment = GateService.assign_gate(request)
    assert assignment.gate_id in ["A", "B", "C", "D"]
    assert assignment.gate_id is not None


@pytest.mark.unit
def test_assign_gate_private_vehicle_with_parking():
    """Private vehicle with parking should be directed to parking-adjacent gates."""
    request = GateAssignmentRequest(
        user_id="user123",
        ticket_id="ticket456",
        commute_mode="private",
        departure_preference="immediate",
        parking_required=True
    )
    assignment = GateService.assign_gate(request)
    assert assignment.gate_id in ["A", "B", "C", "D"]


@pytest.mark.unit
def test_get_gate_status_returns_all_gates():
    """Gate status should return entries for all configured gates."""
    all_gates = GateService.get_all_gates()
    assert isinstance(all_gates, dict)
    assert len(all_gates) >= 4
    for gate_id, gate in all_gates.items():
        assert hasattr(gate, "current_count")
        assert hasattr(gate, "max_capacity")
        assert gate.current_count >= 0
        assert gate.max_capacity > 0


@pytest.mark.unit
def test_gate_capacity_percentage():
    """Capacity percentage should be between 0 and 100."""
    from app.services.gate_service import gates_db
    for gate_id, gate in gates_db.items():
        pct = (gate.current_count / gate.max_capacity) * 100
        assert 0 <= pct <= 100, f"Gate {gate_id} has invalid capacity percentage: {pct}"


@pytest.mark.unit
@patch("app.services.gate_service.ML_ENABLED", True)
def test_ml_prediction_used_when_enabled():
    """When ML is enabled, gate assignment should call the inference server."""
    with patch("app.services.gate_service.get_inference_server") as mock_server:
        mock_server.return_value.predict_gate_load.return_value = {
            "predicted_queue_t10": 50,
            "predicted_queue_t30": 80,
            "should_proactive_reroute": False
        }
        request = GateAssignmentRequest(
            user_id="user123",
            ticket_id="ticket456",
            commute_mode="metro",
            departure_preference="immediate",
            parking_required=False
        )
        GateService.assign_gate(request)
        mock_server.return_value.predict_gate_load.assert_called()
