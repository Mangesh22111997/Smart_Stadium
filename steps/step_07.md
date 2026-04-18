# 🍔 STEP 7: Food Ordering System

## Status: ✅ COMPLETED

## Objective
Create a food ordering module allowing users to place orders with smart booth allocation and delivery zone management.

## Requirements Met
- ✅ Food order placement
- ✅ Menu items with pricing
- ✅ Pickup booth selection
- ✅ Delivery zone assignment (pillar-based)
- ✅ Smart booth allocation (least crowded)
- ✅ Time slot management
- ✅ Order tracking and cancellation

## API Endpoints

### 1. Place Food Order
```
POST /food/orders
Body:
{
  "user_id": "uuid",
  "ticket_id": "uuid",
  "items": [
    {
      "item_id": "pizza_001",
      "quantity": 1,
      "price": 150
    }
  ],
  "delivery_zone": "pillar_1"
}
Response:
{
  "order_id": "uuid",
  "user_id": "uuid",
  "booth_id": "B01",
  "delivery_zone": "pillar_1",
  "total_price": 150,
  "pickup_time": "12:30",
  "status": "confirmed",
  "estimated_prep_time": 10
}
```

### 2. Get Order
```
GET /food/orders/{order_id}
Response: Order details
```

### 3. List User Orders
```
GET /food/orders/user/{user_id}
Response: All orders by user
```

### 4. Get Menu
```
GET /food/menu
Response: Available items with prices
```

### 5. Update Order Status
```
PUT /food/orders/{order_id}/status
Body:
{
  "status": "ready"
}
Response: Updated order
```

### 6. Cancel Order
```
DELETE /food/orders/{order_id}
Response: 204 No Content
```

## Files Created
- `app/models/food.py` - Food Pydantic models
- `app/services/food_service.py` - Food ordering logic
- `app/routes/food_routes.py` - Food API endpoints

## Data Models
```python
class MenuItem:
  - item_id: str
  - name: str
  - price: float
  - category: str (snacks, beverages, main)
  - preparation_time: int (minutes)

class FoodOrder:
  - order_id: UUID
  - user_id: UUID
  - ticket_id: UUID
  - items: List[OrderItem]
  - booth_id: str
  - delivery_zone: str (pillar location)
  - total_price: float
  - pickup_time: str (HH:MM format)
  - status: str (pending, confirmed, preparing, ready, picked_up, cancelled)
  - ordered_at: datetime
  - estimated_prep_time: int (minutes)
```

## Menu Items
```
Snacks:
- pizza_001: Margherita Pizza - ₹150 (12 min)
- burger_001: Classic Burger - ₹120 (8 min)
- fries_001: French Fries - ₹80 (5 min)
- nachos_001: Cheesy Nachos - ₹100 (6 min)

Beverages:
- coke_001: Coca Cola - ₹50 (2 min)
- juice_001: Fresh Orange Juice - ₹80 (3 min)
- water_001: Bottled Water - ₹30 (1 min)

Main Dishes:
- biryani_001: Chicken Biryani - ₹250 (15 min)
- paneer_001: Paneer Butter Masala - ₹200 (12 min)
```

## Booth Management
```
Booths: B01, B02, B03, B04, B05 (total capacity: 50 orders)
Max queue per booth: 10 orders
Capacity tracking updates dynamically
```

## Delivery Zones (Pillar-based)
```
Stadium Pillars:
- pillar_1: North Gate
- pillar_2: South Gate
- pillar_3: East Gate
- pillar_4: West Gate
- center: Center Stand
```

## Order Status Flow
```
pending → confirmed → preparing → ready → picked_up
          ↓
        cancelled (at any point)
```

## Booth Allocation Algorithm
1. Calculate crowd (queue) at each booth
2. Select booth with minimum queue
3. If tied, prefer nearest to user's delivery zone
4. Assign time slot (5-min increments)
5. Calculate prep + queue time

## Time Slot Calculation
```
Estimated Pickup Time = current_time + prep_time + queue_delay
Queue Delay = (current_queue_size × avg_service_time)
```

## Storage
- Type: In-memory
- Menu: Static list
- Orders: Dynamic tracking
- Booth status: Real-time update

## Key Features
- Smart booth allocation
- Realistic prep times
- Queue management
- Multiple items per order
- Zone-based delivery
- Order status tracking
- Time slot management

## Integration Points
- User: Via user_id
- Ticket: Via ticket_id for validation
- Booth: Via booth allocation

## Use Cases
1. User orders pizza at Booth B01 for Pillar 1
2. System allocates B02 (least crowded)
3. User gets pickup time: 12:45 (10 min prep + 5 min queue)
4. Staff sees order in booth queue
5. User picks up order at assigned time

## Benefits
- No long queues at single booth
- Realistic wait time management
- Multi-zone support for large stadiums
- Real-time order tracking
- Flexible menu management

## Next Steps
→ STEP 8: Smart Booth Allocation
