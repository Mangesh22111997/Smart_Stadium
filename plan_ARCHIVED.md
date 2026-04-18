# 🏟️ Smart Stadium System – Copilot Build Guide

## 🎯 Goal
Build a prototype system using:
- **Backend:** Python (FastAPI)
- **Frontend:** Streamlit (Python-based UI)
- Modular, scalable architecture

---

# 🧱 STEP 1: Project Setup

## Prompt
Create a scalable backend project using FastAPI in Python.

Requirements:
- Modular folder structure:
  - app/
    - routes/
    - services/
    - models/
    - utils/
- Include main entry file (main.py)
- Use async support
- Add basic health check route

## Expected Outcome
- Clean folder structure
- FastAPI server runs successfully
- `/health` endpoint returns status

---

# 👤 STEP 2: User Management System

## Prompt
Create a user management module.

Requirements:
- Each user has:
  - unique user_id (UUID)
  - name
  - email/phone
  - past commute preference
- APIs:
  - register user
  - get user by ID
  - update preferences
- Use Pydantic models
- Use in-memory storage (dictionary)

## Expected Outcome
- Users can be created and retrieved
- Unique ID assigned per user
- Preferences stored for reuse

---

# 🎟️ STEP 3: Ticket Booking System

## Prompt
Create a ticket booking API.

Requirements:
- Mandatory fields:
  - user_id
  - event_id
  - commute_mode (metro, bus, private, cab)
  - parking_required (true/false)
  - departure_preference (early, immediate, delayed)
- Validate inputs using Pydantic
- Store ticket data
- Return ticket_id

## Expected Outcome
- Ticket created successfully
- All required fields enforced
- Data stored for further processing

---

# 🚪 STEP 4: Gate Assignment Engine (CORE)

## Prompt
Create a gate assignment service.

Requirements:
- Inputs:
  - commute_mode
  - departure_preference
- Define:
  - available gates (A, B, C, D)
  - max capacity per gate
- Logic:
  - Group users by commute type
  - Assign primary gate
  - Prevent overload by distributing users
- Return assigned gate

## Expected Outcome
- Users get assigned gates
- Load distributed across gates
- System avoids congestion at one gate

---

# 📊 STEP 5: Crowd Monitoring (Simulation)

## Prompt
Create a crowd monitoring module.

Requirements:
- Track:
  - gate_id
  - current crowd count
  - congestion level (low, medium, high)
- API:
  - get crowd status
- Simulate updates (random increments)

## Expected Outcome
- Live crowd data available
- Each gate shows congestion level
- Can be used for dynamic decisions

---

# 🔁 STEP 6: Dynamic Gate Reassignment

## Prompt
Enhance gate assignment system.

Requirements:
- If congestion = high:
  - reassign users to nearby gates
- Provide reason for reassignment
- Ensure minimal disruption

## Expected Outcome
- System reacts to congestion
- Users get updated gate suggestions
- Improves real-time flow

---

# 🍔 STEP 7: Food Ordering System

## Prompt
Create a food ordering module.

Requirements:
- User can:
  - place order
  - choose:
    - pickup booth
    - delivery zone (pillar-based)
- Assign:
  - booth based on least crowd
  - time slot for pickup

Return:
- order_id
- instructions

## Expected Outcome
- Orders created successfully
- Smart booth allocation works
- Time slots reduce crowding

---

# 🧭 STEP 8: Smart Booth Allocation

## Prompt
Create booth allocation logic.

Requirements:
- Input:
  - user zone/pillar
  - booth crowd data
- Output:
  - best booth
- Logic:
  - nearest + least crowded

## Expected Outcome
- Users assigned optimal booth
- Avoids long queues

---

# 🚨 STEP 9: Emergency (SOS System)

## Prompt
Create an emergency handling system.

Requirements:
- User triggers SOS
- Capture:
  - user_id
  - location
  - emergency_type
- Find:
  - nearest safe exit
- Notify staff

## Expected Outcome
- Emergency requests handled
- Exit guidance generated
- Staff alerted

---

# 📱 STEP 10: Notification System

## Prompt
Create notification service.

Requirements:
- Send messages for:
  - gate assignment
  - reassignment
  - food ready
  - emergency alerts
- Simulate using logs

## Expected Outcome
- Messages triggered correctly
- Works across modules

---

# 👮 STEP 11: Staff Dashboard APIs

## Prompt
Create staff dashboard APIs.

Requirements:
- View:
  - crowd per gate
  - emergencies
  - food orders
- Controls:
  - open/close gate
  - redirect crowd

## Expected Outcome
- Staff can monitor system
- Can take manual actions

---

# 🧠 STEP 12: Integration Layer

## Prompt
Create central service layer.

Requirements:
- Connect:
  - users
  - tickets
  - gates
  - crowd
  - food
  - emergency
- Ensure smooth communication

## Expected Outcome
- System works end-to-end
- Clean architecture maintained

---

# 🔄 STEP 13: End-to-End Simulation

## Prompt
Create simulation script.

Flow:
1. Create users
2. Book tickets
3. Assign gates
4. Simulate crowd
5. Reassign gates
6. Place food orders
7. Trigger emergency

## Expected Outcome
- Full system demo works
- Logs show complete flow

---

# 🎨 STEP 14: Streamlit UI (Frontend)

## Prompt
Create a Streamlit app.

Features:
- User registration
- Ticket booking
- View gate assignment
- Order food
- Trigger SOS

Use API calls to backend.

## Expected Outcome
- Simple UI working
- End-to-end demo ready
- Judges can interact live

---

# 🏆 Final Notes

- Focus on:
  - Gate assignment logic
  - Real-time adaptability
- Keep UI simple but functional
- Explain system clearly during demo

---

# 🚀 Final Goal

A working prototype that:
- Guides users
- Manages crowd
- Handles food
- Responds to emergencies
