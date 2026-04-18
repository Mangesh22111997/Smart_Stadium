#!/usr/bin/env python3
"""
Firebase Realtime Database Test
Quick verification that pyrebase is working
"""

from app.config.firebase_config import get_db_connection
import json

def test_firebase_rtdb():
    """Test Firebase Realtime Database operations"""
    
    print("\n" + "="*80)
    print("🔥 FIREBASE REALTIME DATABASE TEST")
    print("="*80 + "\n")
    
    try:
        # Get database connection
        print("📌 Connecting to Firebase Realtime Database...")
        db = get_db_connection()
        print("✅ Connected successfully\n")
        
        # Test 1: Write data
        print("TEST 1: Writing data to 'test_data' path")
        print("-" * 80)
        test_data = {
            "message": "Firebase Realtime Database works!",
            "timestamp": "2026-04-18",
            "status": "connected"
        }
        
        db.child("test_data").set(test_data)
        print(f"✅ Data written: {json.dumps(test_data, indent=2)}\n")
        
        # Test 2: Read data
        print("TEST 2: Reading data from 'test_data' path")
        print("-" * 80)
        result = db.child("test_data").get()
        
        if result.val():
            data = result.val()
            print(f"✅ Data retrieved successfully:")
            print(f"   Message: {data.get('message')}")
            print(f"   Status: {data.get('status')}")
        else:
            print("❌ No data found")
            return False
        
        print("\n")
        
        # Test 3: Write to users path
        print("TEST 3: Writing user data to 'users' collection")
        print("-" * 80)
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        
        db.child("users").child("user_001").set(user_data)
        print(f"✅ User data written:\n{json.dumps(user_data, indent=2)}\n")
        
        # Test 4: Read user data
        print("TEST 4: Reading user data")
        print("-" * 80)
        user_result = db.child("users").child("user_001").get()
        
        if user_result.val():
            user = user_result.val()
            print(f"✅ User retrieved:")
            print(f"   Name: {user.get('name')}")
            print(f"   Email: {user.get('email')}")
        else:
            print("❌ User not found")
            return False
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\n📊 Summary:")
        print("   ✅ Firebase Realtime Database connected")
        print("   ✅ Data write operations working")
        print("   ✅ Data read operations working")
        print("   ✅ User collection operations working\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_firebase_rtdb()
    sys.exit(0 if success else 1)
