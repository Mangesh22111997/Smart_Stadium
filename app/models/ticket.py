"""
Ticket models using Pydantic for validation
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Literal, Optional, Dict, Any, List

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class TicketBookingRequest(BaseModel):
    """
    Model for ticket booking request with strict validation
    """
    user_id: str
    event_id: str
    commute_mode: str = Field(..., description="Mode of commute (metro, bus, private, cab, walk)")
    parking_required: bool = Field(default=False, description="Is parking needed?")
    departure_preference: str = Field(default="immediate", description="When to depart (early, immediate, delayed)")

    @field_validator("commute_mode")
    @classmethod
    def validate_commute_mode(cls, v: str) -> str:
        allowed = {"metro", "bus", "private", "cab", "walk"}
        if v.lower() not in allowed:
            raise ValueError(f"commute_mode must be one of {allowed}")
        return v.lower()

    @field_validator("departure_preference")
    @classmethod
    def validate_departure_preference(cls, v: str) -> str:
        allowed = {"early", "immediate", "delayed"}
        if v.lower() not in allowed:
            raise ValueError(f"departure_preference must be one of {allowed}")
        return v.lower()

    class Config:
        example = {
            "user_id": "user_123",
            "event_id": "event_456",
            "commute_mode": "metro",
            "parking_required": False,
            "departure_preference": "immediate"
        }


class TicketUpdateRequest(BaseModel):
    """
    Model for ticket update request
    """
    commute_mode: Optional[str] = Field(default=None, description="Updated mode of commute")
    parking_required: Optional[bool] = Field(default=None, description="Is parking needed?")
    departure_preference: Optional[str] = Field(default=None, description="Updated departure preference")

    @field_validator("commute_mode")
    @classmethod
    def validate_commute_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return None
        allowed = {"metro", "bus", "private", "cab", "walk"}
        if v.lower() not in allowed:
            raise ValueError(f"commute_mode must be one of {allowed}")
        return v.lower()

    class Config:
        example = {
            "commute_mode": "bus",
            "parking_required": True
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class TicketResponse(BaseModel):
    """
    Model for ticket response
    """
    ticket_id: str
    user_id: str
    event_id: str
    commute_mode: str
    parking_required: bool
    departure_preference: str
    booking_date: str
    status: str

    class Config:
        from_attributes = True
        example = {
            "ticket_id": "TICKET-1234",
            "user_id": "user_123",
            "event_id": "event_456",
            "commute_mode": "metro",
            "parking_required": False,
            "departure_preference": "immediate",
            "booking_date": "2026-04-14T10:30:00",
            "status": "confirmed"
        }


class TicketListResponse(BaseModel):
    """
    Model for ticket list response
    """
    total: int
    tickets: List[TicketResponse]


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class Ticket(BaseModel):
    """
    Internal Ticket model for storage
    """
    ticket_id: str
    user_id: str
    event_id: str
    commute_mode: str
    parking_required: bool
    departure_preference: str
    booking_date: datetime
    status: str

    class Config:
        from_attributes = True
