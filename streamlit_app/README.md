"""
🚀 STREAMLIT PORTAL STARTUP GUIDE
====================================

Smart Stadium System - Complete Multi-Portal Application
Includes: Customer Portal, Admin Portal, Security Portal (coming soon)

PREREQUISITES
=============
1. FastAPI Backend running on http://localhost:8000
2. Firebase Realtime Database configured and accessible
3. Python 3.8+ installed
4. Virtual environment activated

QUICK START (Windows PowerShell)
================================

Step 1: Create/Activate Virtual Environment (if not done)
---------------------------------------------------------
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

Step 2: Install Streamlit Dependencies
--------------------------------------
cd streamlit_app
pip install -r requirements.txt

Step 3: Start FastAPI Backend (in separate terminal)
--------------------------------------------------
# From root directory
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Firebase Realtime Database connected

Step 4: Start Streamlit Application
----------------------------------
# From streamlit_app directory
streamlit run app.py

# Expected output:
# You can now view your Streamlit app in your browser
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501

PORTAL FEATURES
===============

🔐 AUTHENTICATION
-----------------
✅ Customer Signup - Full profile capture
✅ Customer Login - Email/Username + Password
✅ Admin Signup - Role-based admin creation
✅ Admin Login - Admin-specific authentication
✅ Session Management - Secure session tokens
✅ Logout - Graceful session termination

👤 CUSTOMER PORTAL (/)
---------------------
✅ Home Dashboard - Quick links & stats
✅ Event Discovery - Browse & search events
✅ Ticket Booking - Select and book tickets
✅ Stadium Maps - (Integration ready)
✅ Food Ordering - (Integration ready)
✅ Notifications - Alert center
✅ User Profile - Account management

📊 ADMIN PORTAL (/admin)
-----------------------
✅ Dashboard - Key metrics & analytics
✅ Event Management - Create & manage events
✅ User Management - View all users
✅ Gate Management - Status & congestion control
✅ Crowd Analytics - Real-time visualization
✅ Admin Settings - Account & permissions

🔐 SECURITY PORTAL (/security)
------------------------------
🔜 Development in progress
   - Live monitoring
   - Emergency response
   - Security alerts

API INTEGRATION
===============

Backend URL: http://localhost:8000
All API calls go through:
  - api_client.py (HTTP requests)
  - session_manager.py (State management)

Key Endpoints Used:
  POST /auth/signup - Customer registration
  POST /auth/signin - Customer login
  POST /auth/logout - Logout
  POST /auth/admin/signup - Admin registration
  POST /auth/admin/signin - Admin login
  GET /auth/users/all - Fetch all users
  GET /health/firebase - Backend status check

PROJECT STRUCTURE
=================

streamlit_app/
├── app.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── api_client.py          # FastAPI communication
│   └── session_manager.py     # Session state management
├── pages/
│   ├── 1_Login.py             # Customer & Admin login
│   ├── 2_Signup.py            # Customer registration
│   ├── 3_Home.py              # Customer home dashboard
│   ├── 4_Events.py            # Event discovery
│   ├── 5_Bookings.py          # Ticket booking
│   ├── 6_Maps.py              # Stadium navigation (ready)
│   ├── 7_Food.py              # Food ordering (ready)
│   ├── 8_Notifications.py     # Alert center
│   ├── 9_Admin_Dashboard.py   # Admin main dashboard
│   ├── 10_Users.py            # User management
│   ├── 11_Gates.py            # Gate management
│   └── 12_Settings.py         # Admin settings

TESTING THE APP
===============

1. Customer Signup & Login
   - Go to http://localhost:8501
   - Click "📋 Signup" tab
   - Create account with details
   - Login with credentials
   - Should see "✅ Login successful"

2. Event Browsing
   - Navigate to "🎉 Events"
   - Browse cricket tournament, music festival, etc.
   - Click "🎟️ Book Now"

3. Ticket Booking
   - Select number of tickets
   - Choose preferences
   - Click "✅ Confirm Booking"
   - Should see gate assignment

4. Admin Portal
   - Login with admin credentials
   - Click "👨‍💼 Admin Login"
   - Should see "📊 Dashboard" tab
   - View analytics, users, gates

TROUBLESHOOTING
===============

Issue: "Connection refused" error
--> Make sure FastAPI backend is running on http://localhost:8000
--> Run: python -m uvicorn app.main:app --reload

Issue: "Module not found" for streamlit
--> Install dependencies: pip install -r requirements.txt
--> Make sure virtual environment is activated

Issue: Database connection error
--> Check Firebase credentials in firebase_config.py
--> Verify network connectivity
--> Check backend logs for errors

Issue: Can't login with created account
--> Verify account was created successfully (check backend logs)
--> Make sure username is correct (check Firebase console)
--> Clear browser cache and cookies

NEXT STEPS
==========

✅ Core infrastructure complete
✅ Authentication working
✅ Customer portal pages ready
✅ Admin dashboard ready

🔜 Integration Tasks:
   1. Connect Events to Firebase backend (fetch real events)
   2. Implement ticket booking API integration
   3. Add Google Maps for stadium navigation
   4. Implement food ordering system
   5. Add real-time notifications
   6. Complete Security Portal
   7. Add data persistence for admin actions
   8. Implement crowd analytics real-time updates

📝 CUSTOMIZATION
================

To add new pages:
1. Create pages/X_PageName.py
2. Import SessionManager and APIClient
3. Add logout button for consistency
4. Follow existing page structure

To modify styling:
- Edit CSS in app.py (st.markdown with CSS)
- Use Streamlit theming: .streamlit/config.toml

To change API endpoint:
- Edit api_client.py API_BASE_URL
- Currently set to: http://localhost:8000

SUPPORT
=======

For issues or questions:
1. Check backend logs: Run FastAPI with verbose logging
2. Check browsers developer console (F12)
3. Review Streamlit docs: https://docs.streamlit.io
4. Check Firebase console for data verification

Happy Building! 🚀
"""
