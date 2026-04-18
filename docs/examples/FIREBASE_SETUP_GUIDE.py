"""
Firebase Setup & Initialization Guide
Step-by-step instructions for Firebase integration
"""

# ============================================================================
# STEP 1: INSTALL FIREBASE ADMIN SDK
# ============================================================================

"""
Run in terminal:
    pip install firebase-admin

Add to requirements.txt:
    firebase-admin==6.5.0
    google-cloud-firestore>=2.14.0
"""

# ============================================================================
# STEP 2: GET FIREBASE CREDENTIALS
# ============================================================================

"""
1. Go to Firebase Console: https://console.firebase.google.com/

2. Create a new project or select existing:
   - Project name: "Smart Stadium"
   - Region: Choose closest to you

3. Go to Project Settings → Service Accounts

4. Click "Generate New Private Key"
   - Downloads JSON file with credentials

5. Rename downloaded file to: firebase-key.json
   - Place in project root: /g:/Mangesh/Hack2Skill_Google_Challenge_copilot/firebase-key.json

ALTERNATIVE: Use environment variable
    Set FIREBASE_CREDENTIALS_JSON to entire JSON content as string
    Or set GOOGLE_APPLICATION_CREDENTIALS to file path
"""

# ============================================================================
# STEP 3: FIREBASE CONFIGURATION FILE STRUCTURE
# ============================================================================

"""
firebase-key.json (keep this PRIVATE - add to .gitignore):
{
  "type": "service_account",
  "project_id": "smart-stadium-xxxxx",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "client_email": "firebase-adminsdk-xxxxx@smart-stadium-xxxxx.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
"""

# ============================================================================
# STEP 4: ENVIRONMENT SETUP
# ============================================================================

"""
Option A: Using .env file
    Create .env in project root:
    FIREBASE_CREDENTIALS_JSON='{\n...\n}'

Option B: Using environment variables in .gitignore
    Load in app/config/firebase_config.py (already handled)

Option C: Using CI/CD secrets
    GitHub Actions / Docker environments:
    - Set FIREBASE_CREDENTIALS_JSON in GitHub Secrets
    - Or mount firebase-key.json in Docker
"""

# ============================================================================
# STEP 5: FIRESTORE DATABASE SETUP
# ============================================================================

"""
In Firebase Console:

1. Go to Build → Firestore Database

2. Click "Create database"

3. Choose deployment settings:
   - Start in production mode
   - Location: Choose region

4. Security rules:
   Set to this initially (DEVELOPMENT ONLY):
   
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if true;
       }
     }
   }

5. For PRODUCTION, use these rules:
   
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       
       // Users collection
       match /users/{userId} {
         allow read, write: if request.auth.uid == userId || isAdmin();
       }
       
       // Tickets collection
       match /tickets/{ticketId} {
         allow read: if request.auth.uid == resource.data.user_id || isAdmin();
         allow create: if request.auth.uid != null;
         allow update, delete: if request.auth.uid == resource.data.user_id || isAdmin();
       }
       
       // Food orders collection
       match /food_orders/{orderId} {
         allow read, write: if request.auth.uid == resource.data.user_id || isAdmin();
         allow create: if request.auth.uid != null;
       }
       
       // Emergencies collection
       match /emergencies/{emergencyId} {
         allow read: if isAdmin() || isStaff();
         allow create: if request.auth.uid != null;
         allow update: if isAdmin() || isStaff();
       }
       
       // Helper function
       function isAdmin() {
         return get(/databases/$(database)/documents/admins/$(request.auth.uid)).data.role == 'admin';
       }
       
       function isStaff() {
         return get(/databases/$(database)/documents/staff/$(request.auth.uid)).data != null;
       }
     }
   }
"""

# ============================================================================
# STEP 6: CREATE COLLECTIONS IN FIRESTORE
# ============================================================================

"""
Collections are auto-created when you write first document, but you can manually:

Firebase Console → Firestore Database → Create Collection:

1. users
   - Document structure:
     {
       "user_id": "uuid-string",
       "name": "John Doe",
       "email": "john@example.com",
       "phone": "+1234567890",
       "password_hash": "sha256hash",
       "commute_preference": "metro",
       "departure_preference": "early",
       "created_at": timestamp,
       "updated_at": timestamp,
       "is_active": true
     }

2. tickets
   - Document structure:
     {
       "ticket_id": "uuid-string",
       "user_id": "uuid-string",
       "event_id": "EVT_001",
       "seat_zone": "A",
       "seat_row": 10,
       "seat_number": 5,
       "price": 1000,
       "status": "CONFIRMED",
       "gate_assignment": "Gate A",
       "created_at": timestamp,
       "updated_at": timestamp
     }

3. food_orders
   - Document structure:
     {
       "order_id": "uuid-string",
       "user_id": "uuid-string",
       "event_id": "EVT_001",
       "items": ["pizza", "coke"],
       "booth_id": "B1",
       "total_amount": 500,
       "status": "PENDING",
       "created_at": timestamp,
       "updated_at": timestamp,
       "estimated_ready_time": timestamp
     }

4. emergencies
   - Document structure:
     {
       "emergency_id": "EM_001_20260418",
       "type": "FIRE",
       "location": "North Gate",
       "severity": "HIGH",
       "description": "Fire detected near entrance",
       "reported_by": "uuid-string",
       "status": "ACTIVE",
       "created_at": timestamp,
       "updated_at": timestamp,
       "responded": false,
       "response_time_minutes": null,
       "updates": [
         {
           "message": "Fire brigade called",
           "updated_by": "STAFF_001",
           "timestamp": timestamp
         }
       ]
     }
"""

# ============================================================================
# STEP 7: PYTHON INITIALIZATION
# ============================================================================

"""
In your main app startup (app/main.py):

from app.config.firebase_config import FirebaseConfig, get_firestore_client

# This runs on app startup:
@app.on_event("startup")
async def startup_event():
    # Initialize Firebase
    config = FirebaseConfig()
    print("✅ Firebase initialized with Firestore")
    
    # Verify connection
    client = get_firestore_client()
    print(f"✅ Firestore client connected")

# And on shutdown:
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Closing Firestore connection")
    # Firebase admin SDK handles cleanup automatically
"""

# ============================================================================
# STEP 8: ADD REQUIREMENTS
# ============================================================================

"""
requirements.txt should include:

firebase-admin==6.5.0
google-cloud-firestore>=2.14.0
python-dotenv>=1.0.0

Run:
    pip install -r requirements.txt
"""

# ============================================================================
# STEP 9: UPDATE .gitignore
# ============================================================================

"""
Add to .gitignore:

# Firebase credentials
firebase-key.json
.env
.env.local

# IDE
.vscode/
.idea/

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
"""

# ============================================================================
# STEP 10: VERIFY INSTALLATION
# ============================================================================

"""
Create test script (test_firebase_connection.py):

import asyncio
from app.config.firebase_config import FirebaseConfig, get_firestore_client
from app.services.firebase_service import get_firestore_service

async def test_connection():
    # Test 1: Firebase initialization
    try:
        config = FirebaseConfig()
        print("✅ Firebase Config initialized")
    except Exception as e:
        print(f"❌ Firebase Config failed: {e}")
        return
    
    # Test 2: Firestore client
    try:
        client = get_firestore_client()
        print("✅ Firestore client connected")
    except Exception as e:
        print(f"❌ Firestore client failed: {e}")
        return
    
    # Test 3: Create test document
    try:
        fs = get_firestore_service()
        doc_id = await fs.create_document(
            "test_collection",
            data={"test": "data", "timestamp": "test"}
        )
        print(f"✅ Test document created: {doc_id}")
    except Exception as e:
        print(f"❌ Document creation failed: {e}")
        return
    
    # Test 4: Read test document
    try:
        doc = await fs.get_document("test_collection", doc_id)
        print(f"✅ Test document retrieved: {doc}")
    except Exception as e:
        print(f"❌ Document retrieval failed: {e}")
        return
    
    # Test 5: Clean up
    try:
        await fs.delete_document("test_collection", doc_id)
        print(f"✅ Test document deleted")
    except Exception as e:
        print(f"❌ Document deletion failed: {e}")
        return

# Run test
if __name__ == "__main__":
    asyncio.run(test_connection())

Run:
    python test_firebase_connection.py
"""

# ============================================================================
# STEP 11: MIGRATION FROM IN-MEMORY TO FIRESTORE
# ============================================================================

"""
Update services to use Firestore instead of in-memory dicts:

BEFORE (In-memory):
    users_db: Dict[UUID, User] = {}
    
    @staticmethod
    def register_user(request):
        user = User(...)
        users_db[user.user_id] = user
        return user

AFTER (Firestore):
    fs = get_firestore_user_service()
    
    @staticmethod
    async def register_user(request):
        user = User(...)
        doc_id = await fs.create_user(user)
        return user

All route handlers need to be async:
    
    BEFORE:
        @router.post("/users/register")
        def register_user(request: UserRegisterRequest):
            return UserService.register_user(request)
    
    AFTER:
        @router.post("/users/register")
        async def register_user(request: UserRegisterRequest):
            return await fs.create_user(request)
"""

# ============================================================================
# STEP 12: ERROR HANDLING & LOGGING
# ============================================================================

"""
Firestore errors are already logged in firebase_service.py

To add custom error handling in routes:

from fastapi import HTTPException, status

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user_service = get_firestore_user_service()
        user = await user_service.get_user_by_id(UUID(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        return user
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user ID format: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
"""

# ============================================================================
# STEP 13: PERFORMANCE CONSIDERATIONS
# ============================================================================

"""
Index Creation (for better query performance):

In Firebase Console → Firestore Database → Indexes:

1. Collection: tickets
   - Field: user_id (Ascending)
   - Field: status (Ascending)
   - Reason: Query by user_id and status

2. Collection: food_orders
   - Field: status (Ascending)
   - Field: created_at (Descending)
   - Reason: Find pending orders sorted by time

3. Collection: emergencies
   - Field: severity (Ascending)
   - Field: status (Ascending)
   - Reason: Find high-severity active emergencies

Firestore also provides:
- Composite indexes (automatic for complex queries)
- TTL policies (delete old data automatically)
"""

# ============================================================================
# STEP 14: MONITORING & COSTS
# ============================================================================

"""
Firebase provides free tier:
- 50,000 read/write operations per day
- 1GB storage
- Perfect for development

Pricing:
- $0.06 per 100,000 read operations
- $0.18 per 100,000 write operations
- $0.18 per 100,000 delete operations

Monitor in Firebase Console:
- Firestore Database → Usage
- Check reads/writes per collection
- Set up billing alerts

For production optimization:
- Use composite queries efficiently
- Batch operations where possible
- Add appropriate indexes
- Cache frequently accessed data in memory
"""

print("✅ Firebase setup guide loaded successfully")
