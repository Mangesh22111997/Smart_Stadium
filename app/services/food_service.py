"""
Food Service - Business logic for food ordering
"""
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models.food import (
    FoodOrder, MenuItem, OrderItem, FoodOrderRequest, BoothStatus
)

# ============================================================================
# MENU DATABASE (Static)
# ============================================================================

MENU_ITEMS = [
    # Snacks
    MenuItem(
        item_id="pizza_001",
        name="Margherita Pizza",
        price=150.0,
        category="snacks",
        preparation_time=12
    ),
    MenuItem(
        item_id="burger_001",
        name="Classic Burger",
        price=120.0,
        category="snacks",
        preparation_time=8
    ),
    MenuItem(
        item_id="fries_001",
        name="French Fries",
        price=80.0,
        category="snacks",
        preparation_time=5
    ),
    MenuItem(
        item_id="nachos_001",
        name="Cheesy Nachos",
        price=100.0,
        category="snacks",
        preparation_time=6
    ),
    # Beverages
    MenuItem(
        item_id="coke_001",
        name="Coca Cola",
        price=50.0,
        category="beverages",
        preparation_time=2
    ),
    MenuItem(
        item_id="juice_001",
        name="Fresh Orange Juice",
        price=80.0,
        category="beverages",
        preparation_time=3
    ),
    MenuItem(
        item_id="water_001",
        name="Bottled Water",
        price=30.0,
        category="beverages",
        preparation_time=1
    ),
    # Main Dishes
    MenuItem(
        item_id="biryani_001",
        name="Chicken Biryani",
        price=250.0,
        category="main",
        preparation_time=15
    ),
    MenuItem(
        item_id="paneer_001",
        name="Paneer Butter Masala",
        price=200.0,
        category="main",
        preparation_time=12
    ),
]

# ============================================================================
# BOOTH DATABASE
# ============================================================================

BOOTHS = {
    "B01": BoothStatus(booth_id="B01", current_orders=0, max_capacity=10),
    "B02": BoothStatus(booth_id="B02", current_orders=0, max_capacity=10),
    "B03": BoothStatus(booth_id="B03", current_orders=0, max_capacity=10),
    "B04": BoothStatus(booth_id="B04", current_orders=0, max_capacity=10),
    "B05": BoothStatus(booth_id="B05", current_orders=0, max_capacity=10),
}

# ============================================================================
# ORDER DATABASE
# ============================================================================

orders_db: Dict[UUID, FoodOrder] = {}
user_orders: Dict[UUID, List[UUID]] = {}


# ============================================================================
# FOOD SERVICE CLASS
# ============================================================================

class FoodService:
    """
    Service class for managing food orders
    """

    @staticmethod
    def get_menu() -> List[MenuItem]:
        """
        Get all menu items
        
        Returns:
            List of MenuItem objects
        """
        return MENU_ITEMS.copy()

    @staticmethod
    def get_menu_item(item_id: str) -> Optional[MenuItem]:
        """
        Get specific menu item by ID
        
        Args:
            item_id: Menu item ID
            
        Returns:
            MenuItem or None if not found
        """
        for item in MENU_ITEMS:
            if item.item_id == item_id:
                return item
        return None

    @staticmethod
    def _find_best_booth() -> str:
        """
        Find booth with least orders
        
        Returns:
            Booth ID with lowest utilization
        """
        best_booth = "B01"
        min_orders = BOOTHS["B01"].current_orders
        
        for booth_id, booth in BOOTHS.items():
            if booth.current_orders < min_orders:
                min_orders = booth.current_orders
                best_booth = booth_id
        
        return best_booth

    @staticmethod
    def _calculate_prep_time(items: List[OrderItem]) -> int:
        """
        Calculate total preparation time for order
        
        Args:
            items: List of order items
            
        Returns:
            Maximum prep time among items (minutes)
        """
        max_prep_time = 0
        
        for item in items:
            menu_item = FoodService.get_menu_item(item.item_id)
            if menu_item and menu_item.preparation_time > max_prep_time:
                max_prep_time = menu_item.preparation_time
        
        return max(max_prep_time, 5)  # Minimum 5 minutes

    @staticmethod
    def _calculate_queue_delay(booth_id: str, avg_service_time: int = 3) -> int:
        """
        Calculate queue delay at booth
        
        Args:
            booth_id: Booth identifier
            avg_service_time: Average service time per order (minutes)
            
        Returns:
            Queue delay in minutes
        """
        booth = BOOTHS.get(booth_id)
        if not booth:
            return 0
        
        return booth.current_orders * avg_service_time

    @staticmethod
    def _calculate_pickup_time(prep_time: int, queue_delay: int) -> str:
        """
        Calculate pickup time for order
        
        Args:
            prep_time: Preparation time (minutes)
            queue_delay: Queue delay (minutes)
            
        Returns:
            Pickup time as HH:MM string
        """
        now = datetime.now()
        total_delay = timedelta(minutes=prep_time + queue_delay)
        pickup_time = now + total_delay
        
        return pickup_time.strftime("%H:%M")

    @staticmethod
    def place_order(request: FoodOrderRequest) -> FoodOrder:
        """
        Place a new food order
        
        Args:
            request: FoodOrderRequest with order details
            
        Returns:
            Created FoodOrder object
        """
        # Find best booth
        booth_id = FoodService._find_best_booth()
        
        # Calculate prices and prep time
        total_price = sum(item.quantity * item.unit_price for item in request.items)
        prep_time = FoodService._calculate_prep_time(request.items)
        
        # Calculate queue delay
        queue_delay = FoodService._calculate_queue_delay(booth_id)
        
        # Calculate pickup time
        pickup_time = FoodService._calculate_pickup_time(prep_time, queue_delay)
        
        # Create order
        order_id = uuid4()
        order = FoodOrder(
            order_id=order_id,
            user_id=request.user_id,
            ticket_id=request.ticket_id,
            items=request.items,
            booth_id=booth_id,
            delivery_zone=request.delivery_zone,
            total_price=total_price,
            pickup_time=pickup_time,
            status="confirmed",
            ordered_at=datetime.now(),
            estimated_prep_time=prep_time + queue_delay
        )
        
        # Store order
        orders_db[order_id] = order
        
        # Track in user orders
        if request.user_id not in user_orders:
            user_orders[request.user_id] = []
        user_orders[request.user_id].append(order_id)
        
        # Update booth
        BOOTHS[booth_id].current_orders += 1
        BOOTHS[booth_id].orders.append(order_id)
        
        print(f"✅ Food order placed: {order_id} at Booth {booth_id}, Pickup: {pickup_time}")
        return order

    @staticmethod
    def get_order(order_id: UUID) -> Optional[FoodOrder]:
        """
        Get order by ID
        
        Args:
            order_id: Order ID
            
        Returns:
            FoodOrder or None if not found
        """
        return orders_db.get(order_id)

    @staticmethod
    def get_user_orders(user_id: UUID) -> List[FoodOrder]:
        """
        Get all orders for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of FoodOrder objects
        """
        order_ids = user_orders.get(user_id, [])
        return [orders_db[oid] for oid in order_ids if oid in orders_db]

    @staticmethod
    def update_order_status(order_id: UUID, new_status: str) -> Optional[FoodOrder]:
        """
        Update order status
        
        Args:
            order_id: Order ID
            new_status: New status
            
        Returns:
            Updated FoodOrder or None if not found
        """
        if order_id not in orders_db:
            return None
        
        order = orders_db[order_id]
        old_status = order.status
        order.status = new_status
        
        # If picked up, decrement booth orders
        if new_status == "picked_up" and old_status != "picked_up":
            booth = BOOTHS.get(order.booth_id)
            if booth and order_id in booth.orders:
                booth.orders.remove(order_id)
                booth.current_orders = max(0, booth.current_orders - 1)
        
        print(f"✅ Order status updated: {order_id} {old_status}→{new_status}")
        return order

    @staticmethod
    def cancel_order(order_id: UUID) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            
        Returns:
            True if cancelled, False if not found
        """
        if order_id not in orders_db:
            return False
        
        order = orders_db[order_id]
        
        # Remove from booth
        booth = BOOTHS.get(order.booth_id)
        if booth and order_id in booth.orders:
            booth.orders.remove(order_id)
            booth.current_orders = max(0, booth.current_orders - 1)
        
        # Mark as cancelled
        order.status = "cancelled"
        
        print(f"✅ Order cancelled: {order_id}")
        return True

    @staticmethod
    def get_booth_status(booth_id: str) -> Optional[Dict]:
        """
        Get booth status
        
        Args:
            booth_id: Booth identifier
            
        Returns:
            Booth status dictionary or None
        """
        if booth_id not in BOOTHS:
            return None
        
        booth = BOOTHS[booth_id]
        utilization = (booth.current_orders / booth.max_capacity) * 100
        wait_time = booth.current_orders * 3  # 3 min per order
        
        return {
            "booth_id": booth_id,
            "current_orders": booth.current_orders,
            "max_capacity": booth.max_capacity,
            "utilization_percent": round(utilization, 2),
            "estimated_wait_time": wait_time
        }

    @staticmethod
    def get_all_booths_status() -> List[Dict]:
        """
        Get status of all booths
        
        Returns:
            List of booth status dictionaries
        """
        return [
            FoodService.get_booth_status(booth_id)
            for booth_id in sorted(BOOTHS.keys())
        ]

    @staticmethod
    def clear_all():
        """
        Clear all orders (for testing)
        """
        orders_db.clear()
        user_orders.clear()
        for booth in BOOTHS.values():
            booth.current_orders = 0
            booth.orders.clear()
        print("✅ All food orders cleared")
