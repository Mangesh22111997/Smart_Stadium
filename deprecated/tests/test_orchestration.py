#!/usr/bin/env python3
"""
End-to-End Test Script for Smart Stadium Orchestration System
Tests all major orchestration workflows
"""

import requests
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Server URL
BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = f"{BASE_URL}/api/v1/orchestration"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    """Print a section title"""
    print(f"\n{BLUE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}\n")

def print_success(msg):
    """Print success message"""
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    """Print error message"""
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    """Print info message"""
    print(f"{YELLOW}ℹ {msg}{RESET}")

def test_health_check():
    """Test basic health check"""
    print_section("TEST 1: System Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_register_and_book():
    """Test user registration and ticket booking workflow"""
    print_section("TEST 2: User Registration & Ticket Booking Workflow")
    
    payload = {
        "email": f"user_{uuid4().hex[:8]}@example.com",
        "full_name": "Rahul Sharma",
        "phone": "+91-9876543210",
        "commute_mode": "CAR",
        "parking_required": True,
        "event_date": "2024-12-20",
        "arrival_time": "2024-12-20T14:30:00"
    }
    
    try:
        response = requests.post(
            f"{API_PREFIX}/user-journey/register-and-book",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("User registration & ticket booking successful")
            print_info(f"User ID: {data.get('user_id')}")
            print_info(f"Ticket ID: {data.get('ticket_id')}")
            print_info(f"Assigned Gate: {data.get('assigned_gate')}")
            print_info(f"Entry Time: {data.get('entry_time_minutes')} minutes")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Workflow Steps: {json.dumps(data.get('workflow_steps'), indent=2)}")
            return data.get('user_id'), data
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None, None

def test_get_user_journey(user_id):
    """Test getting user journey status"""
    print_section("TEST 3: Get User Journey Status")
    
    if not user_id:
        print_error("No valid user_id provided")
        return False
    
    try:
        response = requests.get(f"{API_PREFIX}/user-journey/{user_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("User journey retrieved successfully")
            print_info(f"User: {data.get('full_name')} ({data.get('email')})")
            print_info(f"Journey Status: {data.get('journey_status')}")
            print_info(f"Current Gate: {data.get('current_gate')}")
            print_info(f"Gate Utilization: {data.get('current_utilization')}")
            print_info(f"Entry Time Estimate: {data.get('entry_time_estimate')}")
            print_info(f"Events Count: {len(data.get('events', []))}")
            print_info(f"Active Emergencies: {data.get('active_emergencies')}")
            return True
        else:
            print_error(f"Get journey failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Get journey error: {str(e)}")
        return False

def test_redistribute_users():
    """Test user redistribution during overcrowding"""
    print_section("TEST 4: User Redistribution (Load Balancing)")
    
    payload = {
        "utilization_threshold": 75,
        "max_users_to_move": 50,
        "prefer_preferences": True
    }
    
    try:
        response = requests.post(
            f"{API_PREFIX}/redistribute-users",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("User redistribution orchestrated successfully")
            print_info(f"Reassignments Made: {data.get('reassignments_made')}")
            print_info(f"Users Affected: {data.get('users_affected')}")
            print_info(f"Notifications Sent: {data.get('notifications_sent')}")
            print_info(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Redistribution failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Redistribution error: {str(e)}")
        return False

def test_evacuation():
    """Test emergency evacuation workflow"""
    print_section("TEST 5: Emergency Evacuation Workflow")
    
    payload = {
        "location": "Gate-A",
        "emergency_type": "FIRE_ALARM",
        "target_gates": ["Gate-D", "Gate-E"]
    }
    
    try:
        response = requests.post(
            f"{API_PREFIX}/evacuation",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Evacuation orchestrated successfully")
            print_info(f"Users Evacuated: {data.get('users_evacuated')}")
            print_info(f"Evacuation ID: {data.get('evacuation_id')}")
            print_info(f"Emergency ID: {data.get('emergency_id')}")
            print_info(f"Notifications Sent: {data.get('notifications_sent')}")
            print_info(f"Status: {data.get('status')}")
            return True
        else:
            print_error(f"Evacuation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Evacuation error: {str(e)}")
        return False

def test_food_ordering(user_id):
    """Test food ordering workflow"""
    print_section("TEST 6: Food Ordering Workflow")
    
    if not user_id:
        print_error("No valid user_id provided")
        return False
    
    payload = {
        "items": [
            {"item_id": "item-1", "quantity": 2},
            {"item_id": "item-3", "quantity": 1}
        ]
    }
    
    try:
        response = requests.post(
            f"{API_PREFIX}/food-ordering/{user_id}",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Food order orchestrated successfully")
            print_info(f"Order ID: {data.get('order_id')}")
            print_info(f"Booth ID: {data.get('booth_id')}")
            print_info(f"Prep Time: {data.get('estimated_prep_time_minutes')} minutes")
            print_info(f"Booth Crowd Level: {data.get('booth_crowd_level')}")
            print_info(f"Status: {data.get('status')}")
            return True
        else:
            print_error(f"Food ordering failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Food ordering error: {str(e)}")
        return False

def test_emergency_sos(user_id):
    """Test emergency SOS response workflow"""
    print_section("TEST 7: Emergency SOS Response Workflow")
    
    if not user_id:
        print_error("No valid user_id provided")
        return False
    
    payload = {
        "emergency_type": "MEDICAL_EMERGENCY",
        "location": "Section-B2",
        "description": "User collapsed, requires immediate assistance"
    }
    
    try:
        response = requests.post(
            f"{API_PREFIX}/emergency-sos/{user_id}",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Emergency SOS orchestrated successfully")
            print_info(f"Emergency ID: {data.get('emergency_id')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Staff Assigned: {data.get('staff_assigned')}")
            print_info(f"Nearest Exit: {data.get('nearest_exit')}")
            print_info(f"Exit Distance: {data.get('exit_distance_meters')} meters")
            print_info(f"Affected Users: {data.get('affected_users_count')}")
            notifs = data.get('notifications_sent', {})
            print_info(f"Notifications - Critical: {notifs.get('critical_alerts', 0)}, Staff: {notifs.get('staff_alerts', 0)}")
            evacplan = data.get('evacuation_plan', {})
            print_info(f"Evacuation Plan - Primary Exit: {evacplan.get('primary_exit')}")
            return True
        else:
            print_error(f"Emergency SOS failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Emergency SOS error: {str(e)}")
        return False

def test_system_sync():
    """Test system synchronization"""
    print_section("TEST 8: System Synchronization")
    
    try:
        response = requests.post(f"{API_PREFIX}/sync-all-systems")
        
        if response.status_code == 200:
            data = response.json()
            print_success("System sync completed successfully")
            print_info(f"Sync Timestamp: {data.get('sync_timestamp')}")
            print_info(f"Modules Synced: {', '.join(data.get('modules_synced', []))}")
            print_info(f"Total Events Processed: {data.get('total_events_processed')}")
            return True
        else:
            print_error(f"System sync failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"System sync error: {str(e)}")
        return False

def test_system_health():
    """Test system health check"""
    print_section("TEST 9: System Health Status")
    
    try:
        response = requests.get(f"{API_PREFIX}/system-health")
        
        if response.status_code == 200:
            data = response.json()
            print_success("System health retrieved successfully")
            print_info(f"Overall Status: {data.get('overall_status')}")
            print_info(f"Timestamp: {data.get('timestamp')}")
            modules = data.get('modules', {})
            for module_name, module_data in modules.items():
                status = module_data.get('status', 'UNKNOWN')
                status_icon = f"{GREEN}✓{RESET}" if status == "HEALTHY" else f"{RED}✗{RESET}"
                print_info(f"  {status_icon} {module_name}: {status}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_event_log():
    """Test event log retrieval"""
    print_section("TEST 10: Event Log Retrieval")
    
    try:
        response = requests.get(
            f"{API_PREFIX}/event-log",
            params={"limit": 10, "skip": 0}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Event log retrieved successfully")
            print_info(f"Total Events: {data.get('total_events')}")
            events = data.get('events', [])
            print_info(f"Events in Response: {len(events)}")
            if events:
                for i, event in enumerate(events[:3], 1):
                    print_info(f"  Event {i}: {event.get('event_type')} - {event.get('status')}")
            return True
        else:
            print_error(f"Event log retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Event log error: {str(e)}")
        return False

def test_journey_analytics():
    """Test journey analytics"""
    print_section("TEST 11: Journey Analytics")
    
    try:
        response = requests.get(
            f"{API_PREFIX}/journey-analytics",
            params={"time_window": "24h"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Journey analytics retrieved successfully")
            print_info(f"Total Users Today: {data.get('total_users_today')}")
            print_info(f"Average Entry Time: {data.get('average_entry_time_minutes')} minutes")
            print_info(f"Users Reassigned: {data.get('users_reassigned')}")
            print_info(f"Reassignment Rate: {data.get('reassignment_rate_percent')}%")
            print_info(f"Average Satisfaction: {data.get('average_journey_satisfaction')}/5.0")
            print_info(f"Food Orders: {data.get('food_orders_placed')}")
            print_info(f"Emergencies Responded: {data.get('emergencies_responded')}")
            return True
        else:
            print_error(f"Analytics retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Analytics error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"\n{YELLOW}" + "="*70)
    print("  SMART STADIUM ORCHESTRATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70 + f"{RESET}\n")
    
    results = {
        "Health Check": False,
        "User Registration & Booking": False,
        "User Journey Status": False,
        "User Redistribution": False,
        "Emergency Evacuation": False,
        "Food Ordering": False,
        "Emergency SOS": False,
        "System Sync": False,
        "System Health": False,
        "Event Log": False,
        "Journey Analytics": False
    }
    
    # Run tests
    results["Health Check"] = test_health_check()
    
    user_id, booking_data = test_register_and_book()
    results["User Registration & Booking"] = booking_data is not None
    
    if user_id:
        results["User Journey Status"] = test_get_user_journey(user_id)
        results["Food Ordering"] = test_food_ordering(user_id)
        results["Emergency SOS"] = test_emergency_sos(user_id)
    
    results["User Redistribution"] = test_redistribute_users()
    results["Emergency Evacuation"] = test_evacuation()
    results["System Sync"] = test_system_sync()
    results["System Health"] = test_system_health()
    results["Event Log"] = test_event_log()
    results["Journey Analytics"] = test_journey_analytics()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"  [{status}] {test_name}")
    
    print(f"\n{BLUE}{'='*70}")
    percentage = (passed / total) * 100
    if percentage == 100:
        print(f"  {GREEN}ALL TESTS PASSED! ({passed}/{total}){RESET}")
    elif percentage >= 70:
        print(f"  {YELLOW}MOST TESTS PASSED ({passed}/{total} - {percentage:.0f}%){RESET}")
    else:
        print(f"  {RED}SOME TESTS FAILED ({passed}/{total} - {percentage:.0f}%){RESET}")
    print(f"{'='*70}{RESET}\n")

if __name__ == "__main__":
    main()
