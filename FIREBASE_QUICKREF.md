# Firebase Firestore Integration - Quick Reference Card

**Print this or save as bookmark!** | **Updated**: April 18, 2026

---

## 🔧 Installation (2 minutes)

```bash
# 1. Install Firebase
pip install firebase-admin==6.5.0

# 2. Get credentials from Firebase Console
# Project Settings → Service Accounts → Generate Key → Download JSON

# 3. Save as firebase-key.json in project root

# 4. Test
python test_firebase_connection.py
```

---

## 📁 File Locations

```
NEW files created:
├── app/config/firebase_config.py
├── app/services/firebase_service.py
├── app/services/firestore_collections_service.py
├── app/config/FIREBASE_SETUP_GUIDE.py
├── FIREBASE_FIRESTORE_INTEGRATION.md (main guide)
├── FIREBASE_DELIVERY_SUMMARY.md
├── FIREBASE_IMPLEMENTATION_CHECKLIST.md
└── FIREBASE_QUICKREF.md (this file)
```

---

## ⚡ Quick Examples

### Initialize Firebase
```python
from app.config.firebase_config import FirebaseConfig

@app.on_event("startup")
async def startup():
    FirebaseConfig()  # One line!
```

### Get Services
```python
from app.services.firestore_collections_service import (
    get_firestore_user_service,
    get_firestore_ticket_service,
    get_firestore_food_order_service,
    get_firestore_emergency_service
)

user_service = get_firestore_user_service()
ticket_service = get_firestore_ticket_service()
food_service = get_firestore_food_order_service()
emergency_service = get_firestore_emergency_service()
```

### Create Document
```python
# User
user = User(user_id=uuid4(), name="John", email="john@example.com")
doc_id = await user_service.create_user(user)

# Ticket
ticket = Ticket(ticket_id=uuid4(), user_id=user_id, event_id="EVT_001")
doc_id = await ticket_service.create_ticket(ticket)

# Food Order
order = FoodOrder(order_id=uuid4(), user_id=user_id, items=["pizza"])
doc_id = await food_service.create_food_order(order)
```

### Read Document
```python
# Get single user
user = await user_service.get_user_by_id(user_id)

# Get by email
user = await user_service.get_user_by_email("john@example.com")

# Get all users (limit 100)
users = await user_service.get_all_users(limit=100)

# Get user's tickets
tickets = await ticket_service.get_tickets_by_user(user_id)

# Get pending orders
pending = await food_service.get_pending_orders(limit=50)

# Get active emergencies
emergencies = await emergency_service.get_active_emergencies()
```

### Update Document
```python
# Update user
await user_service.update_user(user_id, {"phone": "1234567890"})

# Update ticket status
await ticket_service.update_ticket_status(ticket_id, "USED")

# Update order status
await food_service.update_order_status(order_id, "READY", booth_id="B1")

# Update emergency
await emergency_service.update_emergency_status(emergency_id, "RESOLVED")
```

### Delete Document
```python
from app.services.firebase_service import get_firestore_service

fs = get_firestore_service()

# Delete entire document
await fs.delete_document("users", user_id)

# Delete specific field
await fs.delete_field("users", user_id, "temporary_field")
```

### Batch Operations
```python
fs = get_firestore_service()

# Batch create
doc_ids = await fs.batch_create("users", [
    ("user_1", {"name": "Alice"}),
    ("user_2", {"name": "Bob"}),
    (None, {"name": "Charlie"})  # Auto-ID
])

# Batch update
await fs.batch_update("tickets", {
    "ticket_1": {"status": "USED"},
    "ticket_2": {"status": "USED"},
    "ticket_3": {"status": "USED"}
})
```

### Query Documents
```python
fs = get_firestore_service()

# Query single field
users = await fs.query_documents(
    collection="users",
    field="email",
    operator="==",
    value="john@example.com"
)

# Operators: '==', '<', '>', '<=', '>=', '!='

# With limit
pending_orders = await fs.query_documents(
    collection="food_orders",
    field="status",
    operator="==",
    value="PENDING",
    limit=50
)
```

---

## 📚 Collections & Fields

### Users Collection
```json
{
  "user_id": "uuid",
  "name": "John",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password_hash": "sha256hash",
  "commute_preference": "metro",
  "departure_preference": "early",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "is_active": true
}
```

### Tickets Collection
```json
{
  "ticket_id": "uuid",
  "user_id": "uuid",
  "event_id": "EVT_001",
  "seat_zone": "A",
  "seat_row": 10,
  "seat_number": 5,
  "price": 1000,
  "status": "CONFIRMED",
  "gate_assignment": "Gate A",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Food Orders Collection
```json
{
  "order_id": "uuid",
  "user_id": "uuid",
  "event_id": "EVT_001",
  "items": ["pizza", "coke"],
  "booth_id": "B1",
  "total_amount": 500,
  "status": "PENDING",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "estimated_ready_time": "timestamp"
}
```

### Emergencies Collection
```json
{
  "emergency_id": "EM_001_20260418",
  "type": "FIRE",
  "location": "North Gate",
  "severity": "HIGH",
  "description": "Fire detected",
  "reported_by": "uuid",
  "status": "ACTIVE",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "responded": false,
  "response_time_minutes": null,
  "updates": [
    {
      "message": "Fire brigade called",
      "updated_by": "STAFF_001",
      "timestamp": "timestamp"
    }
  ]
}
```

---

## 🔑 Collection Constants

```python
from app.config.firebase_config import Collections

Collections.USERS              # "users"
Collections.TICKETS           # "tickets"
Collections.FOOD_ORDERS       # "food_orders"
Collections.EMERGENCIES       # "emergencies"
Collections.GATES             # "gates"
Collections.CROWD_DATA        # "crowd_data"
Collections.NOTIFICATIONS     # "notifications"
Collections.STAFF             # "staff"
Collections.BOOTH_ALLOCATION  # "booth_allocation"
```

---

## 🚀 Route Handler Pattern

```python
from fastapi import APIRouter, HTTPException, status

@router.post("/users/register")
async def register_user(request: UserRegisterRequest):
    try:
        user_service = get_firestore_user_service()
        user = User(...)
        doc_id = await user_service.create_user(user)
        
        return {
            "success": True,
            "user_id": doc_id,
            "message": "✅ User registered"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

---

## 🔍 Common Queries

```python
# Get user by ID
user = await user_service.get_user_by_id(user_id)

# Get user by email
user = await user_service.get_user_by_email("john@example.com")

# Get all user tickets
tickets = await ticket_service.get_tickets_by_user(user_id)

# Get event tickets
event_tickets = await ticket_service.get_tickets_by_event("EVT_001")

# Get pending food orders
pending = await food_service.get_pending_orders(limit=50)

# Get orders by status
ready = await food_service.get_orders_by_status("READY")

# Get active emergencies
active_em = await emergency_service.get_active_emergencies()

# Get critical emergencies
critical = await emergency_service.get_emergencies_by_severity("CRITICAL")
```

---

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Credentials not found" | Set FIREBASE_CREDENTIALS_JSON or place firebase-key.json in root |
| "Permission denied" | Check Firestore security rules are set |
| "Async context error" | Make route handler `async` |
| "Collection not found" | Create in Firebase Console or it auto-creates on first write |
| "Slow queries" | Create composite indexes (Firebase Console) |
| "Too many requests" | Check billing limits, add billing alert |

---

## 📊 Methods by Service

### FirestoreService (Generic)
```
create_document()           batch_create()
get_document()             batch_update()
get_all_documents()        query_documents()
update_document()          increment_field()
add_to_array()            remove_from_array()
delete_document()         delete_field()
```

### FirestoreUserService
```
create_user()              get_user_by_id()
get_user_by_email()        update_user()
get_all_users()            deactivate_user()
```

### FirestoreTicketService
```
create_ticket()            get_ticket_by_id()
get_tickets_by_user()      get_tickets_by_event()
update_ticket_status()
```

### FirestoreFoodOrderService
```
create_food_order()        get_food_order_by_id()
get_orders_by_user()       get_orders_by_status()
get_pending_orders()       update_order_status()
```

### FirestoreEmergencyService
```
create_emergency()         get_emergency_by_id()
get_active_emergencies()   get_emergencies_by_severity()
update_emergency_status()  add_emergency_update()
```

---

## 🔗 Useful Links

- **Firebase Console**: https://console.firebase.google.com
- **Firestore Docs**: https://firebase.google.com/docs/firestore
- **Python Admin SDK**: https://firebase.google.com/docs/database/admin/start
- **Security Rules**: https://firebase.google.com/docs/firestore/security/get-started

---

## ✅ Implementation Checklist

Quick boxes to check:

- [ ] Install firebase-admin
- [ ] Get credentials
- [ ] Create Firestore database
- [ ] Create 4 collections
- [ ] Test connection
- [ ] Update first service
- [ ] Make routes async
- [ ] Test end-to-end
- [ ] Update all routes
- [ ] Remove in-memory DBs
- [ ] Deploy to production

---

## 💾 Environment Setup

```bash
# .env (add to .gitignore)
FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Or use file
GOOGLE_APPLICATION_CREDENTIALS=firebase-key.json

# Or use firebase-key.json directly (add to .gitignore)
```

---

## 📈 Performance Metrics

| Operation | Time |
|-----------|------|
| Single read | ~50-100ms |
| Single write | ~50-100ms |
| Query | ~100-200ms |
| Batch 100 | ~500-1000ms |
| Batch 1000 | ~5-10s |

---

## 💰 Pricing (Monthly)

| Operation | Cost |
|-----------|------|
| Read (per 100K) | $0.06 |
| Write (per 100K) | $0.18 |
| Delete (per 100K) | $0.18 |
| Storage (per GB) | $0.18 |

**Free tier**: 50K reads/writes/day + 1GB storage ✅

---

## 🆘 Help Commands

```bash
# Test connection
python test_firebase_connection.py

# Run specific test
python -m pytest tests/test_user_service.py -v

# Check Firebase version
pip show firebase-admin

# Update Firebase
pip install --upgrade firebase-admin
```

---

## 📞 Get Help

1. **Setup issues**: Read `FIREBASE_SETUP_GUIDE.py`
2. **Code examples**: See `MIGRATION_EXAMPLES.py`
3. **Full guide**: Read `FIREBASE_FIRESTORE_INTEGRATION.md`
4. **Quick ref**: See `FIREBASE_IMPLEMENTATION_CHECKLIST.md`
5. **Official docs**: https://firebase.google.com/docs/firestore

---

**Print & Save This Card!** | Last Updated: April 18, 2026
