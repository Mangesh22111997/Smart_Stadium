# 🔁 STEP 6: Dynamic Gate Reassignment

## Status: ✅ COMPLETED

## Objective
Enhance gate assignment to dynamically reassign users when congestion becomes too high.

## Requirements Met
- ✅ Monitor gate congestion in real-time
- ✅ Detect high congestion (>75%) 
- ✅ Auto-reassign users to nearby/less-crowded gates
- ✅ Provide reassignment reasons
- ✅ Minimize disruption
- ✅ Track reassignment history

## API Endpoints

### 1. Check and Reassign (if needed)
```
POST /reassignments/check-and-reassign
Response:
{
  "reassignments_made": 2,
  "message": "Checked 4 gates, made 2 reassignments",
  "details": [
    {
      "ticket_id": "uuid",
      "user_id": "uuid",
      "from_gate": "A",
      "to_gate": "B",
      "reason": "High congestion at Gate A (85%), reassigning to nearby Gate B"
    }
  ]
}
```

### 2. Get Reassignment for Ticket
```
GET /reassignments/{ticket_id}
Response: Reassignment history for ticket
```

### 3. Manual Reassignment
```
POST /reassignments/manual
Body:
{
  "ticket_id": "uuid",
  "new_gate_id": "B",
  "reason": "User request"
}
Response: Reassignment details
```

### 4. Get All Reassignments
```
GET /reassignments
Response: All reassignment records
```

### 5. Get Gate Reassignments
```
GET /reassignments/gate/{gate_id}
Response: All reassignments from specific gate
```

## Files Created
- `app/models/reassignment.py` - Reassignment models
- `app/services/reassignment_service.py` - Reassignment logic
- `app/routes/reassignment_routes.py` - Reassignment API

## Data Model
```python
class Reassignment:
  - reassignment_id: UUID
  - ticket_id: UUID
  - user_id: UUID
  - from_gate: str (original gate)
  - to_gate: str (new gate)
  - reason: str (why reassigned)
  - reassigned_at: datetime
  - congestion_before: float (%)
  - congestion_after: float (%)
```

## Reassignment Logic

### Trigger Conditions
1. Gate congestion reaches HIGH (>75%)
2. Gate is approaching critical (>85%)
3. Manual override by staff

### Selection Algorithm
1. Identify critically congested gate
2. Find nearby gates with lower congestion
3. Select best available gate based on:
   - Lowest congestion score
   - Same commute mode preference (if possible)
   - Adjacent gate priority

### Nearby Gate Mapping
```
Gate A → B, C (nearby)
Gate B → A, D (nearby)
Gate C → D, A (nearby)
Gate D → C, B (nearby)
```

### Disruption Minimization
- Only reassign if:
  - New gate has <15% less congestion than current
  - New gate is not critical
  - User hasn't been reassigned recently
- Preserve commute mode preference
- Batch reassignments when possible

## Congestion Thresholds
- **low**: 0-50% - No action
- **medium**: 50-75% - Monitor
- **high**: 75-90% - Begin reassignments
- **critical**: >90% - Force reassignments

## Reassignment Reasons
- "Automatic: High congestion detected"
- "Automatic: Gate approaching critical capacity"
- "Manual: Staff request"
- "Manual: User request"
- "Temporary: Load balancing"

## Storage
- Type: In-memory list
- Tracks all reassignments (not replaced)
- Linked to ticket and gate data

## Safety Checks
- ✅ Don't reassign to equally congested gate
- ✅ Don't reassign to full gate
- ✅ Don't reassign multiple times rapidly
- ✅ Preserve user preferences when possible
- ✅ Log all reassignments

## Key Features
- Real-time congestion monitoring
- Smart gate selection
- Minimal disruption
- Full reassignment history
- Manual override capability
- Automatic cascading checks

## Reassignment Formula

```
Score = (congestion % × weight_congestion) +
        (distance × weight_distance) +
        (mode_mismatch × weight_mode)

Lower score = better target gate
```

## Use Cases
1. **Automatic**: System detects Gate A at 85%, reassigns 10 users to Gate B
2. **Manual**: Staff reassigns users from Gate C for maintenance
3. **Load Balancing**: System redistributes to prevent any gate hitting critical
4. **Recovery**: After crowd peak subsides, users gradually return

## Benefits
- Smoother flow during peak times
- Prevents single gate bottlenecks
- Reduces wait times system-wide
- Flexible capacity management
- Real-time adaptability

## Next Steps
→ STEP 7: Food Ordering System
