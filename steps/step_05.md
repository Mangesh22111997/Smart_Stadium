# 📊 STEP 5: Crowd Monitoring (Simulation)

## Status: ✅ COMPLETED

## Objective
Create a crowd monitoring module that tracks live crowd data and simulates dynamic updates.

## Requirements Met
- ✅ Track crowd count per gate
- ✅ Track congestion level per gate (low, medium, high, critical)
- ✅ Simulate crowd updates with random increments/decrements
- ✅ API to get crowd status
- ✅ Gate capacity monitoring
- ✅ Real-time flow data

## API Endpoints

### 1. Get Crowd Status for Gate
```
GET /crowd/{gate_id}
Response:
{
  "gate_id": "A",
  "current_crowd": 45,
  "congestion_level": "low",
  "estimated_entry_time": "2 minutes",
  "peak_capacity": 100,
  "flow_rate": 10,
  "trend": "increasing"
}
```

### 2. Get All Crowd Status
```
GET /crowd/status/all
Response: Array of all gates with crowd data
```

### 3. Simulate Crowd Update
```
POST /crowd/simulate-update
Response: Updated crowd data for all gates
```

### 4. Update Crowd Manually
```
PUT /crowd/{gate_id}
Body:
{
  "crowd_change": 5
}
Response: Updated gate crowd status
```

### 5. Get Flow Metrics
```
GET /crowd/metrics/all
Response: System-wide crowd metrics
```

## Files Created
- `app/models/crowd.py` - Crowd Pydantic models
- `app/services/crowd_service.py` - Crowd tracking & simulation
- `app/routes/crowd_routes.py` - Crowd API endpoints

## Data Model
```python
class CrowdData:
  - gate_id: str
  - current_crowd: int
  - peak_capacity: int
  - congestion_level: str (low, medium, high, critical)
  - avg_entry_time_minutes: float
  - flow_rate: int (people per minute)
  - trend: str (increasing, stable, decreasing)
  - last_updated: datetime
```

## Simulation Logic

### Random Updates
- Each simulation cycle adds/removes random 5-15 people per gate
- 60% chance of increase (people arriving)
- 40% chance of decrease (people leaving)
- Respects gate capacity

### Entry Time Calculation
```
Entry Time = (current_crowd / peak_capacity) * 30 minutes
```
- Low: 0-5 minutes
- Medium: 5-10 minutes
- High: 10-20 minutes
- Critical: >20 minutes

### Flow Rate
```
Flow Rate = people per minute based on congestion
- Low: 15-20 people/min
- Medium: 10-15 people/min
- High: 5-10 people/min
- Critical: <5 people/min
```

## Congestion Thresholds
- **low**: 0-50% capacity
- **medium**: 50-75% capacity
- **high**: 75-90% capacity
- **critical**: > 90% capacity

## Trend Analysis
- **increasing**: If current > last update
- **stable**: If current ≈ last update (±2%)
- **decreasing**: If current < last update

## Storage
- Type: In-memory gate-linked data
- Synced with Gate Service crowd counts
- Historical data tracked per gate

## Key Features
- Real-time crowd tracking
- Simulation of dynamic flow
- Entry time estimation
- Flow rate calculation
- Trend analysis
- Easy crowd data updates

## Simulation Features
- **Realistic patterns**: Random but within bounds
- **Capacity respecting**: Won't exceed gate max
- **Trend tracking**: Shows flow direction
- **Entry time estimation**: For user info
- **Flow metrics**: For staff monitoring

## Use Cases
1. Monitor live crowd at gates
2. Show estimated wait times to users
3. Detect sudden influxes
4. Track flow patterns
5. Alert staff on critical crowding

## Next Steps
→ STEP 6: Dynamic Gate Reassignment
