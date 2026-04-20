# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Booth Allocation Routes - API endpoints for booth allocation
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import Literal

from app.models.booth_allocation import (
    BoothAllocationResponse,
    TopBoothsResponse,
    DistanceMetricsResponse,
    BoothAllocationRequest,
    BoothReallocationRequest
)
from app.services.booth_allocation_service import BoothAllocationService

# Create router
router = APIRouter(prefix="/booths", tags=["Booth Allocation"])

# ============================================================================
# BOOTH ALLOCATION ENDPOINTS
# ============================================================================

@router.post("/allocate", response_model=BoothAllocationResponse, status_code=status.HTTP_200_OK)
async def allocate_booth(request: BoothAllocationRequest) -> BoothAllocationResponse:
    """
    Find the best booth for a user based on zone and crowd
    
    - **user_id**: UUID of the user
    - **delivery_zone**: User's delivery zone (pillar_1, pillar_2, pillar_3, pillar_4, center)
    
    Returns: Best booth allocation with scores and queue info
    """
    allocation = BoothAllocationService.allocate_booth(
        str(request.user_id),
        request.delivery_zone
    )
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not allocate booth"
        )
    
    return BoothAllocationResponse(**allocation.dict())


@router.get("/allocate/top/{zone}", response_model=TopBoothsResponse)
async def get_top_booths(
    zone: Literal["pillar_1", "pillar_2", "pillar_3", "pillar_4", "center"] = "center"
) -> TopBoothsResponse:
    """
    Get top 3 best booths for a zone
    
    - **zone**: Delivery zone
    
    Returns: Top 3 booth options with scores
    """
    booths = BoothAllocationService.get_top_booths(zone, top_n=3)
    
    return TopBoothsResponse(
        zone=zone,
        top_booths=[BoothAllocationResponse(**booth.dict()) for booth in booths],
        total_booths=len(booths)
    )


@router.get("/distance/{booth_id}/{zone}", response_model=DistanceMetricsResponse)
async def get_distance_metrics(
    booth_id: str,
    zone: Literal["pillar_1", "pillar_2", "pillar_3", "pillar_4", "center"] = "center"
) -> DistanceMetricsResponse:
    """
    Get distance metrics between booth and zone
    
    - **booth_id**: Booth identifier (B01-B05)
    - **zone**: Delivery zone
    
    Returns: Distance metrics or 400 if invalid
    """
    if booth_id not in ["B01", "B02", "B03", "B04", "B05"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid booth ID: {booth_id}"
        )
    
    metrics = BoothAllocationService.get_distance_to_booth(booth_id, zone)
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booth {booth_id} not found"
        )
    
    return DistanceMetricsResponse(**metrics)


@router.post("/reallocate", response_model=BoothAllocationResponse)
async def reallocate_booth(request: BoothReallocationRequest) -> BoothAllocationResponse:
    """
    Reallocate an order to a better booth based on current conditions
    
    - **order_id**: UUID of the order
    - **reason**: Reason for reallocation (e.g., "Too crowded", "User preference")
    
    Returns: New booth allocation or 400 if order not found
    """
    allocation = BoothAllocationService.reallocate_order(
        str(request.order_id),
        request.reason
    )
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {request.order_id} not found"
        )
    
    return BoothAllocationResponse(**allocation.dict())
