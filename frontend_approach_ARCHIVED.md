# 🏟️ Smart Stadium UI & Admin Portal – Feature Guide + Copilot Prompts

## 🎯 Goal
Design two interfaces:
1. **User Booking App (Streamlit UI)**
2. **Admin/Staff Portal (Streamlit UI)**

Both should be simple, functional, and demo-ready.

---

# 📱 USER BOOKING APP (Streamlit UI)

## 🧩 1. User Registration / Login

### Prompt
Create a Streamlit UI for user registration and login.

Requirements:
- Input fields:
  - name
  - email/phone
- Button:
  - Register / Login
- On submit:
  - call backend API
  - store user_id in session state

### Expected Outcome
- User can register/login
- Session persists user_id
- Clean UI form

---

## 🎟️ 2. Ticket Booking Form (CORE FEATURE)

### Prompt
Create a ticket booking form in Streamlit.

Requirements:
- Inputs:
  - event_id (dropdown or text)
  - commute_mode (radio: metro, bus, private, cab)
  - parking_required (checkbox)
  - departure_preference (radio: early, immediate, delayed)
- Submit button:
  - call booking API
- Display:
  - ticket_id
  - assigned gate

### Expected Outcome
- User books ticket successfully
- Gate assignment shown instantly

---

## 🚪 3. Gate Information Display

### Prompt
Create a UI section to display gate details.

Requirements:
- Show:
  - assigned gate
  - instructions (e.g., "Use Gate B for faster exit")
- Add refresh button for real-time updates

### Expected Outcome
- Users always see latest gate info
- Supports dynamic reassignment

---

## 📊 4. Live Crowd Status (Optional but impressive)

### Prompt
Create a Streamlit dashboard to show crowd status.

Requirements:
- Display:
  - gate-wise crowd level (low, medium, high)
- Use simple charts or text indicators

### Expected Outcome
- Users can see congestion levels
- Adds transparency

---

## 🍔 5. Food Ordering UI

### Prompt
Create a food ordering interface.

Requirements:
- Inputs:
  - food item (dropdown)
  - quantity
  - delivery type:
    - pickup booth
    - delivery zone (pillar)
- Submit:
  - call food API
- Display:
  - order_id
  - pickup booth or pillar info
  - time slot

### Expected Outcome
- Food ordering works end-to-end
- Clear instructions shown

---

## 🧭 6. Navigation Instructions (Simple)

### Prompt
Create a section to show navigation instructions.

Requirements:
- Display:
  - "From your section, walk towards Gate X"
- Static or rule-based text is fine

### Expected Outcome
- Users understand movement path
- Improves usability

---

## 🚨 7. Emergency (SOS Button)

### Prompt
Create an SOS button in Streamlit.

Requirements:
- Button: "Trigger Emergency"
- On click:
  - call emergency API
- Display:
  - exit instructions
  - confirmation message

### Expected Outcome
- Emergency request triggered
- User gets guidance instantly

---

## 🔔 8. Notifications Panel

### Prompt
Create a notifications section.

Requirements:
- Display messages:
  - gate updates
  - food ready
  - alerts
- Use simple list or text area

### Expected Outcome
- Central place for updates
- Improves UX clarity

---

# 👮 ADMIN / STAFF PORTAL (Streamlit UI)

---

## 📊 1. Crowd Monitoring Dashboard (MOST IMPORTANT)

### Prompt
Create a dashboard for staff to monitor crowd.

Requirements:
- Display:
  - gate-wise crowd count
  - congestion level
- Use charts (bar or table)

### Expected Outcome
- Staff sees real-time crowd distribution
- Easy decision-making

---

## 🚪 2. Gate Control Panel

### Prompt
Create a gate control UI.

Requirements:
- For each gate:
  - status: open/closed
- Buttons:
  - open gate
  - close gate

### Expected Outcome
- Staff can control gate availability
- Useful for congestion handling

---

## 🔁 3. Crowd Redirection Control

### Prompt
Create a redirection control panel.

Requirements:
- Select:
  - source gate
  - target gate
- Button:
  - "Redirect Crowd"
- Trigger backend logic

### Expected Outcome
- Staff can manually reroute crowd
- Overrides system decisions

---

## 🚨 4. Emergency Monitoring Panel

### Prompt
Create emergency dashboard.

Requirements:
- Display:
  - active SOS requests
  - location
  - type
- Button:
  - "Resolve"

### Expected Outcome
- Staff sees all emergencies
- Can respond quickly

---

## 🍔 5. Food Operations Dashboard

### Prompt
Create food management dashboard.

Requirements:
- Display:
  - orders per booth
  - pending vs completed
- Highlight crowded booths

### Expected Outcome
- Staff manages food flow
- Avoids bottlenecks

---

## 👥 6. Staff Allocation Insights

### Prompt
Create a staff allocation view.

Requirements:
- Show:
  - expected crowd per gate
- Suggest:
  - number of staff needed

### Expected Outcome
- Helps planning
- Data-driven staffing

---

## 🔔 7. Broadcast Notification System

### Prompt
Create a broadcast messaging UI.

Requirements:
- Input:
  - message text
- Button:
  - send to all users or specific gate

### Expected Outcome
- Staff can send announcements
- Real-time communication

---

# 🏆 FINAL UI STRATEGY

## User App Focus:
- Simplicity
- Guidance
- Real-time updates

## Admin Portal Focus:
- Control
- Visibility
- Decision-making

---

# 🚀 FINAL GOAL

A complete prototype where:
- Users get guided experience
- Staff controls operations
- System adapts dynamically
