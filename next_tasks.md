# 🏟️ Smart Stadium – Full UI & Portal Build Guide (Streamlit + FastAPI + Firebase)

## 🎯 Goal
Build 3 portals:
1. Customer Portal (/)
2. Admin Portal (/admin)
3. Security Portal (/security)

Backend already uses Firebase (Auth + DB) ✅

---

# 📱 1. CUSTOMER PORTAL (/)

---

## 🧩 1.1 User Signup Page (Detailed Profile)

### Prompt
Create a Streamlit signup UI.

Requirements:
- Input fields:
  - name
  - date_of_birth
  - occupation (dropdown: student, business, service, other)
  - address
  - city
  - state
  - hobbies (multi-select, optional)
  - email/phone
  - password
- Submit:
  - call Firebase signup API
- Store user_id in session

### Expected Outcome
- Full user profile stored in Firebase
- Clean onboarding experience
- Useful data for analytics

---

## 🔐 1.2 Login Page

### Prompt
Create login UI.

Requirements:
- email/phone
- password
- call signin API
- store session token

### Expected Outcome
- User logs in successfully
- Session maintained

---

## 🎉 1.3 Event Discovery Page

### Prompt
Create event listing UI.

Requirements:
- Fetch events from backend
- Display:
  - event name
  - date
  - location
- Button:
  - "Book Now"

### Expected Outcome
- Users can explore events
- Smooth navigation to booking

---

## 🎟️ 1.4 Ticket Booking Page

### Prompt
Create ticket booking UI.

Requirements:
- Inputs:
  - number of tickets
  - commute_mode
  - parking_required
  - departure_preference
- Submit:
  - call booking API
- Show:
  - ticket_id
  - assigned gate

### Expected Outcome
- Ticket booking complete
- Gate assigned instantly

---

## 🗺️ 1.5 Google Maps Integration (IMPORTANT)

### Prompt
Integrate Google Maps in Streamlit.

Requirements:
- Show stadium location
- Show route:
  - user → stadium
- Inside stadium:
  - highlight nearest gate
- Optional:
  - show congestion-based route

### Expected Outcome
- Visual navigation
- High demo impact

---

## 🍔 1.6 Food Ordering UI

### Prompt
Create food ordering UI.

Requirements:
- Inputs:
  - food item
  - quantity
  - pickup booth OR pillar
- Show:
  - order status
  - instructions

### Expected Outcome
- Smooth ordering flow
- Clear pickup instructions

---

## 🚨 1.7 SOS Button

### Prompt
Create emergency UI.

Requirements:
- Button: "Emergency"
- Call SOS API
- Show:
  - exit instructions

### Expected Outcome
- Emergency handled instantly
- Safe exit guidance

---

## 🔔 1.8 Notification Panel

### Prompt
Create notifications section.

Requirements:
- Show:
  - gate updates
  - food ready
  - alerts

### Expected Outcome
- Central communication panel

---

# 👨‍💼 2. ADMIN PORTAL (/admin)

---

## 🧩 2.1 Create New Event (VERY IMPORTANT)

### Prompt
Create event creation UI.

Requirements:
- Inputs:
  - event_name
  - date
  - start_time
  - end_time
  - venue_type (stadium, auditorium, hall)
  - seating_capacity
  - number_of_gates
  - parking_available (yes/no)
  - parking_capacity
  - nearby_metro_count
  - nearby_bus_stops
  - gates_near_transport
  - staff_available (yes/no)
  - number_of_staff
  - vendor_booths_available (yes/no)
  - number_of_booths
- Submit:
  - store in Firebase

### Expected Outcome
- Event created successfully
- Full infrastructure captured

---

## 📊 2.2 Crowd Monitoring Dashboard

### Prompt
Create admin dashboard.

Requirements:
- Show:
  - crowd per gate
  - congestion level
- Charts using pandas

### Expected Outcome
- Real-time insights
- Better decision-making

---

## 🚪 2.3 Gate Management

### Prompt
Create gate control UI.

Requirements:
- Open/close gates
- Show status

### Expected Outcome
- Admin controls flow

---

## 🔁 2.4 Crowd Redirection

### Prompt
Create redirection UI.

Requirements:
- Select source gate
- Select target gate
- Trigger reroute

### Expected Outcome
- Manual override possible

---

## 🍔 2.5 Food Management

### Prompt
Create food dashboard.

Requirements:
- Show:
  - orders per booth
  - delays
- Highlight congestion

### Expected Outcome
- Food flow optimized

---

## 👥 2.6 Staff Planning

### Prompt
Create staff estimation logic.

Requirements:
- Use:
  - crowd %
  - event size
- Suggest staff count

### Expected Outcome
- Smart staffing decisions

---

# 🔐 3. SECURITY PORTAL (/security)

---

## 📊 3.1 Live Monitoring Dashboard

### Prompt
Create security dashboard.

Requirements:
- Show:
  - live crowd
  - alerts
  - anomalies

### Expected Outcome
- Security visibility

---

## 🚨 3.2 Emergency Monitoring

### Prompt
Create SOS monitoring UI.

Requirements:
- Show:
  - active SOS
  - location
- Button:
  - resolve

### Expected Outcome
- Fast emergency response

---

## 🚪 3.3 Restricted Gate Control

### Prompt
Create restricted gate control.

Requirements:
- Control emergency exits only
- No access to event creation

### Expected Outcome
- Role-based access control

---

## 🔔 3.4 Alert System

### Prompt
Create alert system.

Requirements:
- Show:
  - anomalies
  - high congestion alerts

### Expected Outcome
- Proactive response system

---

# 🗺️ FINAL INTEGRATION PLAN

## Google Services Used:
- Firebase (Auth + DB) ✅
- Google Maps (Navigation) 🔜

---

# 🏆 FINAL GOAL

A complete system where:
- Customer → books, navigates, orders
- Admin → creates & manages event
- Security → monitors & handles emergencies

---

# 🚀 FINAL CHECKLIST

- [ ] Signup with full profile
- [ ] Event creation working
- [ ] Ticket booking + gate assignment
- [ ] Google Maps integrated
- [ ] Admin dashboard working
- [ ] Security portal working
