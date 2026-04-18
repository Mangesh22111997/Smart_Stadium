"""
Reassignment Routes - API endpoints for dynamic gate reassignments
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List

from app.models.reassignment import (
    ReassignmentResponse,
    CheckAndReassignResponse,
    ReassignmentHistoryResponse,
    ManualReassignmentRequest
)
from app.services.reassignment_service import ReassignmentService
from app.services.gate_service import GateService

# Create router
router = APIRouter(prefix="/reassignments", tags=["Reassignments"])

# ============================================================================
# REASSIGNMENT ENDPOINTS
# ============================================================================

@router.post("/check-and-reassign", response_model=CheckAndReassignResponse, status_code=status.HTTP_200_OK)
async def check_and_reassign() -> CheckAndReassignResponse:
    """
    Check all gates for high congestion and auto-reassign users if needed
    
    Returns: Details of reassignments made
    """
    result = ReassignmentService.check_and_reassign_all()
    
    return CheckAndReassignResponse(
        reassignments_made=result["reassignments_made"],
        message=result["message"],
        gates_checked=result["gates_checked"],
        gates_with_high_congestion=result["gates_with_high_congestion"],
        details=[
            ReassignmentResponse(**reassignment.dict()) 
            for reassignment in result["details"]
        ]
    )


@router.post("/manual", response_model=ReassignmentResponse, status_code=status.HTTP_201_CREATED)
async def manual_reassign(request: ManualReassignmentRequest) -> ReassignmentResponse:
    """
    Manually reassign a ticket to a different gate
    
    - **ticket_id**: UUID of the ticket
    - **new_gate_id**: New gate identifier (A, B, C, D)
    - **reason**: Reason for reassignment
    
    Returns: Reassignment details or 400 if failed
    """
    # Validate new gate
    if request.new_gate_id not in ["A", "B", "C", "D"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gate ID: {request.new_gate_id}. Must be A, B, C, or D"
        )
    
    # Check if ticket exists
    assignment = GateService.get_assignment(request.ticket_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {request.ticket_id} not found"
        )
    
    # Perform reassignment
    reassignment = ReassignmentService.manual_reassign(request)
    if not reassignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reassignment failed"
        )
    
    return ReassignmentResponse(**reassignment.dict())


@router.get("/{ticket_id}", response_model=ReassignmentHistoryResponse)
async def get_ticket_reassignments(ticket_id: UUID) -> ReassignmentHistoryResponse:
    """
    Get reassignment history for a ticket
    
    - **ticket_id**: UUID of the ticket
    
    Returns: Reassignment history or 404 if ticket not found
    """
    # Check if ticket exists
    assignment = GateService.get_assignment(ticket_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_id} not found"
        )
    
    reassignments = ReassignmentService.get_ticket_reassignments(ticket_id)
    current_gate = assignment.gate_id if assignment else "Unknown"
    
    return ReassignmentHistoryResponse(
        ticket_id=ticket_id,
        total_reassignments=len(reassignments),
        current_gate=current_gate,
        reassignments=[
            ReassignmentResponse(**reassignment.dict()) 
            for reassignment in reassignments
        ]
    )


@router.get("", response_model=List[ReassignmentResponse])
async def get_all_reassignments() -> List[ReassignmentResponse]:
    """
    Get all reassignments in the system
    
    Returns: List of all reassignments
    """
    reassignments = ReassignmentService.get_all_reassignments()
    return [
        ReassignmentResponse(**reassignment.dict()) 
        for reassignment in reassignments
    ]


@router.get("/gate/{gate_id}", response_model=List[ReassignmentResponse])
async def get_gate_reassignments(gate_id: str) -> List[ReassignmentResponse]:
    """
    Get all reassignments from a specific gate
    
    - **gate_id**: Gate identifier (A, B, C, D)
    
    Returns: List of reassignments from that gate
    """
    if gate_id not in ["A", "B", "C", "D"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gate ID: {gate_id}"
        )
    
    reassignments = ReassignmentService.get_gate_reassignments(gate_id)
    return [
        ReassignmentResponse(**reassignment.dict()) 
        for reassignment in reassignments
    ]
