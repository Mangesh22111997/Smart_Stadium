"""
Tests for FoodService — menu retrieval and order routing.
"""

import pytest
from app.services.food_service import FoodService


@pytest.mark.unit
def test_menu_returns_items(mock_firebase):
    """Menu endpoint should return a non-empty list of food items."""
    mock_firebase.get.return_value.val.return_value = {
        "item_001": {"name": "Burger", "price": 150, "category": "meal"},
        "item_002": {"name": "Coke", "price": 60, "category": "beverage"},
    }
    menu = FoodService.get_menu()
    assert isinstance(menu, list)
    assert len(menu) >= 1


@pytest.mark.unit
def test_nearest_booth_assignment_returns_valid_booth():
    """Booth assignment should return a valid booth identifier."""
    booth = FoodService.get_nearest_booth(zone="A", order_type="meal")
    assert booth is not None


@pytest.mark.unit
def test_order_creation_returns_order_id(mock_firebase):
    """Placing a food order should return an order ID."""
    mock_firebase.push.return_value = {"name": "ORDER123"}

    from app.models.food import FoodOrderRequest
    order = FoodOrderRequest(
        user_id="user123",
        zone="A",
        items=[{"item_id": "item_001", "quantity": 2}]
    )
    result = FoodService.create_order(order)
    assert result is not None
