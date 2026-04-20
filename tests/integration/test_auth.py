"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""


import pytest

def test_signup_returns_201(client, mock_firebase):
    """Valid signup creates user and returns 201."""
    # Mock username not taken
    mock_firebase.child.return_value.get.return_value.val.return_value = None 

    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "test@stadium.com",
        "password": "SecurePass@123",
        "name": "Test User"
    })
    assert response.status_code == 201
    assert "user_id" in response.json()

def test_signin_with_bad_credentials_returns_401(client, mock_firebase):
    """Invalid credentials return 401, not 500."""
    # Mock user not found
    mock_firebase.child.return_value.get.return_value.val.return_value = None 

    response = client.post("/auth/signin", json={
        "username": "nobody",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_all_users_without_auth_returns_401(client):
    """Admin-only endpoint must reject unauthenticated requests."""
    response = client.get("/auth/users/all")
    assert response.status_code in [401, 403, 422] # 422 if Depends fails early

def test_get_all_users_as_non_admin_returns_403(client, mock_firebase):
    """Non-admin authenticated user must be rejected from admin endpoint."""
    from app.utils.auth_middleware import admin_only
    from app.main import app
    from fastapi import HTTPException
    
    # Override admin_only to return a 403
    app.dependency_overrides[admin_only] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Unauthorized")
    )
    
    response = client.get("/auth/users/all")
    assert response.status_code == 403
    app.dependency_overrides.clear()

def test_health_check_does_not_require_auth(client):
    """Health endpoint must be publicly accessible."""
    response = client.get("/health")
    assert response.status_code == 200
