"""
End-to-end test: Register → Login → Book Ticket → Verify Gate Assignment.
Tests the complete user journey through the API layer.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
def test_complete_booking_workflow(client, mock_firebase):
    """
    Full E2E: signup → signin → book ticket → verify gate assigned.
    Validates the entire booking pipeline with mocked Firebase.
    """
    # Step 1 — Register new user
    mock_firebase.child.return_value.get.return_value.val.return_value = None
    mock_firebase.push.return_value = {"name": "USER001"}

    signup_response = client.post("/auth/signup", json={
        "username": "e2e_testuser",
        "email": "e2e@stadium.com",
        "password": "E2eTest@123",
        "name": "E2E Tester"
    })
    assert signup_response.status_code == 201
    assert "user_id" in signup_response.json()

    # Step 2 — Login
    mock_firebase.child.return_value.get.return_value.val.return_value = {
        "user_id": "USER001",
        "username": "e2e_testuser",
        "email": "e2e@stadium.com",
        "password_hash": "hashed",
        "is_admin": False
    }
    signin_response = client.post("/auth/signin", json={
        "username": "e2e_testuser",
        "password": "E2eTest@123"
    })
    assert signin_response.status_code == 200
    session_token = signin_response.json().get("session_token")
    assert session_token is not None

    # Step 3 — Book ticket with authenticated session
    from app.utils.auth_middleware import verify_token
    from app.main import app
    app.dependency_overrides[verify_token] = lambda: {
        "uid": "USER001",
        "username": "e2e_testuser",
        "is_admin": False
    }
    mock_firebase.push.return_value = {"name": "TICKET001"}

    booking_response = client.post("/bookings/create", json={
        "user_id": "USER001",
        "event_id": "EVT001",
        "commute_mode": "metro",
        "parking_required": False,
        "departure_preference": "immediate"
    })
    assert booking_response.status_code == 201
    booking_data = booking_response.json()
    assert "ticket_id" in booking_data
    assert "assigned_gate" in booking_data
    assert booking_data["assigned_gate"] in ["A", "B", "C", "D"]

    app.dependency_overrides.clear()


@pytest.mark.e2e
def test_health_endpoints_sequence(client, mock_firebase):
    """Verify health check cascade — system, then Firebase."""
    system_health = client.get("/health")
    assert system_health.status_code == 200
    assert system_health.json()["status"] == "ok"

    firebase_health = client.get("/health/firebase")
    assert firebase_health.status_code == 200
