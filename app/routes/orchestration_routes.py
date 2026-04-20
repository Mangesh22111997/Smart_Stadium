# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.integration import (
    RegisterAndBookRequest, UserJourneyResponse, ReassignmentRequest,
    EvacuationRequest, EvacuationResponse, FoodOrderingWorkflowRequest,
    FoodOrderingWorkflowResponse, EmergencySOSWorkflowRequest, EmergencySOSWorkflowResponse,
    SyncAllSystemsResponse, SystemHealthResponse, JourneyAnalyticsResponse
)
from app.services import orchestration_service
from app.utils.auth_middleware import verify_token, admin_only


# Create router
router = APIRouter(
    prefix="/api/v1/orchestration",
    tags=["Orchestration"]
)


@router.post("/user-journey/register-and-book", response_model=dict)
async def register_and_book_ticket(request: RegisterAndBookRequest):
    """
    Complete user registration and ticket booking workflow.
    (This is an initial registration flow, so it might be public if creating a new user)
    """
    try:
        result = orchestration_service.OrchestrationService.register_and_book_ticket(
            email=request.email,
            full_name=request.full_name,
            phone=request.phone,
            commute_mode=request.commute_mode,
            parking_required=request.parking_required,
            event_date=request.event_date,
            arrival_time=request.arrival_time
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-journey/{user_id}", response_model=dict)
async def get_user_journey(
    user_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get complete user journey status and history. Protected."""
    if user_id != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    try:
        result = orchestration_service.OrchestrationService.get_user_journey(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redistribute-users", response_model=dict)
async def redistribute_users(
    request: ReassignmentRequest,
    current_user: dict = Depends(admin_only)
):
    """
    Check gates and redistribute users from overcrowded gates.
    ADMIN ONLY.
    """
    try:
        result = orchestration_service.OrchestrationService.check_and_redistribute_users(
            utilization_threshold=request.utilization_threshold,
            max_users_to_move=request.max_users_to_move,
            prefer_preferences=request.prefer_preferences
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evacuation", response_model=EvacuationResponse)
async def orchestrate_evacuation(
    request: EvacuationRequest,
    current_user: dict = Depends(admin_only)
):
    """
    Orchestrate comprehensive emergency evacuation.
    ADMIN ONLY.
    """
    try:
        result = orchestration_service.OrchestrationService.orchestrate_evacuation(
            location=request.location,
            emergency_type=request.emergency_type,
            target_gates=request.target_gates
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/food-ordering/{user_id}", response_model=FoodOrderingWorkflowResponse)
async def orchestrate_food_ordering(
    user_id: str,
    request: FoodOrderingWorkflowRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Orchestrate complete food ordering workflow. Protected.
    """
    if user_id != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    try:
        result = orchestration_service.OrchestrationService.orchestrate_food_ordering(
            user_id=user_id,
            items=request.items
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-sos/{user_id}", response_model=EmergencySOSWorkflowResponse)
async def orchestrate_emergency_sos(
    user_id: str,
    request: EmergencySOSWorkflowRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Orchestrate comprehensive emergency SOS response. Protected.
    """
    if user_id != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    try:
        result = orchestration_service.OrchestrationService.orchestrate_emergency_sos(
            user_id=user_id,
            emergency_type=request.emergency_type,
            location=request.location,
            description=request.description
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-all-systems", response_model=SyncAllSystemsResponse)
async def sync_all_systems(current_user: dict = Depends(admin_only)):
    """Force synchronization of all modules. ADMIN ONLY."""
    try:
        result = orchestration_service.OrchestrationService.sync_all_systems()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(current_user: dict = Depends(admin_only)):
    """Get health status of all integrated modules. ADMIN ONLY."""
    try:
        result = orchestration_service.OrchestrationService.get_system_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-log")
async def get_event_log(
    event_type: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(admin_only)
):
    """Get workflow event log. ADMIN ONLY."""
    try:
        result = orchestration_service.OrchestrationService.get_event_log(
            event_type=event_type,
            limit=limit,
            skip=skip
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journey-analytics", response_model=JourneyAnalyticsResponse)
async def get_journey_analytics(
    time_window: str = Query("24h", pattern="^(1h|6h|24h|7d)$"),
    current_user: dict = Depends(admin_only)
):
    """Get analytics on user journeys. ADMIN ONLY."""
    try:
        result = orchestration_service.OrchestrationService.get_journey_analytics(
            time_window=time_window
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
