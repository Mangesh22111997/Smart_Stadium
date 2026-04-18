#!/usr/bin/env python3
"""
Login Test Script - Debug authentication issues
"""

import sys
from pathlib import Path
import hashlib
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.config.firebase_config import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("  LOGIN TEST - PASSWORD VERIFICATION")
print("="*70)

# Test credentials
test_accounts = [
    ("customer_demo", "Customer@2026"),
    ("admin_super", "AdminPass@2026"),
    ("security_gate1", "GateSecurity@2026"),
]

db = get_db_connection()

def test_login(username: str, password: str):
    """Test login for a user"""
    print(f"\n🔍 Testing: {username}")
    
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    print(f"   Input password: {password}")
    print(f"   Hashed as: {password_hash}")
    
    # Try to find in users
    print("\n   🔎 Searching in 'users'...")
    users = db.child("users").get()
    if users.val():
        for uid, user_data in users.val().items():
            if user_data.get('username') == username:
                stored_hash = user_data.get('password_hash', '')
                print(f"   ✅ Found user!")
                print(f"      - Username: {user_data.get('username')}")
                print(f"      - Email: {user_data.get('email')}")
                print(f"      - Active: {user_data.get('is_active')}")
                print(f"      - Stored hash: {stored_hash}")
                print(f"      - Input hash:  {password_hash}")
                
                if password_hash == stored_hash:
                    print(f"      ✅ PASSWORD MATCHES!")
                    return True
                else:
                    print(f"      ❌ PASSWORD MISMATCH")
                    return False
    
    # Try to find in admins
    print("\n   🔎 Searching in 'admins'...")
    admins = db.child("admins").get()
    if admins.val():
        for aid, admin_data in admins.val().items():
            if admin_data.get('username') == username:
                stored_hash = admin_data.get('password_hash', '')
                print(f"   ✅ Found admin!")
                print(f"      - Username: {admin_data.get('username')}")
                print(f"      - Admin Type: {admin_data.get('admin_type')}")
                print(f"      - Email: {admin_data.get('email')}")
                print(f"      - Active: {admin_data.get('is_active')}")
                print(f"      - Stored hash: {stored_hash}")
                print(f"      - Input hash:  {password_hash}")
                
                if password_hash == stored_hash:
                    print(f"      ✅ PASSWORD MATCHES!")
                    return True
                else:
                    print(f"      ❌ PASSWORD MISMATCH")
                    return False
    
    # Try to find in security staff
    print("\n   🔎 Searching in 'security_staff'...")
    staff = db.child("security_staff").get()
    if staff.val():
        for sid, staff_data in staff.val().items():
            if staff_data.get('username') == username:
                stored_hash = staff_data.get('password_hash', '')
                print(f"   ✅ Found security staff!")
                print(f"      - Username: {staff_data.get('username')}")
                print(f"      - Role: {staff_data.get('role')}")
                print(f"      - Email: {staff_data.get('email')}")
                print(f"      - Active: {staff_data.get('is_active')}")
                print(f"      - Stored hash: {stored_hash}")
                print(f"      - Input hash:  {password_hash}")
                
                if password_hash == stored_hash:
                    print(f"      ✅ PASSWORD MATCHES!")
                    return True
                else:
                    print(f"      ❌ PASSWORD MISMATCH")
                    return False
    
    print(f"   ❌ User not found in any collection")
    return False

# Run tests
print("\n" + "="*70)
print("  TESTING AUTHENTICATION")
print("="*70)

results = {}
for username, password in test_accounts:
    results[username] = test_login(username, password)

# Summary
print("\n" + "="*70)
print("  TEST SUMMARY")
print("="*70)
for username, success in results.items():
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {username}")
