# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Validation utilities for form inputs
"""

import re
from typing import Tuple

class InputValidator:
    """Handle form input validation"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            return False, "Email is required"
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, "✅ Valid email"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain a number"
        return True, "✅ Strong password"
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """Validate username"""
        if not username:
            return False, "Username is required"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, "✅ Valid username"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        if not phone:
            return False, "Phone number is required"
        if not re.match(r'^[0-9]{10}$', phone):
            return False, "Phone must be 10 digits"
        return True, "✅ Valid phone"
    
    @staticmethod
    def validate_booking_quantity(quantity: int, available: int) -> Tuple[bool, str]:
        """Validate ticket quantity"""
        if quantity < 1:
            return False, "Must book at least 1 ticket"
        if quantity > 10:
            return False, "Maximum 10 tickets per booking"
        if quantity > available:
            return False, f"Only {available} tickets available"
        return True, "✅ Valid quantity"
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Validate full name"""
        if not name:
            return False, "Name is required"
        if len(name) < 2:
            return False, "Name must be at least 2 characters"
        if len(name) > 50:
            return False, "Name must be at most 50 characters"
        return True, "✅ Valid name"
    
    @staticmethod
    def validate_not_empty(value: str, field_name: str) -> Tuple[bool, str]:
        """Generic non-empty validation"""
        if not value or value.strip() == "":
            return False, f"{field_name} is required"
        return True, f"✅ {field_name} provided"
    
    @staticmethod
    def validate_age(age: int) -> Tuple[bool, str]:
        """Validate age"""
        if age < 13:
            return False, "Must be at least 13 years old"
        if age > 130:
            return False, "Invalid age"
        return True, "✅ Valid age"


class FormFeedback:
    """Generate visual feedback for form validation"""
    
    @staticmethod
    def get_status_icon(is_valid: bool) -> str:
        """Get appropriate icon for validation status"""
        return "✅" if is_valid else "❌"
    
    @staticmethod
    def get_status_color(is_valid: bool) -> str:
        """Get appropriate color for validation status"""
        return "green" if is_valid else "red"
