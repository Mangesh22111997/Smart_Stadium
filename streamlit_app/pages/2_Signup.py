"""
Signup Page - New Customer Account Creation
"""

import streamlit as st
from utils.session_manager import SessionManager
from utils.api_client import get_api_client
from utils.validators import InputValidator
from utils.ui_helper import add_background_image
import time

st.set_page_config(page_title="Signup - Smart Stadium", page_icon="📋", layout="centered")

# Apply Background
add_background_image()

# Check if already logged in
if SessionManager.is_logged_in():
    st.success("✅ You're already logged in!")
    st.switch_page("pages/01_home.py")
    st.stop()

st.markdown("# 📋 Create Your Account")
st.markdown("*Join Smart Stadium and start booking events*")
st.divider()

api_client = get_api_client()

# Signup form
with st.form("signup_form"):
    st.markdown("## Basic Information")
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input(
            "First Name *",
            placeholder="John",
            key="first_name"
        )
    with col2:
        last_name = st.text_input(
            "Last Name *",
            placeholder="Doe",
            key="last_name"
        )
    
    full_name = f"{first_name} {last_name}".strip()
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input(
            "Email Address *",
            placeholder="john@example.com",
            key="email"
        )
    with col2:
        phone = st.text_input(
            "Phone Number",
            placeholder="+91 98765 43210",
            key="phone"
        )
    
    date_of_birth = st.date_input(
        "Date of Birth",
        key="dob"
    )
    
    st.markdown("## Account Credentials")
    
    username = st.text_input(
        "Username *",
        placeholder="john_doe",
        help="Unique username for login (minimum 3 characters)",
        key="username"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input(
            "Password *",
            type="password",
            placeholder="Enter a strong password",
            help="Minimum 6 characters",
            key="password"
        )
    with col2:
        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Re-enter password",
            key="confirm_password"
        )
    
    st.markdown("## Additional Information")
    
    occupation = st.selectbox(
        "Occupation",
        ["Select...", "Student", "Business", "Service", "Other"],
        key="occupation"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City", placeholder="Mumbai", key="city")
    with col2:
        state = st.text_input("State", placeholder="Maharashtra", key="state")
    
    address = st.text_area("Address", placeholder="Enter your full address", key="address")
    
    # Date of Birth with extended year range
    from datetime import date
    dob_val = st.date_input(
        "Date of Birth",
        value=date(2000, 1, 1),
        min_value=date(1947, 1, 1),
        max_value=date.today(),
        key="dob_picker"
    )
    
    hobbies_options = ["Sports", "Music", "Movies", "Gaming", "Reading", "Travel", "Art", "Cooking"]
    hobbies = st.multiselect(
        "Hobbies (Optional - Select up to 3)",
        hobbies_options,
        max_selections=3,
        key="hobbies"
    )
    
    # Terms and conditions with link
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("I agree to the [Terms & Conditions](./0_Terms_and_Conditions) and Privacy Policy")
    with col2:
        if st.button("📜 View Terms", key="view_terms"):
            st.switch_page("pages/0_Terms_and_Conditions.py")
    
    agree_terms = st.checkbox(
        "I confirm my agreement to the above terms",
        key="agree_terms"
    )
    
    st.divider()
    
    # Submit button
    col1, col2, col3 = st.columns(3)
    with col1:
        submit_btn = st.form_submit_button("✅ Create Account", use_container_width=True)
    with col2:
        st.form_submit_button("❌ Cancel", use_container_width=True)
    with col3:
        pass
    
    if submit_btn:
        # Validation using validators module
        errors = []
        
        # Username validation
        is_valid, msg = InputValidator.validate_username(username)
        if not is_valid:
            errors.append(msg)
        
        # Email validation  
        is_valid, msg = InputValidator.validate_email(email)
        if not is_valid:
            errors.append(msg)
        
        # Password validation
        is_valid, msg = InputValidator.validate_password(password)
        if not is_valid:
            errors.append(msg)
        
        # Confirm password match
        if password != confirm_password:
            errors.append("❌ Passwords do not match")
        
        # Full name validation
        is_valid, msg = InputValidator.validate_name(full_name)
        if not is_valid:
            errors.append(msg)
        
        # Phone validation (if provided)
        if phone:
            is_valid, msg = InputValidator.validate_phone(phone)
            if not is_valid:
                errors.append(msg)
        
        # Terms agreement
        if not agree_terms:
            errors.append("❌ You must agree to Terms & Conditions")
        
        if errors:
            st.error("❌ Please fix the following errors:")
            for error in errors:
                st.write(f"• {error}")
        else:
            # Call API to create account
            with st.spinner("📝 Creating your account..."):
                # Prepare profile data
                profile_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "phone": phone if phone else None,
                    "name": full_name
                }
                
                result = api_client.signup(**profile_data)
            
            if "user_id" in result:
                # Signup successful
                st.success("✅ Account created successfully!")
                st.info(f"Welcome, {full_name}! Please log in to continue.")
                
                # Store the additional info in session for now
                st.session_state["signup_complete"] = True
                st.session_state["new_user_id"] = result.get("user_id")
                
                time.sleep(2)
                st.switch_page("pages/1_Login.py")
            else:
                st.error(f"❌ Signup failed: {result.get('detail', 'Unknown error')}")

st.divider()
st.markdown("### Already have an account?")
if st.button("🔐 Login Here", use_container_width=True):
    st.switch_page("pages/1_Login.py")
