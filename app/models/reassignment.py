"""
Reassignment models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class ManualReassignmentRequest(BaseModel):
    """
    Model for manual reassignment request
    """
    ticket_id: UUID
    new_gate_id: str = Field(..., description="New gate ID (A, B, C, D)")
    reason: str = Field(
        default="Manual: Staff request",
        description="Reason for reassignment"
    )

    class Config:
        example = {
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "new_gate_id": "B",
            "reason": "User request"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class ReassignmentResponse(BaseModel):
    """
    Model for reassignment response
    """
    reassignment_id: UUID
    ticket_id: UUID
    user_id: UUID
    from_gate: str
    to_gate: str
    reason: str
    reassigned_at: datetime
    congestion_before_percent: float
    congestion_after_percent: float
    disruption_score: float  # Lower is better

    class Config:
        example = {
            "reassignment_id": "550e8400-e29b-41d4-a716-446655440003",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "from_gate": "A",
            "to_gate": "B",
            "reason": "High congestion detected at Gate A",
            "reassigned_at": "2026-04-14T10:30:00",
            "congestion_before_percent": 85.0,
            "congestion_after_percent": 65.0,
            "disruption_score": 20.0
        }


class CheckAndReassignResponse(BaseModel):
    """
    Model for check and reassign response
    """
    reassignments_made: int
    message: str
    gates_checked: int
    gates_with_high_congestion: int
    details: list[ReassignmentResponse]

    class Config:
        example = {
            "reassignments_made": 2,
            "message": "Checked 4 gates, made 2 reassignments",
            "gates_checked": 4,
            "gates_with_high_congestion": 2,
            "details": []
        }


class ReassignmentHistoryResponse(BaseModel):
    """
    Model for reassignment history response
    """
    ticket_id: UUID
    total_reassignments: int
    current_gate: str
    reassignments: list[ReassignmentResponse]

    class Config:
        example = {
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "total_reassignments": 1,
            "current_gate": "B",
            "reassignments": []
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class Reassignment(BaseModel):
    """
    Internal Reassignment model for storage
    """
    reassignment_id: UUID
    ticket_id: UUID
    user_id: UUID
    from_gate: str
    to_gate: str
    reason: str
    reassigned_at: datetime
    congestion_before_percent: float
    congestion_after_percent: float
    disruption_score: float  # Metric for minimizing disruption

    class Config:
        from_attributes = True
