"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Food Routes - API endpoints for food ordering with server-side authentication
"""
from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from typing import List, Dict, Any

from app.models.food import (
    FoodOrderResponse,
    MenuResponse,
    BoothStatusResponse,
    FoodOrderRequest,
    OrderStatusUpdateRequest,
    MenuItem
)
from app.services.food_service import FoodService
from app.utils.auth_middleware import verify_token

# Create router
router = APIRouter(prefix="/food", tags=["Food"])

@router.post("/orders", response_model=FoodOrderResponse, status_code=status.HTTP_201_CREATED)
async def place_food_order(
    request: FoodOrderRequest,
    current_user: dict = Depends(verify_token)
) -> FoodOrderResponse:
    """
    Place a new food order. Requires authentication.
    """
    if str(request.user_id) != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    order = FoodService.place_order(request)
    return FoodOrderResponse(**order.dict())

@router.get("/orders/{order_id}", response_model=FoodOrderResponse)
async def get_food_order(
    order_id: str,
    current_user: dict = Depends(verify_token)
) -> FoodOrderResponse:
    """
    Get food order details. Requires authentication.
    """
    order = FoodService.get_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found")
        
    if str(order.user_id) != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    return FoodOrderResponse(**order.dict())

@router.get("/orders/user/{user_id}", response_model=List[FoodOrderResponse])
async def get_user_food_orders(
    user_id: str,
    current_user: dict = Depends(verify_token)
) -> List[FoodOrderResponse]:
    """
    Get all food orders for a user.
    """
    if user_id != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    orders = FoodService.get_user_orders(user_id)
    return [FoodOrderResponse(**order.dict()) for order in orders]

@router.get("/menu", response_model=MenuResponse)
async def get_menu() -> MenuResponse:
    """
    Get food menu with all available items. (Publicly accessible)
    """
    items = FoodService.get_menu()
    return MenuResponse(items=items, total_items=len(items))

@router.put("/orders/{order_id}/status", response_model=FoodOrderResponse)
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdateRequest,
    current_user: dict = Depends(verify_token)
) -> FoodOrderResponse:
    """
    Update food order status. Only admins or owners (cancellation only) can update.
    """
    order = FoodService.get_order(order_id)
    if not order:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found")

    # Only admin can change status generally, user can only cancel
    if not current_user.get("is_admin") and request.status != "cancelled":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    if request.status == "cancelled" and str(order.user_id) != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    updated_order = FoodService.update_order_status(order_id, request.status)
    return FoodOrderResponse(**updated_order.dict())

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_food_order(
    order_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Cancel a food order.
    """
    order = FoodService.get_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
    if str(order.user_id) != current_user.get("uid") and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
        
    cancelled = FoodService.cancel_order(order_id)
    return None
