"""
Gate Routes - API endpoints for gate assignment
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from app.models.gate import (
    GateAssignmentResponse,
    GateStatusResponse,
    AllGatesStatusResponse,
    GateAssignmentRequest
)
from app.services.gate_service import GateService

# Create router
router = APIRouter(prefix="/gates", tags=["Gates"])

# ============================================================================
# GATE ENDPOINTS
# ============================================================================

@router.post("/assign", response_model=GateAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_gate(request: GateAssignmentRequest) -> GateAssignmentResponse:
    """
    Assign a gate to a user
    
    - **user_id**: UUID of the user
    - **ticket_id**: UUID of the ticket
    - **commute_mode**: metro, bus, private, or cab
    - **departure_preference**: early, immediate, or delayed
    
    Returns: Gate assignment with details
    """
    assignment = GateService.assign_gate(request)
    gate_status = GateService.get_gate_status(assignment.gate_id)
    
    return GateAssignmentResponse(
        gate_id=assignment.gate_id,
        user_id=assignment.user_id,
        ticket_id=assignment.ticket_id,
        capacity_used=gate_status["current_count"],
        capacity_remaining=gate_status["capacity_remaining"],
        utilization_percent=gate_status["utilization_percent"],
        assignment_reason=assignment.assignment_reason,
        assigned_at=assignment.assigned_at
    )


@router.get("/{gate_id}", response_model=GateStatusResponse)
async def get_gate_status(gate_id: str) -> GateStatusResponse:
    """
    Get status of a specific gate
    
    - **gate_id**: Gate identifier (A, B, C, D)
    
    Returns: Gate status or 404 if not found
    """
    status_data = GateService.get_gate_status(gate_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate {gate_id} not found"
        )
    
    return GateStatusResponse(**status_data)


@router.get("/status/all", response_model=AllGatesStatusResponse)
async def get_all_gates_status() -> AllGatesStatusResponse:
    """
    Get status of all gates
    
    Returns: All gates status with system utilization
    """
    status_data = GateService.get_all_gates_status()
    
    return AllGatesStatusResponse(
        gates=[GateStatusResponse(**gate) for gate in status_data["gates"]],
        total_capacity=status_data["total_capacity"],
        total_assigned=status_data["total_assigned"],
        system_utilization_percent=status_data["system_utilization_percent"]
    )


@router.get("/assignment/{ticket_id}", response_model=GateAssignmentResponse)
async def get_assignment(ticket_id: UUID) -> GateAssignmentResponse:
    """
    Get gate assignment for a ticket
    
    - **ticket_id**: UUID of the ticket
    
    Returns: Assignment details or 404 if not found
    """
    assignment = GateService.get_assignment(ticket_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment for ticket {ticket_id} not found"
        )
    
    gate_status = GateService.get_gate_status(assignment.gate_id)
    
    return GateAssignmentResponse(
        gate_id=assignment.gate_id,
        user_id=assignment.user_id,
        ticket_id=assignment.ticket_id,
        capacity_used=gate_status["current_count"],
        capacity_remaining=gate_status["capacity_remaining"],
        utilization_percent=gate_status["utilization_percent"],
        assignment_reason=assignment.assignment_reason,
        assigned_at=assignment.assigned_at
    )


@router.put("/reassign/{ticket_id}/{new_gate_id}", response_model=GateAssignmentResponse)
async def reassign_gate(ticket_id: UUID, new_gate_id: str) -> GateAssignmentResponse:
    """
    Reassign a ticket to a different gate
    
    - **ticket_id**: UUID of the ticket
    - **new_gate_id**: New gate identifier (A, B, C, D)
    
    Returns: Updated assignment or 404 if not found
    """
    if new_gate_id not in ["A", "B", "C", "D"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gate ID: {new_gate_id}. Must be A, B, C, or D"
        )
    
    assignment = GateService.reassign_gate(ticket_id, new_gate_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment for ticket {ticket_id} not found"
        )
    
    gate_status = GateService.get_gate_status(assignment.gate_id)
    
    return GateAssignmentResponse(
        gate_id=assignment.gate_id,
        user_id=assignment.user_id,
        ticket_id=assignment.ticket_id,
        capacity_used=gate_status["current_count"],
        capacity_remaining=gate_status["capacity_remaining"],
        utilization_percent=gate_status["utilization_percent"],
        assignment_reason=assignment.assignment_reason,
        assigned_at=assignment.assigned_at
    )


# ============================================================================
# ML-ENHANCED GATE ENDPOINTS (Predictive)
# ============================================================================

@router.get("/ml/status/all")
async def get_all_gates_status_ml():
    """
    Get ML-enhanced status of all gates with predictions
    
    Returns: All gates status + ML predictions for next 30 minutes
    
    Includes:
    - Current utilization
    - Predicted queue depth (T+10, T+30)
    - Reroute recommendations
    - System-wide alerts
    """
    status_data = GateService.get_all_gates_status_ml_enhanced()
    return status_data


@router.get("/ml/{gate_id}")
async def get_gate_status_ml(gate_id: str):
    """
    Get ML-enhanced status of a specific gate with predictions
    
    - **gate_id**: Gate identifier (A, B, C, D)
    
    Returns: Gate status + ML predictions or 404 if not found
    
    Includes:
    - Current queue depth
    - Predicted queue depth (T+10, T+30)
    - Should proactive reroute?
    - Recommended staffing
    """
    status_data = GateService.get_gate_status_ml_enhanced(gate_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate {gate_id} not found"
        )
    return status_data
