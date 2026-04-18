"""
Crowd models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class CrowdUpdateRequest(BaseModel):
    """
    Model for manual crowd update request
    """
    crowd_change: int = Field(
        ...,
        description="Number of people to add (positive) or remove (negative)"
    )

    class Config:
        example = {
            "crowd_change": 5
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class CrowdStatusResponse(BaseModel):
    """
    Model for crowd status response
    """
    gate_id: str
    current_crowd: int
    peak_capacity: int
    congestion_level: str  # low, medium, high, critical
    capacity_percent: float
    estimated_entry_time_minutes: float
    flow_rate: int  # people per minute
    trend: str  # increasing, stable, decreasing
    last_updated: datetime

    class Config:
        example = {
            "gate_id": "A",
            "current_crowd": 45,
            "peak_capacity": 100,
            "congestion_level": "low",
            "capacity_percent": 45.0,
            "estimated_entry_time_minutes": 2.5,
            "flow_rate": 18,
            "trend": "stable",
            "last_updated": "2026-04-14T10:30:00"
        }


class AllCrowdStatusResponse(BaseModel):
    """
    Model for all crowd status response
    """
    gates: list[CrowdStatusResponse]
    total_crowd: int
    total_capacity: int
    system_utilization_percent: float
    average_congestion_level: str

    class Config:
        example = {
            "gates": [],
            "total_crowd": 180,
            "total_capacity": 400,
            "system_utilization_percent": 45.0,
            "average_congestion_level": "low"
        }


class CrowdMetricsResponse(BaseModel):
    """
    Model for crowd metrics response
    """
    total_crowd: int
    total_capacity: int
    system_utilization_percent: float
    average_entry_time_minutes: float
    total_flow_rate: int
    gates_critical: int
    gates_high: int
    gates_medium: int
    gates_low: int

    class Config:
        example = {
            "total_crowd": 180,
            "total_capacity": 400,
            "system_utilization_percent": 45.0,
            "average_entry_time_minutes": 5.2,
            "total_flow_rate": 72,
            "gates_critical": 0,
            "gates_high": 1,
            "gates_medium": 2,
            "gates_low": 1
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class CrowdData(BaseModel):
    """
    Internal Crowd Data model for storage
    """
    gate_id: str
    current_crowd: int
    peak_capacity: int
    congestion_level: str
    capacity_percent: float
    estimated_entry_time_minutes: float
    flow_rate: int
    trend: str
    last_updated: datetime
    previous_crowd: int = 0  # For trend calculation

    class Config:
        from_attributes = True
