"""
User models using Pydantic for validation
"""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class UserRegisterRequest(BaseModel):
    """
    Model for user registration request
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Validates email format
    phone: str = Field(..., min_length=7, max_length=20)
    commute_preference: str = Field(
        default="metro",
        description="metro, bus, private, cab"
    )

    class Config:
        example = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+91-9876543210",
            "commute_preference": "metro"
        }


class PreferenceUpdateRequest(BaseModel):
    """
    Model for updating user preferences
    """
    commute_preference: str = Field(
        ...,
        description="metro, bus, private, cab"
    )

    class Config:
        example = {
            "commute_preference": "bus"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class UserResponse(BaseModel):
    """
    Model for user response
    """
    user_id: UUID
    name: str
    email: str
    phone: str
    commute_preference: str
    created_at: datetime

    class Config:
        from_attributes = True
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+91-9876543210",
            "commute_preference": "metro",
            "created_at": "2026-04-14T10:30:00"
        }


class PreferenceUpdateResponse(BaseModel):
    """
    Model for preference update response
    """
    message: str
    user_id: UUID
    commute_preference: str

    class Config:
        example = {
            "message": "Preferences updated successfully",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "commute_preference": "bus"
        }


class UserListResponse(BaseModel):
    """
    Model for user list response
    """
    total: int
    users: list[UserResponse]

    class Config:
        example = {
            "total": 2,
            "users": []
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class User(BaseModel):
    """
    Internal User model for storage
    """
    user_id: UUID
    name: str
    email: str
    phone: str
    commute_preference: str
    created_at: datetime

    class Config:
        from_attributes = True
