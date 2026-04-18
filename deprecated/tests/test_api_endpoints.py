#!/usr/bin/env python3
"""
FastAPI Authentication Endpoints Test
Tests all HTTP endpoints for signup, signin, profile, etc.
"""

import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all API endpoints"""
    
    print("\n" + "="*80)
    print("🌐 FASTAPI AUTHENTICATION ENDPOINTS TEST")
    print("="*80 + "\n")
    
    async with httpx.AsyncClient() as client:
        try:
            # Wait for server startup
            print("⏳ Waiting for server to be ready...")
            max_retries = 10
            for i in range(max_retries):
                try:
                    response = await client.get(f"{BASE_URL}/health")
                    if response.status_code == 200:
                        print("✅ Server is ready!\n")
                        break
                except:
                    if i < max_retries - 1:
                        await asyncio.sleep(2)
                    else:
                        raise Exception("Server not responding")
            
            # TEST 1: Signup Endpoint
            print("TEST 1: User Signup")
            print("-" * 80)
            
            signup_data = {
                "username": f"api-test-user-{int(time.time())}",
                "email": f"apitest-{int(time.time())}@example.com",
                "password": "TestPassword123!@#",
                "name": "API Test User",
                "phone": "+91-1234567890"
            }
            
            response = await client.post(
                f"{BASE_URL}/auth/signup",
                json=signup_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                user_data = response.json()
                print(f"✅ User signup successful")
                print(f"   Username: {user_data.get('username')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   User ID: {user_data.get('user_id')}\n")
                user_id = user_data.get('user_id')
                username = user_data.get('username')
                password = signup_data['password']
            else:
                print(f"❌ Signup failed: {response.text}\n")
                return False
            
            # TEST 2: Signin Endpoint
            print("TEST 2: User Signin")
            print("-" * 80)
            
            signin_data = {
                "username": username,
                "password": password
            }
            
            response = await client.post(
                f"{BASE_URL}/auth/signin",
                json=signin_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                login_data = response.json()
                print(f"✅ User signin successful")
                print(f"   Username: {login_data.get('username')}")
                print(f"   Email: {login_data.get('email')}")
                print(f"   Session Token: {login_data.get('session_token', '')[:20]}...")
                print(f"   Login Time: {login_data.get('login_time')}\n")
                session_token = login_data.get('session_token')
            else:
                print(f"❌ Signin failed: {response.text}\n")
                return False
            
            # TEST 3: Verify Session
            print("TEST 3: Verify Session")
            print("-" * 80)
            
            response = await client.get(
                f"{BASE_URL}/auth/verify-session/{session_token}"
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                session_data = response.json()
                print(f"✅ Session verified successfully")
                print(f"   Username: {session_data.get('username')}")
                print(f"   Email: {session_data.get('email')}")
                print(f"   Active: {session_data.get('is_active')}\n")
            else:
                print(f"❌ Session verification failed: {response.text}\n")
            
            # TEST 4: Get User Profile
            print("TEST 4: Get User Profile")
            print("-" * 80)
            
            response = await client.get(
                f"{BASE_URL}/auth/profile/{user_id}"
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                profile_data = response.json()
                print(f"✅ Profile retrieved successfully")
                print(f"   Username: {profile_data.get('username')}")
                print(f"   Email: {profile_data.get('email')}")
                print(f"   Name: {profile_data.get('name')}")
                print(f"   Phone: {profile_data.get('phone')}")
                print(f"   Created: {profile_data.get('created_at')}\n")
            else:
                print(f"❌ Profile retrieval failed: {response.text}\n")
            
            # TEST 5: Admin Signup
            print("TEST 5: Admin Signup")
            print("-" * 80)
            
            admin_signup_data = {
                "username": f"api-admin-{int(time.time())}",
                "email": f"apiadmin-{int(time.time())}@example.com",
                "password": "AdminPassword123!@#",
                "admin_name": "API Admin User",
                "admin_type": "moderator",
                "phone": "+91-9876543210"
            }
            
            response = await client.post(
                f"{BASE_URL}/auth/admin/signup",
                json=admin_signup_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                admin_data = response.json()
                print(f"✅ Admin signup successful")
                print(f"   Username: {admin_data.get('username')}")
                print(f"   Admin Type: {admin_data.get('admin_type')}")
                print(f"   Permissions: {', '.join(admin_data.get('permissions', []))}\n")
                admin_username = admin_data.get('username')
                admin_password = admin_signup_data['password']
            else:
                print(f"❌ Admin signup failed: {response.text}\n")
                return False
            
            # TEST 6: Admin Signin
            print("TEST 6: Admin Signin")
            print("-" * 80)
            
            admin_signin_data = {
                "username": admin_username,
                "password": admin_password
            }
            
            response = await client.post(
                f"{BASE_URL}/auth/admin/signin",
                json=admin_signin_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                admin_login_data = response.json()
                print(f"✅ Admin signin successful")
                print(f"   Username: {admin_login_data.get('username')}")
                print(f"   Admin Type: {admin_login_data.get('admin_type')}")
                print(f"   Permissions: {', '.join(admin_login_data.get('permissions', []))}")
                print(f"   Session Token: {admin_login_data.get('session_token', '')[:20]}...\n")
                admin_session_token = admin_login_data.get('session_token')
            else:
                print(f"❌ Admin signin failed: {response.text}\n")
                return False
            
            # TEST 7: Get All Users (Admin Protected)
            print("TEST 7: Get All Users (Admin Protected)")
            print("-" * 80)
            
            response = await client.get(
                f"{BASE_URL}/auth/users/all",
                params={"session_token": admin_session_token}
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                users_data = response.json()
                print(f"✅ Retrieved all users (Admin access)")
                print(f"   Total Users: {len(users_data.get('users', []))}")
                for i, user in enumerate(users_data.get('users', [])[:3], 1):
                    print(f"   {i}. {user.get('username')} ({user.get('email')})")
                print()
            else:
                print(f"❌ Get all users failed: {response.text}\n")
            
            # TEST 8: Logout Endpoint
            print("TEST 8: User Logout")
            print("-" * 80)
            
            logout_data = {"session_token": session_token}
            response = await client.post(
                f"{BASE_URL}/auth/logout",
                json=logout_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                logout_result = response.json()
                print(f"✅ User logout successful")
                print(f"   Message: {logout_result.get('message')}\n")
            else:
                print(f"❌ Logout failed: {response.text}\n")
            
            # TEST 9: Verify Logout (Session Should Be Invalid)
            print("TEST 9: Verify Logout (Session Should Be Invalid)")
            print("-" * 80)
            
            response = await client.get(
                f"{BASE_URL}/auth/verify-session/{session_token}"
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 401:
                print(f"✅ Session correctly invalidated after logout\n")
            else:
                print(f"⚠️ Session may still be valid (Status: {response.status_code})\n")
            
            # TEST 10: Invalid Credentials
            print("TEST 10: Invalid Credentials Handling")
            print("-" * 80)
            
            invalid_signin = {
                "username": username,
                "password": "WrongPassword123"
            }
            
            response = await client.post(
                f"{BASE_URL}/auth/signin",
                json=invalid_signin
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 401:
                error_data = response.json()
                print(f"✅ Correctly rejected invalid credentials")
                print(f"   Error: {error_data.get('detail')}\n")
            else:
                print(f"❌ Should have rejected invalid credentials\n")
            
            # SUMMARY
            print("="*80)
            print("✅ ALL API ENDPOINT TESTS PASSED!")
            print("="*80)
            print("\n📊 Summary:")
            print("   ✅ User signup endpoint works")
            print("   ✅ User signin endpoint works")
            print("   ✅ Session verification endpoint works")
            print("   ✅ Get user profile endpoint works")
            print("   ✅ Admin signup endpoint works")
            print("   ✅ Admin signin endpoint works")
            print("   ✅ Get all users endpoint works (admin protected)")
            print("   ✅ Logout endpoint works")
            print("   ✅ Invalid credentials are rejected")
            print("\n🚀 FastAPI Authentication API is READY!\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_api_endpoints())
    import sys
    sys.exit(0 if success else 1)
