"""
Authentication Utilities for Smart Stadium
Handles user registration, login, and admin authentication with JSON storage
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

# File paths
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"


def get_project_root():
    """Get the root directory of the project"""
    return Path(__file__).parent


def load_users():
    """Load users from JSON file"""
    try:
        file_path = get_project_root() / USERS_FILE
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('users', [])
    except Exception as e:
        print(f"Error loading users: {e}")
    return []


def save_users(users):
    """Save users to JSON file"""
    try:
        file_path = get_project_root() / USERS_FILE
        with open(file_path, 'w') as f:
            json.dump({'users': users}, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False


def load_admins():
    """Load admins from JSON file"""
    try:
        file_path = get_project_root() / ADMINS_FILE
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('admins', [])
    except Exception as e:
        print(f"Error loading admins: {e}")
    return []


def save_admins(admins):
    """Save admins to JSON file"""
    try:
        file_path = get_project_root() / ADMINS_FILE
        with open(file_path, 'w') as f:
            json.dump({'admins': admins}, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving admins: {e}")
        return False


def hash_password(password):
    """Hash password using SHA256 (for demo purposes)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password


def customer_signup(name, email, phone, password):
    """
    Register a new customer
    Returns: (success: bool, message: str)
    """
    # Validate input
    if not all([name, email, phone, password]):
        return False, "All fields are required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Load existing users
    users = load_users()
    
    # Check if email already exists
    if any(user['email'].lower() == email.lower() for user in users):
        return False, "Email already registered. Please sign in instead."
    
    # Create new user
    new_user = {
        "user_id": f"USER-{len(users) + 1:04d}",
        "name": name,
        "email": email,
        "phone": phone,
        "password": hash_password(password),  # Store hashed password
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # Add to users list
    users.append(new_user)
    
    # Save to file
    if save_users(users):
        return True, f"Account created successfully! Your User ID: {new_user['user_id']}"
    else:
        return False, "Error creating account. Please try again."


def customer_signin(email, password):
    """
    Authenticate a customer
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    # Validate input
    if not email or not password:
        return False, "Email and password are required", None
    
    # Load users
    users = load_users()
    
    # Find user by email
    user = None
    for u in users:
        if u['email'].lower() == email.lower():
            user = u
            break
    
    if not user:
        return False, "Invalid email or password", None
    
    # Verify password
    if not verify_password(password, user['password']):
        return False, "Invalid email or password", None
    
    # Return user data (without password)
    user_data = {
        'user_id': user['user_id'],
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'created_at': user['created_at']
    }
    
    return True, "Sign in successful!", user_data


def admin_signin(staff_id, password):
    """
    Authenticate an admin
    Returns: (success: bool, message: str, admin_data: dict or None)
    """
    # Validate input
    if not staff_id or not password:
        return False, "Staff ID and password are required", None
    
    # Load admins
    admins = load_admins()
    
    # Find admin by staff_id
    admin = None
    for a in admins:
        if a['staff_id'].lower() == staff_id.lower():
            admin = a
            break
    
    if not admin:
        return False, "Invalid staff ID or password", None
    
    # Verify password (plain text for demo, can be hashed later)
    if admin['password'] != password:
        return False, "Invalid staff ID or password", None
    
    # Return admin data (without password)
    admin_data = {
        'staff_id': admin['staff_id'],
        'name': admin['name'],
        'email': admin['email'],
        'created_at': admin['created_at']
    }
    
    return True, "Admin sign in successful!", admin_data


def add_admin(staff_id, password, name, email):
    """
    Add a new admin (for testing/setup)
    Returns: (success: bool, message: str)
    """
    admins = load_admins()
    
    # Check if staff_id already exists
    if any(a['staff_id'].lower() == staff_id.lower() for a in admins):
        return False, "Staff ID already exists"
    
    new_admin = {
        "staff_id": staff_id,
        "password": password,  # Store plaintext for demo
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat()
    }
    
    admins.append(new_admin)
    
    if save_admins(admins):
        return True, f"Admin {staff_id} created successfully"
    else:
        return False, "Error creating admin"


def get_user_by_id(user_id):
    """Get user details by user ID"""
    users = load_users()
    for user in users:
        if user['user_id'] == user_id:
            return {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'created_at': user['created_at']
            }
    return None


def get_all_users_count():
    """Get total number of registered users"""
    return len(load_users())


def get_all_admins_count():
    """Get total number of admins"""
    return len(load_admins())


# For testing/demo purposes
if __name__ == "__main__":
    # Test customer signup
    print("Testing Customer Signup...")
    success, msg = customer_signup("John Doe", "john@example.com", "9876543210", "password123")
    print(f"  {msg}")
    
    # Test customer signin
    print("\nTesting Customer Sign In...")
    success, msg, user = customer_signin("john@example.com", "password123")
    print(f"  {msg}")
    if success:
        print(f"  User: {user}")
    
    # Test admin signin
    print("\nTesting Admin Sign In...")
    success, msg, admin = admin_signin("STAFF-001", "staff123")
    print(f"  {msg}")
    if success:
        print(f"  Admin: {admin}")
    
    # Test invalid admin
    print("\nTesting Invalid Admin...")
    success, msg, admin = admin_signin("INVALID", "wrongpass")
    print(f"  {msg}")
