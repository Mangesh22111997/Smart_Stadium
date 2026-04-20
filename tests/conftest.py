import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_firebase():
    """Mock Firebase database object."""
    mock = MagicMock()
    with patch("app.config.firebase_config.get_db_connection", return_value=mock):
        yield mock

@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
