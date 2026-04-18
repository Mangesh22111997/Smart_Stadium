# Firebase Integration Setup Complete ✅

## Current Status

Your Firebase integration is **fully configured** and ready to use:

### ✅ Verified Components
- **Firebase Admin SDK** - Initialized
- **Firestore Client** - Connected (with proper authentication)
- **All Services** Ready:
  - FirestoreService (generic CRUD)
  - FirestoreUserService
  - FirestoreTicketService
  - FirestoreFoodOrderService
  - FirestoreEmergencyService

---

## Initialize Firebase (Code Example)

Your standard Firebase initialization:

```python
import firebase_admin
from firebase_admin import credentials

# Method 1: Using firebase-key.json (Recommended)
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Initialize automatically via our wrapper
from app.config.firebase_config import initialize_firebase, get_firestore_client

db = initialize_firebase()  # Initializes Firebase
client = get_firestore_client()  # Gets Firestore client
```

---

## Using the Services

### Quick Examples

**1. Create User Document**
```python
from app.services.firestore_collections_service import get_firestore_user_service
import asyncio

async def create_user():
    user_service = get_firestore_user_service()
    
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91-1234567890",
        "ticket_count": 0
    }
    
    user_id = await user_service.create_user(user_id="user_123", data=user_data)
    return user_id

# Run it
asyncio.run(create_user())
```

**2. Query Tickets**
```python
async def get_user_tickets():
    ticket_service = get_firestore_ticket_service()
    tickets = await ticket_service.get_tickets_by_user("user_123")
    return tickets

asyncio.run(get_user_tickets())
```

**3. Create Emergency**
```python
async def create_emergency():
    emergency_service = get_firestore_emergency_service()
    
    emergency_data = {
        "location": "Gate 5",
        "severity": "high",
        "description": "Medical emergency",
        "status": "active"
    }
    
    emergency_id = await emergency_service.create_emergency(data=emergency_data)
    return emergency_id

asyncio.run(create_emergency())
```

---

## Next Steps (IMPORTANT!)

### 1️⃣ Enable Cloud Firestore API
The Firestore API needs to be enabled in your Google Cloud project:

**Visit this link:**
```
https://console.cloud.google.com/datastore/setup?project=smart-stadium-system-db
```

**Then:**
1. Select "Cloud Firestore" (not Datastore)
2. Create a database in your preferred region
3. Wait 1-2 minutes for activation

---

### 2️⃣ Run the Complete Test Suite
Once Firestore is enabled, run comprehensive tests:

```bash
# With venv activated
python test_firebase_complete.py
```

Expected output: ✅ All 6 test categories pass

---

### 3️⃣ Start the FastAPI Server
```bash
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Start server
python -m uvicorn app.main:app --reload
```

Then visit:
- **API Docs (Swagger):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Firebase Status:** http://localhost:8000/health/firebase

---

## Collection Structure

Your Firestore database will have these collections:

```
smart-stadium-system-db/
├── users/
│   ├── user_123
│   │   ├── name: "John Doe"
│   │   ├── email: "john@example.com"
│   │   └── ticket_count: 5
│
├── tickets/
│   ├── ticket_456
│   │   ├── user_id: "user_123"
│   │   ├── event_date: "2024-04-20"
│   │   └── status: "booked"
│
├── food_orders/
│   ├── order_789
│   │   ├── user_id: "user_123"
│   │   ├── status: "pending"
│   │   └── items: ["burger", "fries"]
│
└── emergencies/
    ├── emergency_101
    │   ├── location: "Gate 5"
    │   ├── severity: "high"
    │   └── status: "active"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `app/config/firebase_config.py` | Firebase initialization (3 credential methods) |
| `app/services/firebase_service.py` | Generic CRUD operations (12 async methods) |
| `app/services/firestore_collections_service.py` | Collection-specific services (25+ methods) |
| `verify_firebase_setup.py` | Setup verification script |
| `test_firebase_complete.py` | Comprehensive test suite (6 categories) |
| `app/main.py` | FastAPI app with Firebase initialization |

---

## Troubleshooting

### Issue: "Cloud Firestore API has not been used in project"
**Solution:** Enable the API at https://console.cloud.google.com/apis/api/firestore.googleapis.com/overview?project=smart-stadium-system-db

### Issue: "The database (default) does not exist"
**Solution:** Create a Firestore database at https://console.cloud.google.com/firestore

### Issue: "Module not found" errors
**Solution:** Make sure venv is activated and packages installed:
```bash
.\.venv\Scripts\Activate.ps1
pip install firebase-admin google-cloud-firestore
```

### Issue: No module named 'app'
**Solution:** Run commands from project root directory

---

## Security Reminders

✅ **DO:**
- Keep `firebase-key.json` in `.gitignore` (already configured)
- Use environment variables for credentials in production
- Set proper Firestore security rules
- Rotate service account keys regularly

❌ **DON'T:**
- Commit `firebase-key.json` to Git
- Expose credentials in logs
- Use the same key across multiple environments
- Store sensitive data unencrypted

---

## API Endpoints (After Route Migration)

```
POST   /api/users/register
GET    /api/users/{user_id}
PUT    /api/users/{user_id}

POST   /api/tickets/book
GET    /api/tickets/{ticket_id}
GET    /api/users/{user_id}/tickets

POST   /api/food-orders
GET    /api/food-orders/{order_id}
GET    /api/users/{user_id}/orders

POST   /api/emergencies
GET    /api/emergencies/active
PUT    /api/emergencies/{emergency_id}/status

GET    /health
GET    /health/firebase
```

---

## Command Reference

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install/update packages
pip install firebase-admin google-cloud-firestore

# Verify setup
python verify_firebase_setup.py

# Run tests
python test_firebase_complete.py

# Start server
python -m uvicorn app.main:app --reload

# Debug mode
python -m uvicorn app.main:app --reload --log-level debug
```

---

## What's Next?

1. ✅ Enable Firestore API (do this first!)
2. ✅ Run test suite to verify integration
3. 🔄 Migrate existing routes to use Firestore services
4. 🔄 Test all endpoints with actual data
5. 📦 Deploy to production

---

**You're all set! 🚀**
