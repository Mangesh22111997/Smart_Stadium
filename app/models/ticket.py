"""
Ticket models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Literal

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class TicketBookingRequest(BaseModel):
    """
    Model for ticket booking request
    """
    user_id: UUID
    event_id: UUID
    commute_mode: Literal["metro", "bus", "private", "cab"] = Field(
        ...,
        description="Mode of commute"
    )
    parking_required: bool = Field(
        default=False,
        description="Is parking needed?"
    )
    departure_preference: Literal["early", "immediate", "delayed"] = Field(
        default="immediate",
        description="When to depart"
    )

    class Config:
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "commute_mode": "metro",
            "parking_required": False,
            "departure_preference": "immediate"
        }


class TicketUpdateRequest(BaseModel):
    """
    Model for ticket update request
    """
    commute_mode: Literal["metro", "bus", "private", "cab"] = Field(
        default=None,
        description="Mode of commute"
    )
    parking_required: bool = Field(
        default=None,
        description="Is parking needed?"
    )
    departure_preference: Literal["early", "immediate", "delayed"] = Field(
        default=None,
        description="When to depart"
    )

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
    ticket_id: UUID
    user_id: UUID
    event_id: UUID
    commute_mode: str
    parking_required: bool
    departure_preference: str
    booking_date: datetime
    status: str

    class Config:
        from_attributes = True
        example = {
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
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
    tickets: list[TicketResponse]

    class Config:
        example = {
            "total": 5,
            "tickets": []
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class Ticket(BaseModel):
    """
    Internal Ticket model for storage
    """
    ticket_id: UUID
    user_id: UUID
    event_id: UUID
    commute_mode: str
    parking_required: bool
    departure_preference: str
    booking_date: datetime
    status: str

    class Config:
        from_attributes = True
