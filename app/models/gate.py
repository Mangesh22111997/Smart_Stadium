"""
Gate models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class GateAssignmentRequest(BaseModel):
    """
    Model for gate assignment request
    """
    user_id: UUID
    ticket_id: UUID = Field(..., description="Ticket ID for tracking")
    commute_mode: Literal["metro", "bus", "private", "cab"] = Field(
        ...,
        description="Mode of commute"
    )
    departure_preference: Literal["early", "immediate", "delayed"] = Field(
        default="immediate",
        description="When user wants to depart"
    )

    class Config:
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "commute_mode": "metro",
            "departure_preference": "immediate"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class GateAssignmentResponse(BaseModel):
    """
    Model for gate assignment response
    """
    gate_id: str
    user_id: UUID
    ticket_id: UUID
    capacity_used: int
    capacity_remaining: int
    utilization_percent: float
    assignment_reason: str
    assigned_at: datetime

    class Config:
        example = {
            "gate_id": "A",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "capacity_used": 45,
            "capacity_remaining": 55,
            "utilization_percent": 45.0,
            "assignment_reason": "Metro users prefer Gate A, available capacity",
            "assigned_at": "2026-04-14T10:30:00"
        }


class GateStatusResponse(BaseModel):
    """
    Model for gate status response
    """
    gate_id: str
    current_count: int
    max_capacity: int
    utilization_percent: float
    congestion_level: str  # low, medium, high, critical
    capacity_remaining: int

    class Config:
        example = {
            "gate_id": "A",
            "current_count": 45,
            "max_capacity": 100,
            "utilization_percent": 45.0,
            "congestion_level": "low",
            "capacity_remaining": 55
        }


class AllGatesStatusResponse(BaseModel):
    """
    Model for all gates status response
    """
    gates: list[GateStatusResponse]
    total_capacity: int
    total_assigned: int
    system_utilization_percent: float

    class Config:
        example = {
            "gates": [],
            "total_capacity": 400,
            "total_assigned": 180,
            "system_utilization_percent": 45.0
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class GateAssignment(BaseModel):
    """
    Internal Gate Assignment model for storage
    """
    ticket_id: UUID
    user_id: UUID
    gate_id: str
    commute_mode: str
    departure_preference: str
    assigned_at: datetime
    assignment_reason: str

    class Config:
        from_attributes = True


class Gate(BaseModel):
    """
    Internal Gate model for storage
    """
    gate_id: str
    current_count: int
    max_capacity: int = 100
    assignments: dict = Field(default_factory=dict)  # ticket_id -> GateAssignment

    class Config:
        from_attributes = True
