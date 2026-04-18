# Firebase Firestore Integration Guide

**Duration to Read**: 15 minutes | **Implementation Time**: 30 minutes | **Difficulty**: Intermediate

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)
8. [Migration Guide](#migration-guide)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Firebase Firestore?

**Firestore** is a NoSQL cloud database by Google that:
- ✅ Scales automatically
- ✅ Stores JSON-like documents
- ✅ Has built-in authentication & security
- ✅ Supports real-time synchronization
- ✅ Offers generous free tier (50K read/writes per day)

### Why Replace In-Memory Database?

| Factor | In-Memory | Firestore |
|--------|-----------|-----------|
| **Data Persistence** | ❌ Lost on restart | ✅ Persistent |
| **Scalability** | ❌ Single server | ✅ Global scale |
| **Real-time Updates** | ❌ Manual polling | ✅ Built-in |
| **Cost** | 0 (but limited) | ✅ Free tier + pay-as-you-go |
| **Security** | ❌ Manual rules | ✅ Firestore security rules |
| **Multi-device Access** | ❌ No | ✅ Yes |

### Architecture Overview

```
┌─────────────┐
│  FastAPI    │
│  Routes     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Service Layer          │
│  (Async/await ready)    │
├─────────────────────────┤
│ • UserService           │
│ • TicketService         │
│ • FoodOrderService      │
│ • EmergencyService      │
└──────┬──────────────────┘
       │
       ▼
┌────────────────────────────┐
│ Collection Services        │
├────────────────────────────┤
│ Firestore{User,Ticket,    │
│  FoodOrder,Emergency}...  │
│ Service                    │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│  Generic Firestore Service │
│  (CRUD + Batch + Query)    │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│  Firebase Admin SDK        │
│  + Python async executor   │
└──────┬─────────────────────┘
       │
       ▼
☁️ Google Cloud Firestore
```

---

## Quick Start

### 1. Install Firebase Admin SDK

```bash
pip install firebase-admin google-cloud-firestore
```

### 2. Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create project → Generate service account key (JSON)
3. Save as `firebase-key.json` in project root

### 3. Initialize in Your App

```python
# app/main.py
from app.config.firebase_config import FirebaseConfig

@app.on_event("startup")
async def startup():
    config = FirebaseConfig()
    print("✅ Firebase initialized")

# Now use services
from app.services.firestore_collections_service import (
    get_firestore_user_service
)

user_service = get_firestore_user_service()

# Use in routes
@app.post("/users/register")
async def register(request: UserRegisterRequest):
    return await user_service.create_user(request)
```

### 4. Run Tests

```bash
python test_firebase_connection.py
```

---

## Architecture

### Service Layer Structure

```python
# Tier 1: Generic Firestore Service
FirestoreService
├── create_document()
├── get_document()
├── query_documents()
├── update_document()
├── batch_create()
├── batch_update()
└── delete_document()

# Tier 2: Collection-Specific Services
├── FirestoreUserService
│   ├── create_user()
│   ├── get_user_by_id()
│   ├── get_user_by_email()
│   ├── update_user()
│   └── get_all_users()
│
├── FirestoreTicketService
│   ├── create_ticket()
│   ├── get_ticket_by_id()
│   ├── get_tickets_by_user()
│   ├── get_tickets_by_event()
│   └── update_ticket_status()
│
├── FirestoreFoodOrderService
│   ├── create_food_order()
│   ├── get_food_order_by_id()
│   ├── get_orders_by_user()
│   ├── get_orders_by_status()
│   ├── get_pending_orders()
│   └── update_order_status()
│
└── FirestoreEmergencyService
    ├── create_emergency()
    ├── get_emergency_by_id()
    ├── get_active_emergencies()
    ├── get_emergencies_by_severity()
    ├── update_emergency_status()
    └── add_emergency_update()
```

---

## Installation

### Step 1: Install Dependencies

```bash
# Install Firebase Admin SDK
pip install firebase-admin==6.5.0

# Or add to requirements.txt
echo "firebase-admin==6.5.0" >> requirements.txt
echo "google-cloud-firestore>=2.14.0" >> requirements.txt

pip install -r requirements.txt
```

### Step 2: Get Firebase Credentials

**Option A: Local Development (Recommended)**

1. [Firebase Console](https://console.firebase.google.com/) → Your Project
2. Project Settings → Service Accounts
3. "Generate New Private Key" → Download JSON
4. Rename to `firebase-key.json`
5. Place in project root

**Option B: Environment Variable**

```bash
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

**Option C: Google Application Credentials**

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-key.json
```

### Step 3: Create Firestore Database

1. Firebase Console → Build → Firestore Database
2. Click "Create Database"
3. Choose region
4. Start in **Production Mode** (security rules required)

### Step 4: Set Security Rules

Go to Firestore → Rules → Copy & paste:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    match /tickets/{ticketId} {
      allow read: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid != null;
    }
    match /food_orders/{orderId} {
      allow read, write: if request.auth.uid == resource.data.user_id;
    }
    match /emergencies/{emergencyId} {
      allow read, write: if true;  // Update for production
    }
  }
}
```

---

## Configuration

### Firebase Config Module (`app/config/firebase_config.py`)

Handles Firebase initialization with three credential methods:

```python
from app.config.firebase_config import (
    FirebaseConfig,
    get_firestore_client,
    Collections
)

# Automatic initialization
config = FirebaseConfig()  # Initialized on first access

# Get client
client = get_firestore_client()

# Use collection names as constants
from app.config.firebase_config import Collections
# Collections.USERS
# Collections.TICKETS
# Collections.FOOD_ORDERS
# Collections.EMERGENCIES
```

### Environment Setup

Create `.env` file (add to `.gitignore`):

```bash
# Option 1: Firebase key file path
GOOGLE_APPLICATION_CREDENTIALS=firebase-key.json

# Option 2: OR JSON string
FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Firestore settings
FIRESTORE_COLLECTION_LIMIT=100
FIRESTORE_BATCH_SIZE=500
```

---

## API Reference

### Generic Firestore Service

All methods are **async** and return appropriate types.

#### CREATE: `create_document()`

```python
from app.services.firebase_service import get_firestore_service

fs = get_firestore_service()

# Auto-generate document ID
doc_id = await fs.create_document(
    collection="users",
    data={
        "name": "John",
        "email": "john@example.com"
    }
)

# With custom document ID
doc_id = await fs.create_document(
    collection="users",
    document_id="user_123",
    data={"name": "John"}
)
```

#### READ: `get_document()` & `get_all_documents()`

```python
# Single document
user = await fs.get_document("users", "user_123")
# Returns: {"id": "user_123", "name": "John", ...}

# All documents (with limit)
users = await fs.get_all_documents("users", limit=100)
# Returns: List of document dicts
```

#### QUERY: `query_documents()`

```python
# Query by field
users = await fs.query_documents(
    collection="users",
    field="email",
    operator="==",
    value="john@example.com",
    limit=1
)

# Operators: '==', '<', '>', '<=', '>=', '!='
ticket_results = await fs.query_documents(
    collection="tickets",
    field="status",
    operator="==",
    value="CONFIRMED"
)
```

#### UPDATE: `update_document()` & `increment_field()`

```python
# Update document (merge with existing)
await fs.update_document(
    collection="users",
    document_id="user_123",
    data={"email": "newemail@example.com"},
    merge=True  # Keep other fields
)

# Increment counter
await fs.increment_field(
    collection="tickets",
    document_id="event_123",
    field="ticket_count",
    value=1
)

# Array operations
await fs.add_to_array(
    collection="emergencies",
    document_id="em_123",
    field="responders",
    value="STAFF_001"
)

await fs.remove_from_array(
    collection="emergencies",
    document_id="em_123",
    field="responders",
    value="STAFF_001"
)
```

#### DELETE: `delete_document()` & `delete_field()`

```python
# Delete entire document
await fs.delete_document("users", "user_123")

# Delete specific field
await fs.delete_field("users", "user_123", "temporary_field")
```

#### BATCH: `batch_create()` & `batch_update()`

```python
# Bulk create
doc_ids = await fs.batch_create(
    collection="users",
    documents=[
        ("user_1", {"name": "Alice"}),
        ("user_2", {"name": "Bob"}),
        (None, {"name": "Charlie"})  # Auto-ID
    ]
)

# Bulk update
await fs.batch_update(
    collection="tickets",
    updates={
        "ticket_1": {"status": "USED"},
        "ticket_2": {"status": "USED"},
        "ticket_3": {"status": "USED"}
    }
)
```

---

### Collection-Specific Services

#### User Service

```python
from app.services.firestore_collections_service import (
    get_firestore_user_service
)

user_service = get_firestore_user_service()

# Create user
doc_id = await user_service.create_user(user_obj)

# Get by ID
user = await user_service.get_user_by_id(user_id)

# Get by email
user = await user_service.get_user_by_email("john@example.com")

# Update
await user_service.update_user(user_id, {"phone": "1234567890"})

# List all
users = await user_service.get_all_users(limit=100)

# Deactivate
await user_service.deactivate_user(user_id)
```

#### Ticket Service

```python
from app.services.firestore_collections_service import (
    get_firestore_ticket_service
)

ticket_service = get_firestore_ticket_service()

# Create
doc_id = await ticket_service.create_ticket(ticket_obj)

# Get
ticket = await ticket_service.get_ticket_by_id(ticket_id)

# Get user's tickets
user_tickets = await ticket_service.get_tickets_by_user(user_id)

# Get event tickets
event_tickets = await ticket_service.get_tickets_by_event("EVT_001")

# Update status
await ticket_service.update_ticket_status(
    ticket_id,
    "USED",
    gate_assignment="Gate A"
)
```

#### Food Order Service

```python
from app.services.firestore_collections_service import (
    get_firestore_food_order_service
)

food_service = get_firestore_food_order_service()

# Create order
doc_id = await food_service.create_food_order(order_obj)

# Get order
order = await food_service.get_food_order_by_id(order_id)

# Get user's orders
user_orders = await food_service.get_orders_by_user(user_id)

# Get pending orders
pending = await food_service.get_pending_orders(limit=50)

# Get by status
ready_orders = await food_service.get_orders_by_status("READY")

# Update status
await food_service.update_order_status(
    order_id,
    "READY",
    booth_id="B1"
)
```

#### Emergency Service

```python
from app.services.firestore_collections_service import (
    get_firestore_emergency_service
)

emergency_service = get_firestore_emergency_service()

# Report emergency
doc_id = await emergency_service.create_emergency(
    emergency_id="EM_20260418_001",
    emergency_type="FIRE",
    location="North Gate",
    severity="HIGH",
    description="Fire detected",
    reported_by=user_id
)

# Get active emergencies
active = await emergency_service.get_active_emergencies()

# Get by severity
critical = await emergency_service.get_emergencies_by_severity("CRITICAL")

# Update status
await emergency_service.update_emergency_status(
    "EM_20260418_001",
    "RESOLVED",
    responded=True,
    response_time_minutes=5
)

# Add update
await emergency_service.add_emergency_update(
    "EM_20260418_001",
    "Fire brigade arrived",
    "STAFF_001"
)
```

---

## Usage Examples

### Example 1: User Registration with Firestore

```python
# routes/user_routes.py
from fastapi import APIRouter, HTTPException, status
from app.models.user import UserRegisterRequest
from app.services.firestore_collections_service import (
    get_firestore_user_service
)

router = APIRouter()
user_service = get_firestore_user_service()

@router.post("/register")
async def register_user(request: UserRegisterRequest):
    try:
        # Create user record
        user = User(
            user_id=uuid4(),
            name=request.name,
            email=request.email,
            phone=request.phone,
            password_hash=hash_password(request.password),
            created_at=datetime.now()
        )
        
        # Save to Firestore
        doc_id = await user_service.create_user(user)
        
        return {
            "success": True,
            "user_id": str(user.user_id),
            "message": "✅ User registered"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
```

### Example 2: Book Ticket and Get Route

```python
# routes/ticket_routes.py
from fastapi import APIRouter, HTTPException, status
from app.services.firestore_collections_service import (
    get_firestore_ticket_service
)

router = APIRouter()
ticket_service = get_firestore_ticket_service()

@router.post("/book")
async def book_ticket(request: TicketBookingRequest):
    '''Book ticket and save to Firestore'''
    try:
        ticket = Ticket(
            ticket_id=uuid4(),
            user_id=request.user_id,
            event_id=request.event_id,
            seat_zone=request.seat_zone,
            price=1000,
            status="CONFIRMED",
            created_at=datetime.now()
        )
        
        doc_id = await ticket_service.create_ticket(ticket)
        return {"success": True, "ticket_id": str(ticket.ticket_id)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_tickets(user_id: str):
    '''Retrieve user's tickets from Firestore'''
    try:
        tickets = await ticket_service.get_tickets_by_user(UUID(user_id))
        return {"tickets": tickets}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Example 3: Food Order Management

```python
# routes/food_routes.py
from fastapi import APIRouter
from app.services.firestore_collections_service import (
    get_firestore_food_order_service
)

router = APIRouter()
food_service = get_firestore_food_order_service()

@router.post("/order")
async def create_food_order(request: FoodOrderRequest):
    '''Create food order in Firestore'''
    order = FoodOrder(
        order_id=uuid4(),
        user_id=request.user_id,
        event_id=request.event_id,
        items=request.items,
        total_amount=calculate_total(request.items),
        status="PENDING",
        created_at=datetime.now()
    )
    
    doc_id = await food_service.create_food_order(order)
    return {"success": True, "order_id": str(order.order_id)}

@router.get("/pending")
async def get_pending_orders():
    '''List pending orders for kitchen staff'''
    pending = await food_service.get_pending_orders(limit=50)
    return {"pending_count": len(pending), "orders": pending}

@router.put("/{order_id}/ready")
async def mark_order_ready(order_id: str):
    '''Mark order as ready in Firestore'''
    await food_service.update_order_status(
        UUID(order_id),
        "READY"
    )
    return {"success": True}
```

### Example 4: Emergency Management

```python
# routes/emergency_routes.py
from fastapi import APIRouter
from app.services.firestore_collections_service import (
    get_firestore_emergency_service
)

router = APIRouter()
emergency_service = get_firestore_emergency_service()

@router.post("/report")
async def report_emergency(request: EmergencyReportRequest):
    '''Report emergency to Firestore'''
    doc_id = await emergency_service.create_emergency(
        emergency_id=f"EM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        emergency_type=request.type,
        location=request.location,
        severity=request.severity,
        description=request.description,
        reported_by=str(request.reported_by)
    )
    return {"success": True, "emergency_id": doc_id}

@router.get("/active")
async def get_active_emergencies():
    '''Retrieve active emergencies from Firestore'''
    emergencies = await emergency_service.get_active_emergencies()
    return {"count": len(emergencies), "emergencies": emergencies}

@router.put("/{emergency_id}/resolve")
async def resolve_emergency(emergency_id: str):
    '''Resolve emergency in Firestore'''
    await emergency_service.update_emergency_status(
        emergency_id,
        "RESOLVED",
        responded=True
    )
    return {"success": True}
```

---

## Migration Guide

### Step 1: Create Firestore Services

Files already created:
- ✅ `app/config/firebase_config.py` - Initialization
- ✅ `app/services/firebase_service.py` - Generic CRUD
- ✅ `app/services/firestore_collections_service.py` - Collection-specific

### Step 2: Update Existing Services

Convert sync methods to async:

**Before:**
```python
@staticmethod
def register_user(request):
    users_db[user_id] = user
    return user
```

**After:**
```python
async def register_user(self, request):
    await self.fs.create_user(user)
    return user
```

### Step 3: Update Routes to Async

**Before:**
```python
@router.post("/register")
def register_user(request):
    return UserService.register_user(request)
```

**After:**
```python
@router.post("/register")
async def register_user(request):
    return await user_service.register_user(request)
```

### Step 4: Remove In-Memory Dictionaries

Delete or comment out:
```python
# users_db: Dict[UUID, User] = {}
# tickets_db: Dict[UUID, Ticket] = {}
```

### Step 5: Test Each Service

```bash
python -m pytest tests/
```

---

## Testing

### Test Firebase Connection

```python
# test_firebase_connection.py

import asyncio
from app.config.firebase_config import FirebaseConfig, get_firestore_client
from app.services.firebase_service import get_firestore_service

async def test_firestore():
    # Initialize
    config = FirebaseConfig()
    print("✅ Firebase initialized")
    
    # Get client
    client = get_firestore_client()
    print("✅ Firestore client ready")
    
    # Get service
    fs = get_firestore_service()
    
    # Create test doc
    doc_id = await fs.create_document(
        "test_collection",
        data={"test": "data"}
    )
    print(f"✅ Created: {doc_id}")
    
    # Read test doc
    doc = await fs.get_document("test_collection", doc_id)
    print(f"✅ Retrieved: {doc}")
    
    # Clean up
    await fs.delete_document("test_collection", doc_id)
    print("✅ Test passed!")

asyncio.run(test_firestore())
```

### Run Tests

```bash
# Connection test
python test_firebase_connection.py

# Pytest tests
python -m pytest tests/ -v

# Specific test
python -m pytest tests/test_firestore_user_service.py
```

---

## Troubleshooting

### Issue: "Firebase credentials not found"

**Solution:** Check one of these is set:
```bash
# Option 1: File
ls firebase-key.json

# Option 2: Env var
echo $FIREBASE_CREDENTIALS_JSON | head -c 50

# Option 3: Path
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### Issue: "Collection not found"

**Solution:** Collections auto-create on first write. If needed, manually create in Firebase Console.

### Issue: "Permission denied" errors

**Solution:** Check Firestore security rules:
```javascript
// Allow development
allow read, write: if true;

// Or add yourself to admins
allow read, write: if request.auth.uid in get(/databases/$(database)/documents/admins/users).data.users;
```

### Issue: "Async context error"

**Solution:** Make sure routes are `async`:
```python
# ❌ Wrong
@router.get("/users")
def get_users():
    return await service.get_users()  # Error!

# ✅ Right
@router.get("/users")
async def get_users():
    return await service.get_users()
```

### Issue: Slow queries

**Solution:** Create indexes in Firebase Console:
1. See error message for index suggestion
2. Copy index definition
3. Create in Firestore → Indexes

---

## Performance Tips

- ✅ Use composite indexes for complex queries
- ✅ Batch operations (100 docs at a time)
- ✅ Cache frequently accessed data in memory
- ✅ Use limits to reduce document reads
- ✅ Monitor usage in Firebase Console

---

## Next Steps

1. ✅ Install firebase-admin
2. ✅ Get credentials
3. ✅ Create Firestore database
4. ✅ Test connection
5. ✅ Update first service
6. ✅ Update routes
7. ✅ Test end-to-end
8. ✅ Monitor in Firebase Console

---

**Status**: 🚀 Ready to deploy | All services integrated | Async-compatible

For questions, check [Firebase Documentation](https://firebase.google.com/docs/firestore) or see migration examples in `MIGRATION_EXAMPLES.py`.
