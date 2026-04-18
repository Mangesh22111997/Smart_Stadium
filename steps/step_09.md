# 🚨 STEP 9: Emergency (SOS System)

## Status: ✅ COMPLETED

## Objective
Create an emergency handling system that captures SOS requests, identifies locations, finds nearest exits, and alerts staff.

## Requirements Met
- ✅ User can trigger SOS
- ✅ Capture user_id, location, emergency_type
- ✅ Find nearest safe exit
- ✅ Alert staff immediately
- ✅ Track emergency status
- ✅ Multiple emergency types supported

## API Endpoints

### 1. Trigger Emergency (SOS)
```
POST /emergency/sos
Body:
{
  "user_id": "uuid",
  "emergency_type": "medical",
  "location": "gate_a",
  "description": "User feeling dizzy"
}
Response:
{
  "emergency_id": "uuid",
  "user_id": "uuid",
  "emergency_type": "medical",
  "location": "gate_a",
  "nearest_exit": "exit_1",
  "exit_distance": 50,
  "status": "reported",
  "staff_notified": true,
  "reported_at": "2026-04-14T12:30:00"
}
```

### 2. Get Emergency Details
```
GET /emergency/{emergency_id}
Response: Emergency information
```

### 3. List Active Emergencies
```
GET /emergency/list/active
Response: All ongoing emergencies
```

### 4. Update Emergency Status
```
PUT /emergency/{emergency_id}/status
Body:
{
  "status": "resolved"
}
Response: Updated emergency
```

### 5. Get Nearest Exit
```
POST /emergency/nearest-exit
Body:
{
  "location": "gate_a"
}
Response: Nearest exit with distance
```

### 6. Get User Emergencies
```
GET /emergency/user/{user_id}
Response: All emergencies for user
```

## Files Created
- `app/models/emergency.py` - Emergency Pydantic models
- `app/services/emergency_service.py` - Emergency handling logic
- `app/routes/emergency_routes.py` - Emergency API endpoints

## Data Model
```python
class Emergency:
  - emergency_id: UUID
  - user_id: UUID
  - emergency_type: str
  - location: str
  - description: str
  - nearest_exit: str
  - exit_distance: int (meters)
  - status: str (reported, responding, resolved, cancelled)
  - reported_at: datetime
  - resolved_at: Optional[datetime]
  - staff_assigned: Optional[str]
```

## Emergency Types
- `medical` - Medical emergency (injury, illness)
- `crowd` - Crowd crush / stampede risk
- `lost` - Person lost
- `threat` - Security threat
- `fire` - Fire emergency
- `evacuation` - Evacuation needed
- `lost_child` - Missing child
- `harassment` - Harassment / assault
- `other` - Other emergency

## Stadium Locations
```
Gates: gate_a, gate_b, gate_c, gate_d, gate_center
Zones: pillar_1, pillar_2, pillar_3, pillar_4, center
Booths: booth_1, booth_2, booth_3, booth_4, booth_5
Sections: section_north, section_south, section_east, section_west
```

## Exit Network
```
Exits: exit_1, exit_2, exit_3, exit_4, exit_main
Distance Map:
- From gate_a: exit_1 (50m), exit_4 (100m)
- From gate_b: exit_2 (60m), exit_1 (120m)
- From gate_c: exit_3 (55m), exit_2 (110m)
- From gate_d: exit_4 (65m), exit_3 (100m)
- From center: exit_main (40m), all others (80-150m)
```

## Status Flow
```
reported → responding → resolved
           ↓
         cancelled
```

## Staff Notification
- Emergency type determines priority
- Priority levels: CRITICAL, HIGH, MEDIUM, LOW
- Auto-escalation if not resolved in time
- Staff assignment tracking

## Priority Levels
```
CRITICAL: medical, fire, crowd, threat (immediate response)
HIGH: lost_child, harassment, evacuation (urgent response)
MEDIUM: lost, other (standard response)
LOW: miscellaneous (informational)
```

## Distance Calculation
```
Distance in meters based on location:
- Same area: 20-50m
- Adjacent area: 50-100m
- Opposite area: 150-200m
```

## Key Features
- Real-time emergency tracking
- Automatic nearest exit calculation
- Priority-based staff assignment
- Status management
- Emergency history
- Location accuracy
- Multi-type support

## Safety Measures
- ✅ Immediate staff notification
- ✅ Nearest exit guidance
- ✅ Location verification
- ✅ Escalation on timeout
- ✅ Emergency logging

## Integration Points
- User: Via user_id
- Gate/Crowd: Via location
- Notification: Auto-alert staff
- Dashboard: Real-time monitoring

## Use Cases
1. User triggers medical emergency at Gate A
   - System finds nearest exit (50m)
   - Staff alerted immediately
   - User receives exit guidance

2. Child reported lost at Pillar 2
   - System creates lost_child emergency
   - Staff dispatched to area
   - Parent notified with updates

3. Security threat detected
   - Emergency marked CRITICAL
   - All nearby staff alerted
   - Evacuation coordinates sent

## Emergency Resolution
- Staff confirm incident details
- Take appropriate action
- Mark emergency resolved
- Log for safety review

## Next Steps
→ STEP 10: Notification System
