# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Booth Allocation models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class BoothAllocationRequest(BaseModel):
    """
    Model for booth allocation request
    """
    user_id: UUID
    delivery_zone: Literal["pillar_1", "pillar_2", "pillar_3", "pillar_4", "center"] = Field(
        default="center",
        description="User's delivery zone"
    )

    class Config:
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "delivery_zone": "pillar_1"
        }


class BoothReallocationRequest(BaseModel):
    """
    Model for booth reallocation request
    """
    order_id: UUID
    reason: str = Field(
        default="User preference",
        description="Reason for reallocation"
    )

    class Config:
        example = {
            "order_id": "550e8400-e29b-41d4-a716-446655440010",
            "reason": "Too crowded"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class BoothAllocationResponse(BaseModel):
    """
    Model for booth allocation response
    """
    booth_id: str
    zone: str
    distance_score: float
    crowd_score: float
    total_score: float
    queue_size: int
    estimated_wait_minutes: int
    reason: str

    class Config:
        example = {
            "booth_id": "B01",
            "zone": "pillar_1",
            "distance_score": 5.0,
            "crowd_score": 30.0,
            "total_score": 18.0,
            "queue_size": 3,
            "estimated_wait_minutes": 9,
            "reason": "Lowest crowd (30%), nearest to pillar_1"
        }


class TopBoothsResponse(BaseModel):
    """
    Model for top booths response
    """
    zone: str
    top_booths: list[BoothAllocationResponse]
    total_booths: int

    class Config:
        example = {
            "zone": "pillar_1",
            "top_booths": [],
            "total_booths": 5
        }


class DistanceMetricsResponse(BaseModel):
    """
    Model for distance metrics
    """
    booth_id: str
    zone: str
    distance_units: float
    distance_score: float
    distance_category: str  # very_close, close, medium, far

    class Config:
        example = {
            "booth_id": "B01",
            "zone": "pillar_1",
            "distance_units": 10.0,
            "distance_score": 5.0,
            "distance_category": "very_close"
        }


# ============================================================================
# INTERNAL MODELS (for calculations)
# ============================================================================

class BoothAllocationData(BaseModel):
    """
    Internal Booth Allocation model
    """
    booth_id: str
    zone: str
    distance_score: float
    crowd_score: float
    total_score: float
    queue_size: int
    estimated_wait_minutes: int
    reason: str

    class Config:
        from_attributes = True
