"""
Crowd Routes - API endpoints for crowd monitoring
"""
from fastapi import APIRouter, HTTPException, status

from app.models.crowd import (
    CrowdStatusResponse,
    AllCrowdStatusResponse,
    CrowdMetricsResponse,
    CrowdUpdateRequest
)
from app.services.crowd_service import CrowdService

# Create router
router = APIRouter(prefix="/crowd", tags=["Crowd"])

# ============================================================================
# CROWD ENDPOINTS
# ============================================================================

@router.get("/{gate_id}", response_model=CrowdStatusResponse)
async def get_crowd_status(gate_id: str) -> CrowdStatusResponse:
    """
    Get current crowd status for a gate
    
    - **gate_id**: Gate identifier (A, B, C, D)
    
    Returns: Crowd status or 404 if gate not found
    """
    crowd_data = CrowdService.get_crowd_status(gate_id)
    if not crowd_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate {gate_id} not found"
        )
    
    return CrowdStatusResponse(**crowd_data.dict())


@router.get("/status/all", response_model=AllCrowdStatusResponse)
async def get_all_crowd_status() -> AllCrowdStatusResponse:
    """
    Get crowd status for all gates
    
    Returns: All gates crowd data with system metrics
    """
    all_status = CrowdService.get_all_crowd_status()
    
    return AllCrowdStatusResponse(
        gates=[CrowdStatusResponse(**gate.dict()) for gate in all_status["gates"]],
        total_crowd=all_status["total_crowd"],
        total_capacity=all_status["total_capacity"],
        system_utilization_percent=all_status["system_utilization_percent"],
        average_congestion_level=all_status["average_congestion_level"]
    )


@router.post("/simulate-update", response_model=AllCrowdStatusResponse)
async def simulate_crowd_update() -> AllCrowdStatusResponse:
    """
    Simulate crowd updates for all gates
    Random realistic changes to crowd counts
    
    Returns: Updated crowd status for all gates
    """
    updated = CrowdService.simulate_crowd_update()
    all_status = CrowdService.get_all_crowd_status()
    
    return AllCrowdStatusResponse(
        gates=[CrowdStatusResponse(**gate.dict()) for gate in all_status["gates"]],
        total_crowd=all_status["total_crowd"],
        total_capacity=all_status["total_capacity"],
        system_utilization_percent=all_status["system_utilization_percent"],
        average_congestion_level=all_status["average_congestion_level"]
    )


@router.put("/{gate_id}", response_model=CrowdStatusResponse)
async def update_crowd(gate_id: str, request: CrowdUpdateRequest) -> CrowdStatusResponse:
    """
    Manually update crowd count for a gate
    
    - **gate_id**: Gate identifier (A, B, C, D)
    - **crowd_change**: Number to add (positive) or remove (negative)
    
    Returns: Updated crowd status or 404 if gate not found
    """
    crowd_data = CrowdService.manual_crowd_change(gate_id, request)
    if not crowd_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate {gate_id} not found"
        )
    
    return CrowdStatusResponse(**crowd_data.dict())


@router.get("/metrics/all", response_model=CrowdMetricsResponse)
async def get_crowd_metrics() -> CrowdMetricsResponse:
    """
    Get detailed crowd metrics across all gates
    
    Returns: System-wide crowd metrics
    """
    metrics = CrowdService.get_crowd_metrics()
    
    return CrowdMetricsResponse(**metrics)
