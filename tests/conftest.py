
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client - no live Firebase connection needed for unit tests."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_firebase(monkeypatch):
    """Mock all Firebase calls so tests run offline and are deterministic."""
    mock_db = MagicMock()
    mock_db.child.return_value = mock_db
    mock_db.get.return_value = MagicMock(val=lambda: None)
    mock_db.set.return_value = True
    
    # Patch the global get_db_connection
    monkeypatch.setattr("app.config.firebase_config.get_db_connection", lambda: mock_db)
    monkeypatch.setattr("app.main.get_db_connection", lambda: mock_db)
    
    return mock_db

@pytest.fixture
def mock_auth(monkeypatch):
    """Mock authentication token verification."""
    mock_user = {
        "uid": "test_user_id",
        "email": "test@stadium.com",
        "role": "user"
    }
    # For now, we'll bypass the actual token verification in tests
    return mock_user
