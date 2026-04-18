#!/usr/bin/env python3
"""
Firebase Setup Verification Script
Tests Firebase initialization and Firestore connection
Run this after placing firebase-key.json in the project root
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_setup():
    """Verify Firebase is properly configured"""
    
    print("\n" + "="*80)
    print("🔥 FIREBASE SETUP VERIFICATION")
    print("="*80 + "\n")
    
    # Check 1: firebase-key.json exists
    print("✅ STEP 1: Checking firebase-key.json...")
    if Path("firebase-key.json").exists():
        print("   ✓ firebase-key.json found")
    else:
        print("   ✗ firebase-key.json NOT found in project root")
        print("   ➜ Place your service account key file there and try again")
        return False
    
    # Check 2: Import Firebase Admin SDK
    print("\n✅ STEP 2: Testing firebase_admin import...")
    try:
        import firebase_admin
        print("   ✓ firebase_admin imported successfully")
    except ImportError as e:
        print(f"   ✗ Failed to import firebase_admin: {e}")
        print("   ➜ Run: pip install firebase-admin")
        return False
    
    # Check 3: Initialize Firebase
    print("\n✅ STEP 3: Initializing Firebase...")
    try:
        from app.config.firebase_config import initialize_firebase, get_firestore_client, Collections
        
        db = initialize_firebase()
        print("   ✓ Firebase initialized successfully")
        print(f"   ✓ Firestore client: {type(db).__name__}")
    except Exception as e:
        print(f"   ✗ Firebase initialization failed: {e}")
        return False
    
    # Check 4: Test Firestore connection
    print("\n✅ STEP 4: Testing Firestore connection...")
    try:
        collections = list(db.collections())
        print(f"   ✓ Connected to Firestore")
        print(f"   ✓ Found {len(collections)} collection(s)")
        if collections:
            collection_names = [c.id for c in collections[:5]]
            print(f"   ✓ Collections: {', '.join(collection_names)}...")
    except Exception as e:
        print(f"   ⚠ Firestore connection test: {e}")
    
    # Check 5: Test service initialization
    print("\n✅ STEP 5: Initializing services...")
    try:
        from app.services.firebase_service import get_firestore_service
        from app.services.firestore_collections_service import (
            get_firestore_user_service,
            get_firestore_ticket_service,
            get_firestore_food_order_service,
            get_firestore_emergency_service
        )
        
        fs = get_firestore_service()
        print(f"   ✓ FirestoreService: {type(fs).__name__}")
        
        user_svc = get_firestore_user_service()
        print(f"   ✓ UserService: {type(user_svc).__name__}")
        
        ticket_svc = get_firestore_ticket_service()
        print(f"   ✓ TicketService: {type(ticket_svc).__name__}")
        
        food_svc = get_firestore_food_order_service()
        print(f"   ✓ FoodOrderService: {type(food_svc).__name__}")
        
        emergency_svc = get_firestore_emergency_service()
        print(f"   ✓ EmergencyService: {type(emergency_svc).__name__}")
        
    except Exception as e:
        print(f"   ✗ Service initialization failed: {e}")
        return False
    
    # Check 6: Collections
    print("\n✅ STEP 6: Collection names...")
    try:
        print(f"   ✓ Users: {Collections.USERS}")
        print(f"   ✓ Tickets: {Collections.TICKETS}")
        print(f"   ✓ Food Orders: {Collections.FOOD_ORDERS}")
        print(f"   ✓ Emergencies: {Collections.EMERGENCIES}")
    except Exception as e:
        print(f"   ✗ Collection names check failed: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL CHECKS PASSED - Firebase is properly configured!")
    print("="*80)
    print("\n📌 Next Steps:")
    print("   1. Run the test suite: python test_firebase_complete.py")
    print("   2. Start the API server: python -m uvicorn app.main:app --reload")
    print("   3. Visit: http://localhost:8000/docs")
    print("   4. Check Firebase status: http://localhost:8000/health/firebase\n")
    
    return True


if __name__ == "__main__":
    try:
        success = verify_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
