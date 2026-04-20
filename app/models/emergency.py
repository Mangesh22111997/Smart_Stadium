"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Emergency models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class EmergencySOSRequest(BaseModel):
    """
    Model for SOS/emergency request
    """
    user_id: UUID
    emergency_type: Literal[
        "medical", "crowd", "lost", "threat", "fire",
        "evacuation", "lost_child", "harassment", "other"
    ]
    location: str = Field(
        ...,
        description="Location: gate_a, gate_b, gate_c, gate_d, gate_center, pillar_1-4, center, etc."
    )
    description: str = Field(
        default="Emergency reported",
        max_length=500,
        description="Detailed description of emergency"
    )

    class Config:
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "emergency_type": "medical",
            "location": "gate_a",
            "description": "User feeling dizzy and unwell"
        }


class NearestExitRequest(BaseModel):
    """
    Model for nearest exit request
    """
    location: str = Field(
        ...,
        description="Current location"
    )

    class Config:
        example = {
            "location": "gate_a"
        }


class EmergencyStatusUpdateRequest(BaseModel):
    """
    Model for emergency status update
    """
    status: Literal["reported", "responding", "resolved", "cancelled"]
    notes: str = Field(
        default="",
        max_length=500,
        description="Additional notes"
    )

    class Config:
        example = {
            "status": "resolved",
            "notes": "Medical team attended, user stable"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class NearestExitResponse(BaseModel):
    """
    Model for nearest exit response
    """
    exit_id: str
    location: str
    distance_meters: int
    direction: str
    coordinates: Optional[dict] = None

    class Config:
        example = {
            "exit_id": "exit_1",
            "location": "gate_a",
            "distance_meters": 50,
            "direction": "North from gate",
            "coordinates": {"latitude": 0.0, "longitude": 0.0}
        }


class EmergencyResponse(BaseModel):
    """
    Model for emergency response
    """
    emergency_id: UUID
    user_id: UUID
    emergency_type: str
    location: str
    description: str
    nearest_exit: str
    exit_distance_meters: int
    status: str
    priority_level: str
    staff_assigned: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        example = {
            "emergency_id": "550e8400-e29b-41d4-a716-446655440020",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "emergency_type": "medical",
            "location": "gate_a",
            "description": "User feeling dizzy",
            "nearest_exit": "exit_1",
            "exit_distance_meters": 50,
            "status": "reported",
            "priority_level": "CRITICAL",
            "staff_assigned": None,
            "reported_at": "2026-04-14T12:30:00",
            "resolved_at": None
        }


class EmergencyListResponse(BaseModel):
    """
    Model for emergency list response
    """
    total: int
    active: int
    emergencies: list[EmergencyResponse]

    class Config:
        example = {
            "total": 5,
            "active": 2,
            "emergencies": []
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class Emergency(BaseModel):
    """
    Internal Emergency model for storage
    """
    emergency_id: UUID
    user_id: UUID
    emergency_type: str
    location: str
    description: str
    nearest_exit: str
    exit_distance_meters: int
    status: str
    priority_level: str
    staff_assigned: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
