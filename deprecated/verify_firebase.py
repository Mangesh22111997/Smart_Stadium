#!/usr/bin/env python3
"""
Firebase Connection & Data Verification Script
Tests Firebase connection and verifies data operations
"""

import sys
from pathlib import Path
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("  FIREBASE CONNECTION & DATA VERIFICATION")
print("="*70)

# Step 1: Test Firebase connection
print("\n📡 Step 1: Testing Firebase Connection...")
try:
    from app.config.firebase_config import get_db_connection, initialize_firebase
    
    firebase = initialize_firebase()
    print("   ✅ Firebase initialized successfully")
    
    db = get_db_connection()
    print("   ✅ Database connection established")
    
except Exception as e:
    print(f"   ❌ Firebase connection failed: {str(e)}")
    sys.exit(1)

# Step 2: Check existing users
print("\n📊 Step 2: Checking Existing Users...")
try:
    users = db.child("users").get()
    
    if users.val():
        print(f"   ✅ Users found: {len(users.val())} users in database")
        for uid, user_data in users.val().items():
            username = user_data.get('username', 'N/A')
            email = user_data.get('email', 'N/A')
            is_active = user_data.get('is_active', False)
            status = "✅ Active" if is_active else "❌ Inactive"
            print(f"      - {username} ({email}) {status}")
    else:
        print("   ⚠️  No users found in database")
        
except Exception as e:
    print(f"   ❌ Error checking users: {str(e)}")

# Step 3: Check existing admins
print("\n👨‍💼 Step 3: Checking Existing Admins...")
try:
    admins = db.child("admins").get()
    
    if admins.val():
        print(f"   ✅ Admins found: {len(admins.val())} admins in database")
        for aid, admin_data in admins.val().items():
            username = admin_data.get('username', 'N/A')
            admin_type = admin_data.get('admin_type', 'N/A')
            print(f"      - {username} ({admin_type})")
    else:
        print("   ⚠️  No admins found in database")
        
except Exception as e:
    print(f"   ❌ Error checking admins: {str(e)}")

# Step 4: Check existing security staff
print("\n🔒 Step 4: Checking Existing Security Staff...")
try:
    staff = db.child("security_staff").get()
    
    if staff.val():
        print(f"   ✅ Security staff found: {len(staff.val())} staff in database")
        for sid, staff_data in staff.val().items():
            username = staff_data.get('username', 'N/A')
            role = staff_data.get('role', 'N/A')
            print(f"      - {username} ({role})")
    else:
        print("   ⚠️  No security staff found in database")
        
except Exception as e:
    print(f"   ❌ Error checking security staff: {str(e)}")

# Step 5: Test write operation
print("\n✍️  Step 5: Testing Write Operation...")
try:
    test_user = {
        "username": f"test_user_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@test.com",
        "password_hash": hashlib.sha256("test123".encode()).hexdigest(),
        "name": "Test User",
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "test": True
    }
    
    result = db.child("users").push(test_user)
    print(f"   ✅ Test user created with key: {result['name']}")
    
    # Try to read it back
    test_read = db.child("users").child(result['name']).get()
    if test_read.val():
        print(f"   ✅ Test user verified in database")
    else:
        print(f"   ⚠️  Test user not readable immediately")
        
except Exception as e:
    print(f"   ❌ Error during write test: {str(e)}")
    import traceback
    traceback.print_exc()

# Step 6: List all paths
print("\n📂 Step 6: Database Structure...")
try:
    root = db.get()
    if root.val():
        print("   ✅ Database contains:")
        for key in root.val().keys():
            path_data = db.child(key).get()
            if path_data.val():
                count = len(path_data.val()) if isinstance(path_data.val(), dict) else "N/A"
                print(f"      - {key}: {count} entries")
            else:
                print(f"      - {key}: (empty)")
    else:
        print("   ⚠️  Database is empty")
        
except Exception as e:
    print(f"   ❌ Error accessing database structure: {str(e)}")

print("\n" + "="*70)
print("  VERIFICATION COMPLETE")
print("="*70)
