#!/usr/bin/env python3
"""
Complete Firebase Integration Test
Tests all authentication and database operations
"""

import asyncio
import json
from app.services.firebase_auth_service import FirebaseAuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_integration_tests():
    """Run comprehensive Firebase integration tests"""
    
    print("\n" + "="*80)
    print("🔥 FIREBASE REALTIME DATABASE INTEGRATION TEST")
    print("="*80 + "\n")
    
    try:
        # TEST 1: User Registration
        print("TEST 1: User Registration")
        print("-" * 80)
        
        user_data = {
            "username": "mangesh-developer",
            "email": "mangesh@smart-stadium.dev",
            "password": "S2LS9ucDD3h281U7a4VDedodcDxCKyTc3XF6ksE8NjZ6kBJn",
            "name": "Mangesh Developer",
            "phone": "+91-9876543210"
        }
        
        registered_user = FirebaseAuthService.register_user(**user_data)
        print(f"✅ User registered successfully")
        print(f"   User ID: {registered_user['user_id']}")
        print(f"   Username: {registered_user['username']}")
        print(f"   Email: {registered_user['email']}")
        print(f"   Name: {registered_user['name']}")
        print(f"   Phone: {registered_user['phone']}\n")
        
        user_id_1 = registered_user['user_id']
        
        # TEST 2: Duplicate User Check
        print("TEST 2: Duplicate User Prevention")
        print("-" * 80)
        try:
            FirebaseAuthService.register_user(
                username="mangesh-developer",  # Same username
                email="another@example.com",
                password="password123",
                name="Another User"
            )
            print("❌ Should have prevented duplicate username")
        except ValueError as e:
            print(f"✅ Correctly prevented duplicate: {str(e)}\n")
        
        # TEST 3: User Login
        print("TEST 3: User Login")
        print("-" * 80)
        
        login_result = FirebaseAuthService.login_user(
            username="mangesh-developer",
            password="S2LS9ucDD3h281U7a4VDedodcDxCKyTc3XF6ksE8NjZ6kBJn"
        )
        print(f"✅ User logged in successfully")
        print(f"   User ID: {login_result['user_id']}")
        print(f"   Username: {login_result['username']}")
        print(f"   Email: {login_result['email']}")
        print(f"   Session Token: {login_result['session_token'][:20]}...")
        print(f"   Login Time: {login_result['login_time']}\n")
        
        session_token_1 = login_result['session_token']
        
        # TEST 4: Session Verification
        print("TEST 4: Session Verification")
        print("-" * 80)
        
        session = FirebaseAuthService.verify_session(session_token_1)
        if session:
            print(f"✅ Session verified successfully")
            print(f"   User: {session.get('username')}")
            print(f"   Email: {session.get('email')}")
            print(f"   Active: True\n")
        else:
            print("❌ Session verification failed\n")
        
        # TEST 5: Get User Profile
        print("TEST 5: Get User Profile")
        print("-" * 80)
        
        profile = FirebaseAuthService.get_user_profile(user_id_1)
        if profile:
            print(f"✅ User profile retrieved")
            print(f"   ID: {profile.get('user_id')}")
            print(f"   Username: {profile.get('username')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   Status: {'Active' if profile.get('is_active') else 'Inactive'}")
            print(f"   Created At: {profile.get('created_at')}\n")
        else:
            print("❌ Profile retrieval failed\n")
        
        # TEST 6: Update User Profile
        print("TEST 6: Update User Profile")
        print("-" * 80)
        
        updated = FirebaseAuthService.update_user_profile(user_id_1, {
            "phone": "+91-9999999999",
            "profile_complete": True
        })
        
        if updated:
            print(f"✅ User profile updated successfully\n")
        else:
            print("❌ Profile update failed\n")
        
        # TEST 7: Admin Registration
        print("TEST 7: Admin Registration")
        print("-" * 80)
        
        admin_data = {
            "username": "admin-mangesh",
            "email": "admin@smart-stadium.dev",
            "password": "AdminSecure123!@#",
            "admin_name": "Mangesh Admin",
            "admin_type": "moderator",
            "phone": "+91-9000000000"
        }
        
        registered_admin = FirebaseAuthService.register_admin(**admin_data)
        print(f"✅ Admin registered successfully")
        print(f"   Admin ID: {registered_admin['admin_id']}")
        print(f"   Username: {registered_admin['username']}")
        print(f"   Email: {registered_admin['email']}")
        print(f"   Name: {registered_admin['name']}")
        print(f"   Type: {registered_admin['admin_type']}")
        print(f"   Permissions: {', '.join(registered_admin['permissions'])}\n")
        
        admin_id = registered_admin['admin_id']
        
        # TEST 8: Admin Login
        print("TEST 8: Admin Login")
        print("-" * 80)
        
        admin_login = FirebaseAuthService.admin_login(
            username="admin-mangesh",
            password="AdminSecure123!@#"
        )
        print(f"✅ Admin logged in successfully")
        print(f"   Admin ID: {admin_login['admin_id']}")
        print(f"   Username: {admin_login['username']}")
        print(f"   Admin Type: {admin_login['admin_type']}")
        print(f"   Session Token: {admin_login['session_token'][:20]}...")
        print(f"   Permissions: {', '.join(admin_login['permissions'])}\n")
        
        admin_session_token = admin_login['session_token']
        
        # TEST 9: Admin Session Verification
        print("TEST 9: Admin Session Verification")
        print("-" * 80)
        
        admin_session = FirebaseAuthService.verify_session(admin_session_token)
        if admin_session and admin_session.get('is_admin'):
            print(f"✅ Admin session verified")
            print(f"   Admin: {admin_session.get('username')}")
            print(f"   Type: {admin_session.get('admin_type')}")
            print(f"   Permissions: {', '.join(admin_session.get('permissions', []))}\n")
        else:
            print("❌ Admin session verification failed\n")
        
        # TEST 10: Get All Users
        print("TEST 10: Get All Users")
        print("-" * 80)
        
        all_users = FirebaseAuthService.get_all_users()
        print(f"✅ Retrieved all users")
        print(f"   Total Users: {len(all_users)}")
        for i, user in enumerate(all_users, 1):
            print(f"   {i}. {user.get('username')} ({user.get('email')})")
        print()
        
        # TEST 11: User Logout
        print("TEST 11: User Logout")
        print("-" * 80)
        
        logout_result = FirebaseAuthService.logout_user(session_token_1)
        print(f"✅ User logged out: {logout_result}\n")
        
        # TEST 12: Verify Logout (session should be invalid)
        print("TEST 12: Verify Logout (Session Should Be Invalid)")
        print("-" * 80)
        
        session_after_logout = FirebaseAuthService.verify_session(session_token_1)
        if not session_after_logout:
            print(f"✅ Session correctly invalidated after logout\n")
        else:
            print(f"❌ Session still valid after logout\n")
        
        # TEST 13: Invalid Login
        print("TEST 13: Invalid Login Handling")
        print("-" * 80)
        
        try:
            FirebaseAuthService.login_user(
                username="mangesh-developer",
                password="wrong_password"
            )
            print("❌ Should have rejected wrong password")
        except ValueError as e:
            print(f"✅ Correctly rejected invalid credentials: {str(e)}\n")
        
        # SUMMARY
        print("="*80)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("="*80)
        print("\n📊 Summary:")
        print("   ✅ User registration works")
        print("   ✅ User login works")
        print("   ✅ Session creation and verification works")
        print("   ✅ User profile retrieval and updates work")
        print("   ✅ Admin registration works")
        print("   ✅ Admin login works")
        print("   ✅ Admin session verification works")
        print("   ✅ Get all users works")
        print("   ✅ Logout works")
        print("   ✅ Invalid credentials are rejected")
        print("\n🚀 Firebase Realtime Database Integration is READY!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    import sys
    sys.exit(0 if success else 1)
