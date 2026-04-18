from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.integration import (
    RegisterAndBookRequest, UserJourneyResponse, ReassignmentRequest,
    EvacuationRequest, EvacuationResponse, FoodOrderingWorkflowRequest,
    FoodOrderingWorkflowResponse, EmergencySOSWorkflowRequest, EmergencySOSWorkflowResponse,
    SyncAllSystemsResponse, SystemHealthResponse, JourneyAnalyticsResponse
)
from app.services import orchestration_service


# Create router
router = APIRouter(
    prefix="/api/v1/orchestration",
    tags=["Orchestration"]
)


@router.post("/user-journey/register-and-book", response_model=dict)
async def register_and_book_ticket(request: RegisterAndBookRequest):
    """
    Complete user registration and ticket booking workflow
    
    Orchestrates:
    - User registration
    - Ticket booking
    - Gate assignment
    - Notification sending
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
async def get_user_journey(user_id: UUID):
    """Get complete user journey status and history"""
    try:
        result = orchestration_service.OrchestrationService.get_user_journey(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redistribute-users", response_model=dict)
async def redistribute_users(
    request: ReassignmentRequest
):
    """
    Check gates and redistribute users from overcrowded gates
    
    Triggers:
    - Utilization check
    - User reassignment
    - Notifications to affected users
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
async def orchestrate_evacuation(request: EvacuationRequest):
    """
    Orchestrate comprehensive emergency evacuation
    
    Orchestrates:
    - User reassignment from evacuation location
    - Emergency creation
    - Staff assignment
    - Multi-channel notifications
    - Evacuation plan generation
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
    user_id: UUID,
    request: FoodOrderingWorkflowRequest
):
    """
    Orchestrate complete food ordering workflow
    
    Orchestrates:
    - Order placement
    - Booth allocation
    - Crowd level assessment
    - Notifications
    """
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
    user_id: UUID,
    request: EmergencySOSWorkflowRequest
):
    """
    Orchestrate comprehensive emergency SOS response
    
    Orchestrates:
    - Emergency creation
    - Exit route computation
    - Staff assignment
    - Multi-channel alert notifications
    - Evacuation plan generation
    """
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
async def sync_all_systems():
    """Force synchronization of all modules"""
    try:
        result = orchestration_service.OrchestrationService.sync_all_systems()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get health status of all integrated modules"""
    try:
        result = orchestration_service.OrchestrationService.get_system_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/event-log")
async def get_event_log(
    event_type: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """Get workflow event log with filtering and pagination"""
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
    time_window: str = Query("24h", pattern="^(1h|6h|24h|7d)$")
):
    """Get analytics on user journeys"""
    try:
        result = orchestration_service.OrchestrationService.get_journey_analytics(
            time_window=time_window
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
