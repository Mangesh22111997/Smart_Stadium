#!/usr/bin/env python3
"""
API Endpoint Test - Test actual endpoints
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("  TESTING API ENDPOINTS")
print("="*70)

# Test 1: Customer Login
print("\n📱 Test 1: Cusomer Login (POST /auth/signin)")
try:
    response = requests.post(
        f"{API_BASE_URL}/auth/signin",
        json={
            "username": "customer_demo",
            "password": "Customer@2026"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response:")
    print(f"   {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n   ✅ CUSTOMER LOGIN SUCCESSFUL")
    else:
        print("\n   ❌ CUSTOMER LOGIN FAILED")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 2: Admin Login
print("\n\n👨‍💼 Test 2: Admin Login (POST /auth/admin/signin)")
try:
    response = requests.post(
        f"{API_BASE_URL}/auth/admin/signin",
        json={
            "username": "admin_super",
            "password": "AdminPass@2026"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response:")
    print(f"   {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n   ✅ ADMIN LOGIN SUCCESSFUL")
    else:
        print("\n   ❌ ADMIN LOGIN FAILED")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 3: Admin Login with wrong password
print("\n\n❌ Test 3: Admin Login with Wrong Password")
try:
    response = requests.post(
        f"{API_BASE_URL}/auth/admin/signin",
        json={
            "username": "admin_super",
            "password": "WrongPassword"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response:")
    print(f"   {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 4: Verify security staff in different collection
print("\n\n🔒 Test 4: Check if security staff use same endpoint (should fail)")
try:
    response = requests.post(
        f"{API_BASE_URL}/auth/admin/signin",
        json={
            "username": "security_gate1",
            "password": "GateSecurity@2026"
        },
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response:")
    print(f"   {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "="*70)
print("  API TEST COMPLETE")
print("="*70)
