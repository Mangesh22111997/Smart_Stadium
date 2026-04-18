#!/usr/bin/env python3
"""
Smart Stadium - Test User Seeding Script
Creates test admin, security staff, and customer accounts in Firebase
"""

import sys
import hashlib
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.firebase_config import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Create test users in Firebase"""
    
    db = get_db_connection()
    
    # Test Customer Accounts
    customers = [
        {
            "username": "customer_demo",
            "email": "customer@smartstadium.com",
            "password": "Customer@2026",
            "name": "Demo Customer",
            "phone": "+91-9876543210"
        },
        {
            "username": "demo_user",
            "email": "demo@smartstadium.com",
            "password": "DemoUser@2026",
            "name": "Test User",
            "phone": "+91-9876543211"
        }
    ]
    
    # Test Admin Accounts
    admins = [
        {
            "username": "admin_super",
            "email": "admin.super@smartstadium.com",
            "password": "AdminPass@2026",
            "name": "Super Admin",
            "admin_type": "superadmin",
            "permissions": {"all": True}
        },
        {
            "username": "admin_events",
            "email": "admin.events@smartstadium.com",
            "password": "EventsAdmin@2026",
            "name": "Events Manager",
            "admin_type": "admin",
            "permissions": {"events": True, "dashboard": True}
        },
        {
            "username": "admin_ops",
            "email": "admin.ops@smartstadium.com",
            "password": "OpsAdmin@2026",
            "name": "Operations Admin",
            "admin_type": "admin",
            "permissions": {"dashboard": True, "reports": True}
        }
    ]
    
    # Test Security Staff Accounts
    security_staff = [
        {
            "username": "security_gate1",
            "email": "security.gate1@smartstadium.com",
            "password": "GateSecurity@2026",
            "name": "Gate Operator 1",
            "role": "Entrance Gate Operator",
            "permissions": {"gate_control": True, "crowd_monitoring": True}
        },
        {
            "username": "security_flow",
            "email": "security.flow@smartstadium.com",
            "password": "FlowCoordinator@2026",
            "name": "Flow Coordinator",
            "role": "Flow Coordinator",
            "permissions": {"flow_management": True, "analytics": True}
        },
        {
            "username": "security_incident",
            "email": "security.incident@smartstadium.com",
            "password": "IncidentMgr@2026",
            "name": "Incident Manager",
            "role": "Incident Manager",
            "permissions": {"incident_logging": True, "alerts": True}
        },
        {
            "username": "security_emergency",
            "email": "security.emergency@smartstadium.com",
            "password": "Emergency@2026",
            "name": "Emergency Responder",
            "role": "Emergency Responder",
            "permissions": {"emergency_protocol": True, "evacuation": True}
        }
    ]
    
    created_count = 0
    
    # Clear existing test users (optional)
    print("\n🔄 Checking for existing test users...")
    
    try:
        # Create Customer Users
        print("\n👤 Creating Customer Accounts...")
        for customer in customers:
            try:
                # Check if user already exists
                users = db.child("users").get()
                user_exists = False
                if users.val():
                    for uid, user_data in users.val().items():
                        if user_data.get('username') == customer['username']:
                            user_exists = True
                            print(f"   ⚠️  {customer['username']} already exists (skipping)")
                            break
                
                if not user_exists:
                    user_data = {
                        "username": customer['username'],
                        "email": customer['email'],
                        "password_hash": hash_password(customer['password']),
                        "name": customer['name'],
                        "phone": customer['phone'],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "is_active": True,
                        "profile_complete": False,
                        "user_type": "customer"
                    }
                    
                    db.child("users").push(user_data)
                    print(f"   ✅ Created: {customer['username']}")
                    created_count += 1
            except Exception as e:
                print(f"   ❌ Error creating {customer['username']}: {str(e)}")
        
        # Create Admin Users
        print("\n👨‍💼 Creating Admin Accounts...")
        for admin in admins:
            try:
                # Check if admin already exists
                admins_db = db.child("admins").get()
                admin_exists = False
                if admins_db.val():
                    for aid, admin_data in admins_db.val().items():
                        if admin_data.get('username') == admin['username']:
                            admin_exists = True
                            print(f"   ⚠️  {admin['username']} already exists (skipping)")
                            break
                
                if not admin_exists:
                    admin_data = {
                        "username": admin['username'],
                        "email": admin['email'],
                        "password_hash": hash_password(admin['password']),
                        "name": admin['name'],
                        "admin_type": admin['admin_type'],
                        "permissions": admin['permissions'],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "is_active": True
                    }
                    
                    db.child("admins").push(admin_data)
                    print(f"   ✅ Created: {admin['username']} ({admin['admin_type']})")
                    created_count += 1
            except Exception as e:
                print(f"   ❌ Error creating {admin['username']}: {str(e)}")
        
        # Create Security Staff Accounts
        print("\n🔒 Creating Security Staff Accounts...")
        for staff in security_staff:
            try:
                # Check if staff already exists
                staff_db = db.child("security_staff").get()
                staff_exists = False
                if staff_db.val():
                    for sid, staff_data in staff_db.val().items():
                        if staff_data.get('username') == staff['username']:
                            staff_exists = True
                            print(f"   ⚠️  {staff['username']} already exists (skipping)")
                            break
                
                if not staff_exists:
                    staff_data = {
                        "username": staff['username'],
                        "email": staff['email'],
                        "password_hash": hash_password(staff['password']),
                        "name": staff['name'],
                        "role": staff['role'],
                        "permissions": staff['permissions'],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "is_active": True
                    }
                    
                    db.child("security_staff").push(staff_data)
                    print(f"   ✅ Created: {staff['username']} ({staff['role']})")
                    created_count += 1
            except Exception as e:
                print(f"   ❌ Error creating {staff['username']}: {str(e)}")
        
        print("\n" + "="*70)
        print(f"✅ Successfully created {created_count} test accounts!")
        print("="*70)
        
        print("\n📋 Test Credentials Summary:\n")
        
        print("🟢 CUSTOMER ACCOUNTS:")
        for customer in customers:
            print(f"   Username: {customer['username']}")
            print(f"   Password: {customer['password']}\n")
        
        print("🔵 ADMIN ACCOUNTS:")
        for admin in admins:
            print(f"   Username: {admin['username']}")
            print(f"   Password: {admin['password']}")
            print(f"   Type: {admin['admin_type']}\n")
        
        print("🟠 SECURITY STAFF ACCOUNTS:")
        for staff in security_staff:
            print(f"   Username: {staff['username']}")
            print(f"   Password: {staff['password']}")
            print(f"   Role: {staff['role']}\n")
        
        print("\n🎯 Ready to login! Access the app at http://localhost:8502")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  SMART STADIUM - TEST USER SEEDING")
    print("="*70)
    
    success = create_test_users()
    sys.exit(0 if success else 1)
