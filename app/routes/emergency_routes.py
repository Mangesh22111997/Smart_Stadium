"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Emergency Routes - API endpoints for emergency handling
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List

from app.models.emergency import (
    EmergencyResponse,
    EmergencyListResponse,
    NearestExitResponse,
    EmergencySOSRequest,
    EmergencyStatusUpdateRequest
)
from app.services.emergency_service import EmergencyService

# Create router
router = APIRouter(prefix="/emergency", tags=["Emergency"])

# ============================================================================
# EMERGENCY ENDPOINTS
# ============================================================================

@router.post("/sos", response_model=EmergencyResponse, status_code=status.HTTP_201_CREATED)
async def trigger_sos(request: EmergencySOSRequest) -> EmergencyResponse:
    """
    Trigger an emergency SOS
    
    - **user_id**: UUID of the user
    - **emergency_type**: medical, crowd, lost, threat, fire, evacuation, lost_child, harassment, other
    - **location**: Current location (gate_a, gate_b, pillar_1, etc.)
    - **description**: Description of the emergency
    
    Returns: Emergency details with nearest exit and priority
    """
    emergency = EmergencyService.trigger_sos(request)
    return EmergencyResponse(**emergency.dict())


@router.get("/{emergency_id}", response_model=EmergencyResponse)
async def get_emergency(emergency_id: UUID) -> EmergencyResponse:
    """
    Get emergency details by ID
    
    - **emergency_id**: UUID of the emergency
    
    Returns: Emergency information or 404 if not found
    """
    emergency = EmergencyService.get_emergency(emergency_id)
    if not emergency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency {emergency_id} not found"
        )
    
    return EmergencyResponse(**emergency.dict())


@router.get("/list/active", response_model=EmergencyListResponse)
async def get_active_emergencies() -> EmergencyListResponse:
    """
    Get all active emergencies (reported or responding)
    
    Returns: List of active emergencies with summary
    """
    emergencies = EmergencyService.get_active_emergencies()
    all_emergencies = list(EmergencyService.emergencies_db.values()) if hasattr(EmergencyService, 'emergencies_db') else []
    
    return EmergencyListResponse(
        total=len(all_emergencies),
        active=len(emergencies),
        emergencies=[EmergencyResponse(**e.dict()) for e in emergencies]
    )


@router.get("/user/{user_id}", response_model=List[EmergencyResponse])
async def get_user_emergencies(user_id: UUID) -> List[EmergencyResponse]:
    """
    Get all emergencies reported by a user
    
    - **user_id**: UUID of the user
    
    Returns: List of user's emergencies
    """
    emergencies = EmergencyService.get_user_emergencies(user_id)
    return [EmergencyResponse(**e.dict()) for e in emergencies]


@router.put("/{emergency_id}/status", response_model=EmergencyResponse)
async def update_emergency_status(
    emergency_id: UUID,
    request: EmergencyStatusUpdateRequest
) -> EmergencyResponse:
    """
    Update emergency status
    
    - **emergency_id**: UUID of the emergency
    - **status**: New status (reported, responding, resolved, cancelled)
    - **notes**: Additional notes (optional)
    
    Returns: Updated emergency or 404 if not found
    """
    emergency = EmergencyService.update_emergency_status(emergency_id, request)
    if not emergency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency {emergency_id} not found"
        )
    
    return EmergencyResponse(**emergency.dict())


@router.post("/nearest-exit", response_model=NearestExitResponse)
async def find_nearest_exit(request: dict) -> NearestExitResponse:
    """
    Find nearest exit from a location
    
    - **location**: Current location (gate_a, pillar_1, center, etc.)
    
    Returns: Nearest exit with distance and direction
    """
    location = request.get("location", "center")
    exit_info = EmergencyService.find_nearest_exit(location)
    
    return NearestExitResponse(
        exit_id=exit_info["exit_id"],
        location=exit_info["location"],
        distance_meters=exit_info["distance_meters"],
        direction=exit_info["direction"],
        coordinates=exit_info.get("coordinates")
    )


@router.get("/statistics/summary", response_model=dict)
async def get_emergency_statistics() -> dict:
    """
    Get emergency statistics and summary
    
    Returns: Statistics about emergencies by priority and type
    """
    return EmergencyService.get_emergency_statistics()


@router.get("/priority/{priority}", response_model=List[EmergencyResponse])
async def get_emergencies_by_priority(priority: str) -> List[EmergencyResponse]:
    """
    Get emergencies by priority level
    
    - **priority**: CRITICAL, HIGH, MEDIUM, or LOW
    
    Returns: List of emergencies with matching priority
    """
    if priority not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid priority level"
        )
    
    emergencies = EmergencyService.get_emergencies_by_priority(priority)
    return [EmergencyResponse(**e.dict()) for e in emergencies]
