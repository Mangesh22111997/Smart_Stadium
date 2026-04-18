# 🏟️ Smart Stadium System - Complete Project Guide

## 🌟 Project Overview
The **Smart Stadium System** is a next-generation event management platform designed to provide a premium, seamless experience for stadium attendees. It integrates real-time data, food ordering, and smart navigation into a unified digital interface.

---

## 🏗️ Technical Architecture
The system is built using a modern decoupled architecture:
- **Backend**: Python **FastAPI** serving a RESTful API.
- **Frontend**: **Streamlit** for a dynamic, reactive user interface.
- **Database**: **Firebase Realtime Database** for live data synchronization.
- **Hosting/Cloud**: Fully integrated with **Google Cloud Platform (GCP)** services.

---

## ☁️ Google Cloud Services Integrated

### 1. Firebase Realtime Database
- **Role**: Core data persistence layer.
- **Implementation**: Stores user profiles, event data, ticket bookings, and food orders.
- **Real-time Sync**: Enables instant status updates (e.g., ticket confirmation, parking availability).

### 2. Firebase Authentication
- **Role**: Secure user management.
- **Implementation**: Handles login, registration, and session token validation via `firebase_config.py`.

### 3. Google Maps Integration
- **Role**: Navigation and Venue Awareness.
- **Implementation**: Embedded interactive maps for:
    - Overall stadium layout.
    - Specific gate details (Red markers).
    - Parking zone occupancy and location.

### 4. Firebase Cloud Storage (via RTDB)
- **Role**: Asset management.
- **Implementation**: Branded assets (Backgrounds, Success GIFs) are stored as optimized Base64 strings in the database, ensuring they are accessible globally without local path dependencies.

---

## 📁 Project Structure & Code Breakdown

### 🔹 Backend (`/app`)
- **`main.py`**: API entry point and middleware configuration.
- **`/models`**: Pydantic schemas for data validation (Tickets, Food, Events).
- **`/routes`**: API endpoints organized by feature:
    - `auth_routes.py`: User registration and login logic.
    - `bookings_routes.py`: Ticket creation and status management.
    - `food_routes.py`: Menu management and order placement.
- **`/services`**: Business logic layer (Firebase CRUD operations).
- **`/config`**: Centralized `firebase_config.py` for GCP credentials.

### 🔹 Frontend (`/streamlit_app`)
- **`app.py`**: Main dashboard entry point.
- **`/pages`**: Individual feature modules:
    - `3_Home.py`: Personalized dashboard for logged-in users.
    - `4_Events.py`: Event discovery and selection.
    - `7_Food.py`: Digital menu with "Confirm Selection" logic.
    - `16_Event_Booking.py`: The core "Unified Booking" page.
    - `5_Bookings.py`: User history with linked Ticket and Food IDs.
    - `6_Maps.py`: Interactive Google Maps navigation.
- **`/utils`**: Shared helpers:
    - `api_client.py`: Wrapper for all backend communication.
    - `ui_helper.py`: Premium styling, database asset fetching, and custom animations.
    - `session_manager.py`: Securely handles user session state across pages.

---

## 🔄 Core Workflow: The "Unified Booking" Loop
We have refined the booking process into a single, seamless transaction:
1. **Event Selection**: User chooses an event from the catalog.
2. **Dynamic Travel**: User selects a commute mode. The system **automatically enables/disables parking** based on the choice (e.g., Metro vs. Private Car).
3. **Food Pre-order**: User enters the menu, selects items, and "Confirms Selection" to return to the booking page.
4. **Atomic Confirmation**: A single "Confirm & Pay" click places both the food order and the ticket booking, linking them perfectly in the backend.
5. **Interactive Guidance**: Upon success, a custom branded **Interwind Animation** plays, and the user is redirected to their history.

---

## 🛠️ Key Files & Their Roles
| File | Role | Key Functionality |
| :--- | :--- | :--- |
| `seed_test_users.py` | Developer Tool | Populates the DB with test accounts for Admin and Customers. |
| `ui_helper.py` | UI Core | Fetches 4K backgrounds and success GIFs from Firebase RTDB. |
| `maps_helper.py` | Navigation | Generates dynamic Google Maps embed URLs for gates and parking. |
| `bookings_routes.py` | Business Logic | Handles the complex linking of Food IDs to Ticket IDs. |

---

## 🚀 Recent Fixes & Optimizations
- **Indentation & Imports**: Resolved all `ModuleNotFoundError` (folium, branca) and `IndentationError` in the food/booking pages.
- **Direct Google Maps**: Migrated from Folium to direct Google Maps embeds for a more premium experience.
- **Database Assets**: Moved all images and animations to Firebase to eliminate "Local File Not Found" errors.
- **Silent Loading**: Implemented `show_spinner=False` for database fetches to ensure a clean, "no-flicker" UI.

---

**This project is now in a production-ready state with a fully integrated GCP-powered ecosystem.**

