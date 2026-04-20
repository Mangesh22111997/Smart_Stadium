"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Food models using Pydantic for validation
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal

# ============================================================================
# MENU MODELS
# ============================================================================

class MenuItem(BaseModel):
    """
    Model for menu item
    """
    item_id: str
    name: str
    price: float = Field(..., gt=0)
    category: Literal["snacks", "beverages", "main"]
    preparation_time: int = Field(..., gt=0, description="Minutes")

    class Config:
        example = {
            "item_id": "pizza_001",
            "name": "Margherita Pizza",
            "price": 150.0,
            "category": "snacks",
            "preparation_time": 12
        }


class OrderItem(BaseModel):
    """
    Model for item in order
    """
    item_id: str
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

    class Config:
        example = {
            "item_id": "pizza_001",
            "name": "Margherita Pizza",
            "quantity": 1,
            "unit_price": 150.0
        }


# ============================================================================
# REQUEST MODELS (for API input)
# ============================================================================

class FoodOrderRequest(BaseModel):
    """
    Model for food order request
    """
    user_id: UUID
    ticket_id: Optional[UUID] = None
    items: List[OrderItem] = Field(..., min_items=1)
    delivery_zone: str = Field(
        default="center",
        description="Delivery zone: pillar_1, pillar_2, pillar_3, pillar_4, center"
    )

    class Config:
        example = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "items": [
                {
                    "item_id": "pizza_001",
                    "name": "Margherita Pizza",
                    "quantity": 1,
                    "unit_price": 150.0
                }
            ],
            "delivery_zone": "pillar_1"
        }


class OrderStatusUpdateRequest(BaseModel):
    """
    Model for order status update
    """
    status: Literal["pending", "confirmed", "preparing", "ready", "picked_up", "cancelled"]

    class Config:
        example = {
            "status": "ready"
        }


# ============================================================================
# RESPONSE MODELS (for API output)
# ============================================================================

class FoodOrderResponse(BaseModel):
    """
    Model for food order response
    """
    order_id: str
    user_id: UUID
    ticket_id: Optional[UUID] = None
    items: List[OrderItem]
    booth_id: str
    delivery_zone: str
    total_price: float
    pickup_time: str
    status: str
    ordered_at: datetime
    estimated_prep_time: int

    class Config:
        example = {
            "order_id": "FOOD-1234",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440002",
            "items": [],
            "booth_id": "B01",
            "delivery_zone": "pillar_1",
            "total_price": 150.0,
            "pickup_time": "12:45",
            "status": "confirmed",
            "ordered_at": "2026-04-14T12:25:00",
            "estimated_prep_time": 15
        }


class MenuResponse(BaseModel):
    """
    Model for menu response
    """
    items: List[MenuItem]
    total_items: int

    class Config:
        example = {
            "items": [],
            "total_items": 10
        }


class BoothStatusResponse(BaseModel):
    """
    Model for booth status response
    """
    booth_id: str
    current_orders: int
    max_capacity: int
    utilization_percent: float
    estimated_wait_time: int

    class Config:
        example = {
            "booth_id": "B01",
            "current_orders": 5,
            "max_capacity": 10,
            "utilization_percent": 50.0,
            "estimated_wait_time": 5
        }


# ============================================================================
# INTERNAL MODELS (for storage)
# ============================================================================

class FoodOrder(BaseModel):
    """
    Internal Food Order model for storage
    """
    order_id: str
    user_id: UUID
    ticket_id: Optional[UUID] = None
    items: List[OrderItem]
    booth_id: str
    delivery_zone: str
    total_price: float
    pickup_time: str
    status: str
    ordered_at: datetime
    estimated_prep_time: int

    class Config:
        from_attributes = True


class BoothStatus(BaseModel):
    """
    Internal Booth Status model for tracking
    """
    booth_id: str
    current_orders: int
    max_capacity: int
    orders: List[UUID] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
