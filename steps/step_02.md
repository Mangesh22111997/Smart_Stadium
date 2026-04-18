# 👤 STEP 2: User Management System

## Status: ✅ COMPLETED

## Objective
Create a user management module with registration, retrieval, and preference management.

## Requirements Met
- ✅ User model with UUID, name, email/phone, and commute preference
- ✅ Register user API - POST `/users/register`
- ✅ Get user by ID - GET `/users/{user_id}`
- ✅ Update preferences - PUT `/users/{user_id}/preferences`
- ✅ List all users - GET `/users`
- ✅ Pydantic models for validation
- ✅ In-memory storage (dictionary)

## API Endpoints

### 1. Register User
```
POST /users/register
Body:
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "commute_preference": "metro"
}
Response:
{
  "user_id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "commute_preference": "metro",
  "created_at": "2026-04-14T..."
}
```

### 2. Get User
```
GET /users/{user_id}
Response:
{
  "user_id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "commute_preference": "metro",
  "created_at": "2026-04-14T..."
}
```

### 3. Update Preferences
```
PUT /users/{user_id}/preferences
Body:
{
  "commute_preference": "bus"
}
Response:
{
  "message": "Preferences updated",
  "user_id": "uuid-string",
  "commute_preference": "bus"
}
```

### 4. List All Users
```
GET /users
Response:
[
  { user object 1 },
  { user object 2 }
]
```

## Files Created
- `app/models/user.py` - User Pydantic models
- `app/services/user_service.py` - User business logic
- `app/routes/user_routes.py` - User API endpoints

## Data Model
```python
class User:
  - user_id: UUID (unique, auto-generated)
  - name: str
  - email: str
  - phone: str
  - commute_preference: str (metro, bus, private, cab)
  - created_at: datetime
```

## Storage
- Type: In-memory dictionary
- Location: `user_service.py` → `users_db`
- Key: user_id (UUID)
- Value: User object

## Commute Preferences Supported
- `metro` - Metro/Rail transport
- `bus` - Bus transport
- `private` - Private vehicle
- `cab` - Cab/Ride-share

## Key Features
- Unique user IDs using UUID4
- Email and phone validation
- Timestamp tracking (created_at)
- Easy preference updates
- List all registered users

## Next Steps
→ STEP 3: Ticket Booking System
