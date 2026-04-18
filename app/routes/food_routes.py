"""
Food Routes - API endpoints for food ordering
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List

from app.models.food import (
    FoodOrderResponse,
    MenuResponse,
    BoothStatusResponse,
    FoodOrderRequest,
    OrderStatusUpdateRequest,
    MenuItem
)
from app.services.food_service import FoodService

# Create router
router = APIRouter(prefix="/food", tags=["Food"])

# ============================================================================
# FOOD ENDPOINTS
# ============================================================================

@router.post("/orders", response_model=FoodOrderResponse, status_code=status.HTTP_201_CREATED)
async def place_food_order(request: FoodOrderRequest) -> FoodOrderResponse:
    """
    Place a new food order
    
    - **user_id**: UUID of the user
    - **ticket_id**: UUID of the ticket
    - **items**: List of items to order
    - **delivery_zone**: Delivery zone (pillar_1, pillar_2, pillar_3, pillar_4, center)
    
    Returns: Created order with booth assignment and pickup time
    """
    order = FoodService.place_order(request)
    return FoodOrderResponse(**order.dict())


@router.get("/orders/{order_id}", response_model=FoodOrderResponse)
async def get_food_order(order_id: str) -> FoodOrderResponse:
    """
    Get food order details
    
    - **order_id**: UUID of the order
    
    Returns: Order details or 404 if not found
    """
    order = FoodService.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    return FoodOrderResponse(**order.dict())


@router.get("/orders/user/{user_id}", response_model=List[FoodOrderResponse])
async def get_user_food_orders(user_id: UUID) -> List[FoodOrderResponse]:
    """
    Get all food orders for a user
    
    - **user_id**: UUID of the user
    
    Returns: List of user's orders
    """
    orders = FoodService.get_user_orders(user_id)
    return [FoodOrderResponse(**order.dict()) for order in orders]


@router.get("/menu", response_model=MenuResponse)
async def get_menu() -> MenuResponse:
    """
    Get food menu with all available items
    
    Returns: Menu with items and categories
    """
    items = FoodService.get_menu()
    return MenuResponse(items=items, total_items=len(items))


@router.put("/orders/{order_id}/status", response_model=FoodOrderResponse)
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdateRequest
) -> FoodOrderResponse:
    """
    Update food order status
    
    - **order_id**: UUID of the order
    - **status**: New status (pending, confirmed, preparing, ready, picked_up, cancelled)
    
    Returns: Updated order or 404 if not found
    """
    order = FoodService.update_order_status(order_id, request.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    return FoodOrderResponse(**order.dict())


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_food_order(order_id: str):
    """
    Cancel a food order
    
    - **order_id**: UUID of the order
    
    Returns: 204 No Content or 404 if not found
    """
    cancelled = FoodService.cancel_order(order_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    return None


@router.get("/booths/{booth_id}", response_model=BoothStatusResponse)
async def get_booth_status(booth_id: str) -> BoothStatusResponse:
    """
    Get status of a specific booth
    
    - **booth_id**: Booth identifier (B01-B05)
    
    Returns: Booth status or 404 if not found
    """
    status_data = FoodService.get_booth_status(booth_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booth {booth_id} not found"
        )
    
    return BoothStatusResponse(**status_data)


@router.get("/booths/status/all", response_model=List[BoothStatusResponse])
async def get_all_booths_status() -> List[BoothStatusResponse]:
    """
    Get status of all food booths
    
    Returns: Status of all booths with utilization and wait times
    """
    booths_status = FoodService.get_all_booths_status()
    return [BoothStatusResponse(**booth) for booth in booths_status]
