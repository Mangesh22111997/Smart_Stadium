"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys

# Ensure app is importable
@pytest.fixture
def client():
    """FastAPI test client - no live Firebase connection needed for unit tests."""
    from app.main import app
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch):
    """Mock all Firebase calls so tests run offline and are deterministic."""
    mock_db = MagicMock()
    mock_db.child.return_value = mock_db
    mock_db.push.return_value = {"name": "mock_id"}
    mock_db.get.return_value.val.return_value = None
    mock_db.set.return_value = True
    mock_db.update.return_value = True
    mock_db.remove.return_value = True
    
    # Define a helper to safely patch if the attribute exists
    def safe_patch(target_module):
        if target_module in sys.modules:
            mod = sys.modules[target_module]
            if hasattr(mod, "get_db_connection"):
                monkeypatch.setattr(f"{target_module}.get_db_connection", lambda: mock_db)
            if hasattr(mod, "get_auth_connection"):
                monkeypatch.setattr(f"{target_module}.get_auth_connection", lambda: MagicMock())

    # Patch the source of truth
    monkeypatch.setattr("app.config.firebase_config.get_db_connection", lambda: mock_db)
    monkeypatch.setattr("app.config.firebase_config.get_auth_connection", lambda: MagicMock())
    
    # Patch known locations that use 'from app.config.firebase_config import get_db_connection'
    locations = [
        "app.main",
        "app.services.ticket_service",
        "app.services.firebase_auth_service",
        "app.services.booth_allocation_service",
        "app.utils.auth_middleware",
        "app.routes.events_routes"
    ]
    
    for loc in locations:
        safe_patch(loc)
    
    return mock_db

@pytest.fixture
def mock_auth():
    """Mock authentication token verification result."""
    return {
        "uid": "test_user_id",
        "email": "test@stadium.com",
        "username": "testuser",
        "is_admin": False
    }

@pytest.fixture
def authenticated_client(client, mock_auth):
    """Client with bypassed authentication."""
    from app.utils.auth_middleware import verify_token
    from app.main import app
    app.dependency_overrides[verify_token] = lambda: mock_auth
    yield client
    app.dependency_overrides.clear()
