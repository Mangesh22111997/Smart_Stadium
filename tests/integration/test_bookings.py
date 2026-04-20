"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


import pytest
from uuid import uuid4

def test_health_check(client):
    """Test the system health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_firebase_health_check(client, mock_firebase):
    """Test the Firebase health check endpoint with mocked DB."""
    response = client.get("/health/firebase")
    assert response.status_code == 200
    assert response.json()["database"] == "online"

def test_get_events(client, mock_firebase):
    """Test retrieving events catalog."""
    # Mock data in Firebase
    mock_events = {
        "event_01": {"name": "Test Event", "price": 500}
    }
    mock_firebase.get.return_value.val.return_value = mock_events
    
    response = client.get("/events/list")
    assert response.status_code == 200
    assert len(response.json()["events"]) > 0
