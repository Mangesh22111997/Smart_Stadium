# 🏟️ Smart Stadium - Quick Reference & Testing Guide

**Frontend Running**: http://localhost:8502  
**Backend Status**: http://127.0.0.1:8000

---

## 🔐 Quick Login

### Test as Customer
```
URL: http://localhost:8502
Tab: "📝 Sign Up"

New Account:
Name: Rajesh Kumar
Email: rajesh@test.com
Phone: 9876543210
Password: test123

Then Sign In:
Email: rajesh@test.com
Password: test123
```

### Test as Admin
```
URL: http://localhost:8502
Bottom: "👮 Admin / Staff Portal" → Expand

Credentials:
Staff ID: STAFF-001
Password: staff123

Alternative:
Staff ID: STAFF-002
Password: admin456
```

---

## 📱 User App - What to Try

### 1. Ticket Booking
```
✓ Select event (Soccer Match)
✓ Choose commute (Private Vehicle)
✓ Enable parking
✓ Pick departure (Immediate)
✓ Set seats (2 tickets, VIP)
✓ Click "✓ Book Ticket"
→ Get Ticket ID and Gate assignment
```

### 2. Gate Info
```
✓ Shows your assigned gate
✓ Current capacity percentage
✓ Wait time estimate
✓ Alternative gates
✓ Entry instructions
✓ "🔄 Refresh" button works
```

### 3. Crowd Status
```
✓ Live bar chart shows gate utilization
✓ Color-coded (Green/Yellow/Red)
✓ Table shows all gates
✓ Tips section with recommendations
```

### 4. Food Ordering
```
✓ Browse 8 food items
✓ Add quantities (0-5)
✓ Choose delivery type:
  - Pickup at booth
  - Delivery to zone
✓ Click "✓ Place Order"
→ Get Order ID, total, ETA
```

### 5. My Journey
```
✓ See current step (2-5)
✓ Assigned gate shown
✓ Timeline of events:
  ✓ Complete tasks
  🟡 In Progress
  ⏳ Pending tasks
```

### 6. Notifications
```
✓ Real-time notification feed
✓ Types: Info, Success, Alert
✓ Timestamps for each
✓ Card-based display
```

### 7. Navigation
```
✓ Turn-by-turn directions to gate
✓ Walking time: 3-5 minutes
✓ Lane markers to follow
✓ Crowd tips
✓ Alternative routes
```

### 8. Emergency
```
✓ Safety status (🟢 Safe)
✓ Nearby exits list
✓ Buttons:
  - 📞 Call Staff
  - 🏥 Medical Emergency
  - 🆘 Emergency SOS
✓ Evacuation routes shown
```

---

## 👮 Admin Portal - What to Try

### 1. Crowd Dashboard
```
✓ 4 KPI cards at top
  - Total users
  - Gate utilization
  - Active gates
  - Critical gates
✓ Time-series chart (user growth)
✓ Gate distribution chart
✓ Status table with actions
```

### 2. Gate Control
```
✓ Select gate from dropdown
✓ See current status
✓ Choose action:
  - Keep Open
  - Pause Entry
  - Close Gate
✓ Quick buttons (Open All/Close All)
✓ Click "✓ Apply"
```

### 3. Crowd Redirection
```
✓ Select source gate
✓ Drag slider (50-150 users)
✓ Select target gate
✓ See capacity change estimate
✓ Click "✓ Initiate Redirection"
→ Confirmation with timeline
```

### 4. Emergency Panel
```
✓ Active emergencies list:
  - ID, Type, Location
  - Time, Status
✓ Buttons per emergency:
  - Resolve
✓ Dispatch actions:
  - Send Medical Team
  - Send Security
```

### 5. Food Operations
```
✓ Orders per booth chart
  - Pending (stacked)
  - Completed (stacked)
✓ Crowded booths alert:
  - Booth number
  - Order count
  - Wait time
  - Status indicator
```

### 6. Staff Allocation
```
✓ Table shows per gate:
  - Current staff
  - Recommended
  - Utilization %
✓ Difference shown (✓ or +number)
✓ "✓ Auto-Allocate Staff" button
→ Confirmation message
```

### 7. Broadcast Message
```
✓ Choose message type:
  - General
  - Gate Specific (select gates)
  - Emergency
✓ Select priority:
  - Normal / High / Urgent
✓ Type message in textarea
✓ Click "✓ Send Message"
→ Delivery confirmation
```

---

## 📊 Data Flow Examples

### User Registration Flow
```
1. Click "📝 Sign Up"
2. Fill: Name, Email, Phone, Password
3. Accept Terms & Conditions
4. Submit → User saved to users.json
5. Can sign in with email + password
6. Auto-assigned User ID (USER-0001, etc.)
```

### Ticket Booking Flow
```
1. Fill ticket form
2. Submit → Ticket ID generated
3. Gate auto-assigned based on ID hash
4. Session stores: booked_ticket, assigned_gate
5. Can view in "Gate Info" and "My Journey"
```

### Food Order Flow
```
1. Select items with quantities
2. Choose delivery type (Booth/Zone)
3. Submit → Order ID generated
4. See confirmation with total price
5. Estimated time: 15 minutes
```

---

## ✅ Testing Checklist

### Authentication
- [ ] Sign up new user
- [ ] Duplicate email error works
- [ ] Sign in with new account
- [ ] Wrong password rejected
- [ ] Admin login works (STAFF-001)
- [ ] Logout button works

### User Features
- [ ] Ticket booking generates ID and gate
- [ ] Gate info shows correct data
- [ ] Crowd status chart displays
- [ ] Food menu shows 8 items
- [ ] Food order calculates total
- [ ] Journey shows 5 timeline steps
- [ ] Notifications display
- [ ] Navigation shows step-by-step
- [ ] Emergency buttons respond

### Admin Features
- [ ] Crowd dashboard shows KPIs
- [ ] Charts display correctly
- [ ] Gate control dropdown works
- [ ] Crowd redirection slider works
- [ ] Emergency list shows
- [ ] Food operations chart displays
- [ ] Staff allocation table shows
- [ ] Broadcast form submits

### UI/UX
- [ ] Colors are consistent
- [ ] Forms are well-organized
- [ ] Buttons are clickable
- [ ] Messages appear on action
- [ ] Layout is responsive
- [ ] Navigation menus work
- [ ] Logout returns to login

---

## 🐛 Troubleshooting

### Frontend won't start
```bash
# Check Python environment
.venv\Scripts\Activate.ps1

# Try running again
streamlit run frontend_redesigned.py
```

### Can't sign in
```
1. Check users.json file exists
2. Verify email spelling
3. Try test account first:
   Email: john@example.com
   Password: password123
4. Check passwords match (case-sensitive)
```

### Admin login fails
```
1. Verify admins.json exists
2. Use correct credentials:
   STAFF-001 / staff123
3. Staff ID must match exactly
4. Password case-sensitive
```

### Chart not showing
```
1. Check plotly is installed
2. Verify data is being passed
3. Clear Streamlit cache:
   ctrl+shift+c in app
4. Refresh browser
```

### Data not saving
```bash
# Verify JSON files in project root:
- g:/Mangesh/Hack2Skill_Google_Challenge_copilot/users.json
- g:/Mangesh/Hack2Skill_Google_Challenge_copilot/admins.json

# Check auth_utils.py save_users() function
# Verify file permissions
```

---

## 📱 Browser Access

### Direct URLs
```
Main App: http://localhost:8502
Alternative: http://192.168.1.109:8502

Devices on Same Network:
Use: http://192.168.1.109:8502
```

### Recommended Browsers
- Chrome ✅
- Firefox ✅
- Safari ✅
- Edge ✅

---

## 🎯 Key Features by Tab

### User App (Horizontal Menu)
1. **Ticket Booking** - Book with options
2. **Gate Info** - See your gate details
3. **Crowd Status** - Live chart + data
4. **Food Ordering** - Browse & order
5. **My Journey** - Track progress
6. **Notifications** - Real-time updates
7. **Navigation** - Route to gate
8. **Emergency** - SOS & safety

### Admin Portal (Horizontal Menu)
1. **Crowd Dashboard** - KPIs + charts
2. **Gate Control** - Manage gates
3. **Crowd Redirection** - Move users
4. **Emergency Panel** - Monitor SOS
5. **Food Operations** - Track booths
6. **Staff Allocation** - Manage staff
7. **Broadcast Message** - Send updates

---

## 📊 Data Examples

### Sample Ticket
```
Ticket ID: TKT-USER-0001-1713139202
Gate: B
Event: Soccer Match - Final
Commute: Private Vehicle
Parking: Yes
Seats: 2 (VIP)
Status: ✓ Confirmed
```

### Sample Food Order
```
Order ID: ORD-1713139202
Items: Pizza (1), Burger (2), Fries (1)
Total: ₹580
Pickup: Booth-3
ETA: 15 minutes
```

### Sample Emergency Response
```
SOS ID: SOS-002
Type: Lost Person
Location: Zone-C (Gate-D)
Time: 15 seconds ago
Status: In Progress
Action: Security team dispatched
```

---

## 🚀 Performance Tips

- [x] Close other browser tabs
- [x] Refresh page if slow
- [x] Check internet connection
- [x] Use Chrome for best performance
- [x] Ensure backend is running
- [x] Clear browser cache

---

## 📞 Support Quick Links

**Documentation**:
- FRONTEND_COMPLETE_GUIDE.md - Full features
- IMPLEMENTATION_COMPLETE.md - All details
- UI_DESIGN_GUIDE.md - Design specs

**Files**:
- frontend_redesigned.py - Main app
- auth_utils.py - Authentication
- users.json - Customer data
- admins.json - Admin data

---

## 🎉 Ready to Test!

**Status**: ✅ All systems operational

### Start Testing:
1. Open http://localhost:8502
2. Create test account (Sign Up)
3. Explore user features
4. Login as admin
5. Test admin features
6. Try emergency features

**Enjoy!**

---

**Last Updated**: April 14, 2026  
**Version**: 1.0 Redesigned  
**Status**: ✅ Production Ready
