# 🚪 STEP 4: Gate Assignment Engine (CORE)

## Status: ✅ COMPLETED

## Objective
Create a smart gate assignment service that distributes users across gates based on commute mode and departure preference.

## Requirements Met
- ✅ Available gates: A, B, C, D
- ✅ Max capacity per gate: 100 users
- ✅ Smart grouping by commute type
- ✅ Load distribution logic to prevent overload
- ✅ Primary gate assignment
- ✅ Fallback gate assignment
- ✅ Return assigned gate with details

## API Endpoints

### 1. Assign Gate
```
POST /gates/assign
Body:
{
  "user_id": "uuid-string",
  "commute_mode": "metro",
  "departure_preference": "immediate"
}
Response:
{
  "gate_id": "A",
  "user_id": "uuid-string",
  "capacity_used": 45,
  "capacity_remaining": 55,
  "assignment_reason": "Metro users prefer Gate A"
}
```

### 2. Get Gate Status
```
GET /gates/{gate_id}
Response:
{
  "gate_id": "A",
  "current_count": 45,
  "max_capacity": 100,
  "utilization_percent": 45,
  "congestion_level": "low"
}
```

### 3. Get All Gates Status
```
GET /gates/status/all
Response: Array of all gates with status
```

### 4. Get Assignment for Ticket
```
GET /gates/assignment/{ticket_id}
Response: Assignment details or 404
```

## Files Created
- `app/models/gate.py` - Gate Pydantic models
- `app/services/gate_service.py` - Gate business logic & assignment
- `app/routes/gate_routes.py` - Gate API endpoints

## Gate Configuration

### Gates
```
Gate A: Metro primary
Gate B: Metro secondary
Gate C: Bus primary
Gate D: Bus secondary
```

### Capacity Per Gate
- Max: 100 users
- Alerts when > 75% (high congestion)
- Critical when > 90% (very high congestion)

## Assignment Logic

### By Commute Mode
- **Metro**: Gates A → B (prefer A, fallback to B)
- **Bus**: Gates C → D (prefer C, fallback to D)
- **Private/Cab**: Gates A, B, C, D (any available)

### By Departure Preference
- **Early**: Prefer Gates A, B (start early)
- **Immediate**: Prefer Gates B, C (balanced)
- **Delayed**: Prefer Gates C, D (start later)

### Load Distribution
1. Calculate utilization of preferred gates
2. If preferred gate < 75%, assign there
3. If > 75%, check fallback gate
4. If all full or > 90%, return highest available

## Congestion Levels
- **low**: 0-50% capacity
- **medium**: 50-75% capacity
- **high**: 75-90% capacity
- **critical**: > 90% capacity

## Data Models
```python
class Gate:
  - gate_id: str (A, B, C, D)
  - current_count: int
  - max_capacity: int
  - assignments: Dict[UUID, GateAssignment]

class GateAssignment:
  - ticket_id: UUID
  - gate_id: str
  - user_id: UUID
  - assigned_at: datetime
  - commute_mode: str
  - departure_preference: str
```

## Storage
- Type: In-memory with gate-specific data
- Gate counts: Updated per assignment
- Assignments: Tracked by ticket_id

## Key Features
- Smart gate selection based on preferences
- Load balancing across gates
- Congestion level tracking
- Assignment reason logging
- Historical assignment data
- Gate capacity management

## Smart Assignment Algorithm

```
1. Determine primary gates based on commute_mode
2. Determine preferred gate order based on departure_preference
3. For each preferred gate:
   - Check utilization
   - If available (< 90%), assign
4. If no primary gate available:
   - Find lowest utilized gate among all gates
   - Assign to lowest
5. Return assignment with reason & status
```

## Next Steps
→ STEP 5: Crowd Monitoring (Simulation)
