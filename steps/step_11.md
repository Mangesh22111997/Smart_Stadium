# STEP 11: Create Staff Dashboard APIs

## Status
✅ COMPLETED

## Objective
Create a staff-focused dashboard API system that provides real-time monitoring of stadium operations and enables staff to take corrective actions. The dashboard consolidates data from all previous modules (crowd, gates, emergencies, food, notifications) and provides write endpoints for staff to manage:
- Gate operations (open, close, force reassign)
- Emergency response coordination
- Crowd flow management
- Food ordering oversight
- Notification acknowledgments

---

## Requirements Met

### 1. Dashboard Data Models
- Comprehensive Pydantic models for dashboard data views
- Models for gate management actions
- Models for emergency response operations
- Models for staff activity tracking

### 2. Read-Only Data Endpoints (Real-time Monitoring)
- Current gate status dashboard (utilization, entry times)
- Live crowd levels per gate and zone
- Active emergencies with priority levels and exit guidance
- Food order queue with status breakdown
- Active notifications alert system

### 3. Write Endpoints (Staff Control)
- Manual gate open/close operations
- Gate capacity override functionality
- Force user reassignment to different gates
- Emergency response acknowledgment
- Emergency status updates from staff

### 4. Staff Action Logging
- Track all staff actions (who did what, when, why)
- Create audit trail for operational changes
- Log gate operations, reassignments, emergency responses
- Provide metrics on staff productivity and decision patterns

### 5. Monitoring & Insights
- Staff workload dashboard (active alerts, response times)
- Gate utilization trends and patterns
- Emergency response effectiveness metrics
- Food ordering system health

---

## API Endpoints

### READ-ONLY ENDPOINTS (Monitoring & Reporting)

#### 1. GET /staff/dashboard/summary
**Get high-level system status summary**
```
Response (200 OK):
{
    "timestamp": "2024-03-15T11:30:00Z",
    "total_gates": 4,
    "total_users_in_stadium": 1250,
    "average_gate_utilization": 67.5,
    "total_active_emergencies": 2,
    "critical_emergencies": 1,
    "pending_notifications": 15,
    "food_orders_pending": 23,
    "gate_status": "OPERATIONAL",
    "system_status": "HEALTHY"
}
```

#### 2. GET /staff/dashboard/gates
**Get gates dashboard with real-time status and capacity**
```
Response (200 OK):
{
    "gates": [
        {
            "gate_id": "A",
            "capacity": 100,
            "current_occupancy": 67,
            "utilization_percent": 67,
            "entry_time_minutes": 20,
            "status": "OPERATIONAL",
            "crowding_level": "MEDIUM",
            "recent_events": [
                "Gate reassignment triggered at 11:20",
                "3 users reassigned to Gate B at 11:15"
            ]
        }
    ],
    "total_capacity": 400,
    "total_occupancy": 268,
    "average_utilization": 67,
    "timestamp": "2024-03-15T11:30:00Z"
}
```

#### 3. GET /staff/dashboard/crowd/{location}
**Get detailed crowd data for specific gate/zone**
```
Query Parameters:
- include_history: boolean (include hourly trends)
- time_window: "1h", "24h", "7d" (aggregation period)

Response (200 OK):
{
    "location": "gate_a",
    "current_occupancy": 67,
    "capacity": 100,
    "utilization_percent": 67,
    "crowding_level": "MEDIUM",
    "entry_time_minutes": 20,
    "peak_time": "11:15",
    "arrival_rate": 5.2,
    "departure_rate": 3.8,
    "net_change": 1.4,
    "recommendations": [
        "Consider opening alternate gates to distribute crowd",
        "Current entry time acceptable"
    ],
    "history": [
        {"time": "11:00", "occupancy": 62},
        {"time": "11:15", "occupancy": 67},
        {"time": "11:30", "occupancy": 67}
    ]
}
```

#### 4. GET /staff/dashboard/emergencies
**Get all active emergencies with details and staff assignments**
```
Query Parameters:
- priority: optional filter ("CRITICAL", "HIGH", "MEDIUM", "LOW")
- status: optional filter ("reported", "responding", "resolved")

Response (200 OK):
{
    "active_emergencies": [
        {
            "emergency_id": "emerg-12345",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "emergency_type": "CROWD_CRUSH",
            "priority": "CRITICAL",
            "location": "gate_b",
            "description": "High crowd density causing safety concern",
            "nearest_exit": "exit_2",
            "exit_distance_meters": 60,
            "status": "responding",
            "staff_assigned": "staff-01",
            "staff_arrival_time": 2,
            "reported_at": "2024-03-15T11:25:00Z",
            "response_time_seconds": 30
        }
    ],
    "total_active": 2,
    "critical_count": 1,
    "high_count": 1,
    "timestamp": "2024-03-15T11:30:00Z"
}
```

#### 5. GET /staff/dashboard/food-orders
**Get food ordering system status and queue overview**
```
Query Parameters:
- booth_id: optional filter by specific booth
- status: optional filter ("placed", "preparing", "ready", "pickup")

Response (200 OK):
{
    "total_orders": 1245,
    "pending_orders": 23,
    "ready_for_pickup": 8,
    "booths": [
        {
            "booth_id": "B01",
            "capacity": 10,
            "current_queue": 3,
            "average_prep_time_minutes": 15,
            "status": "OPERATIONAL",
            "orders_ready": 2,
            "oldest_waiting_minutes": 18
        }
    ],
    "system_status": "OPERATIONAL",
    "recommendations": [
        "B03 has longest queue (5 orders). Consider redirecting orders to B04",
        "All booths within normal operating parameters"
    ],
    "timestamp": "2024-03-15T11:30:00Z"
}
```

#### 6. GET /staff/dashboard/notifications
**Get active notification queue for monitoring**
```
Query Parameters:
- priority: optional filter
- acknowledged: boolean filter

Response (200 OK):
{
    "total_notifications": 4523,
    "unacknowledged_count": 15,
    "active_critical": 2,
    "active_high": 5,
    "notifications": [
        {
            "notification_id": "notif-xxx",
            "notification_type": "EMERGENCY",
            "title": "Emergency Alert",
            "priority": "CRITICAL",
            "status": "SENT",
            "created_at": "2024-03-15T11:25:00Z",
            "acknowledged": false
        }
    ],
    "timestamp": "2024-03-15T11:30:00Z"
}
```

#### 7. GET /staff/dashboard/tickets-by-gate/{gate_id}
**Get all tickets assigned to specific gate**
```
Response (200 OK):
{
    "gate_id": "A",
    "total_tickets": 67,
    "tickets": [
        {
            "ticket_id": "ticket-xxx",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "assigned_gate": "A",
            "entry_time": "2024-03-15T10:15:00Z",
            "parking_required": true,
            "commute_mode": "CAR",
            "status": "active"
        }
    ],
    "timestamp": "2024-03-15T11:30:00Z"
}
```

### WRITE ENDPOINTS (Staff Actions)

#### 8. PUT /staff/gates/{gate_id}/open
**Open a gate**
```
Request:
{
    "reason": "Redistribute crowd flow",
    "staff_id": "staff-01",
    "notes": "Opening Gate C to balance with Gate A"
}

Response (200 OK):
{
    "gate_id": "C",
    "action": "OPENED",
    "previous_status": "CLOSED",
    "new_status": "OPERATIONAL",
    "action_timestamp": "2024-03-15T11:30:30Z",
    "staff_id": "staff-01",
    "reason": "Redistribute crowd flow"
}
```

#### 9. PUT /staff/gates/{gate_id}/close
**Close a gate**
```
Request:
{
    "reason": "Maintenance required",
    "staff_id": "staff-01",
    "estimated_reopening_minutes": 30,
    "affected_users_action": "reassign_to_nearest"  // or "hold", "redirect"
}

Response (200 OK):
{
    "gate_id": "B",
    "action": "CLOSED",
    "previous_status": "OPERATIONAL",
    "new_status": "CLOSED",
    "affected_users": 23,
    "users_reassigned": 23,
    "action_timestamp": "2024-03-15T11:30:30Z",
    "staff_id": "staff-01"
}
```

#### 10. PUT /staff/gates/{gate_id}/capacity-override
**Override gate capacity for emergency purposes**
```
Request:
{
    "new_capacity": 120,
    "reason": "Emergency evacuation - need additional exit capacity",
    "staff_id": "staff-01",
    "duration_minutes": 15
}

Response (200 OK):
{
    "gate_id": "A",
    "previous_capacity": 100,
    "new_capacity": 120,
    "override_active": true,
    "expires_at": "2024-03-15T11:45:30Z",
    "reason": "Emergency evacuation"
}
```

#### 11. POST /staff/reassign-user
**Manually reassign a user from current gate to new gate**
```
Request:
{
    "ticket_id": "ticket-xxx",
    "new_gate_id": "C",
    "reason": "Crowd management - user opted for less crowded gate",
    "staff_id": "staff-01"
}

Response (200 OK):
{
    "ticket_id": "ticket-xxx",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "previous_gate": "A",
    "new_gate": "C",
    "reassignment_type": "MANUAL",
    "reassignment_timestamp": "2024-03-15T11:30:30Z",
    "staff_id": "staff-01",
    "reason": "Crowd management - user opted for less crowded gate"
}
```

#### 12. POST /staff/emergency/respond
**Staff acknowledge and begin response to emergency**
```
Request:
{
    "emergency_id": "emerg-12345",
    "staff_id": "staff-01",
    "response_type": "immediate",  // or "scheduled", "monitoring"
    "initial_notes": "Crowd dispersal in progress"
}

Response (200 OK):
{
    "emergency_id": "emerg-12345",
    "staff_id": "staff-01",
    "status": "responding",
    "response_time_seconds": 45,
    "initial_notes": "Crowd dispersal in progress",
    "timestamp": "2024-03-15T11:30:30Z"
}
```

#### 13. PUT /staff/emergency/{emergency_id}/status
**Update emergency status**
```
Request:
{
    "new_status": "resolved",  // or "escalated", "monitoring"
    "staff_id": "staff-01",
    "resolution_notes": "Crowd successfully redirected, no injuries reported",
    "evacuation_required": false
}

Response (200 OK):
{
    "emergency_id": "emerg-12345",
    "previous_status": "responding",
    "new_status": "resolved",
    "resolution_time_seconds": 180,
    "staff_id": "staff-01",
    "resolved_at": "2024-03-15T11:33:30Z"
}
```

#### 14. PUT /staff/notification/{notification_id}/acknowledge
**Staff acknowledge a notification**
```
Request:
{
    "staff_id": "staff-01",
    "action_taken": "reassigned_2_users_to_gate_c",
    "notes": "Coordinated with gate staff"
}

Response (200 OK):
{
    "notification_id": "notif-xxx",
    "acknowledged": true,
    "acknowledged_by": "staff-01",
    "acknowledged_at": "2024-03-15T11:30:30Z",
    "action_taken": "reassigned_2_users_to_gate_c"
}
```

#### 15. GET /staff/actions/history
**Get staff action history and audit trail**
```
Query Parameters:
- staff_id: optional filter by specific staff member
- action_type: optional filter ("gate_open", "gate_close", "reassignment", "emergency_response")
- limit: 100 (default)
- skip: 0 (default)
- time_window: "1h", "24h", "7d"

Response (200 OK):
{
    "actions": [
        {
            "action_id": "act-xxx",
            "timestamp": "2024-03-15T11:30:30Z",
            "staff_id": "staff-01",
            "action_type": "gate_close",
            "gate_id": "B",
            "reason": "Maintenance",
            "affected_users": 23,
            "duration_seconds": 300
        }
    ],
    "total_count": 47,
    "staff_action_counts": {
        "staff-01": 23,
        "staff-02": 15,
        "staff-03": 9
    }
}
```

#### 16. GET /staff/workload
**Get staff workload and performance metrics**
```
Response (200 OK):
{
    "active_staff": 3,
    "staff_members": [
        {
            "staff_id": "staff-01",
            "status": "ACTIVE",
            "assigned_zone": "gates_a_b",
            "active_emergencies": 1,
            "actions_today": 23,
            "last_action": "2024-03-15T11:30:30Z",
            "response_time_average_seconds": 45,
            "workload_percent": 75
        }
    ],
    "total_workload_percent": 68,
    "critical_alerts_pending": 2,
    "timestamp": "2024-03-15T11:30:00Z"
}
```

---

## Files Created

### 1. `app/models/staff_dashboard.py`
Pydantic models for staff dashboard operations.

**Models:**
- `GateSummary`: Real-time gate status with occupancy, utilization, entry times
- `ControlRoomSummary`: High-level system status overview
- `CrowdAnalysis`: Detailed crowd metrics with recommendations
- `GateManagementRequest`: Request to open/close gate or override capacity
- `GateActionResponse`: Response from gate operations
- `ManualReassignmentRequest`: Request to manually reassign user
- `StaffReassignmentResponse`: Response from reassignment operation
- `EmergencyResponseRequest`: Staff acknowledging emergency
- `EmergencyResponseAction`: Response from emergency response
- `NotificationAcknowledgmentRequest`: Staff acknowledge notification
- `StaffActionLog`: Audit entry for staff actions
- `StaffWorkloadMetrics`: Individual staff member workload data
- `StaffWorkloadResponse`: Overall workload summary

### 2. `app/services/staff_dashboard_service.py`
Service layer for staff dashboard operations.

**Key Features:**
- `get_dashboard_summary()`: Aggregate current system state
- `get_gates_dashboard()`: Real-time gate metrics
- `get_crowd_analysis()`: Detailed crowd data with trends
- `get_active_emergencies()`: Emergency overview with assignments
- `get_food_order_status()`: Food system health check
- `get_notifications_queue()`: Active alerts and notifications
- `get_tickets_by_gate()`: User assignments per gate
- `open_gate()`: Enable gate operations
- `close_gate()`: Disable gate and handle user redirects
- `override_gate_capacity()`: Increase capacity for emergency
- `manual_reassignment()`: Staff-directed user movement
- `respond_to_emergency()`: Begin emergency response
- `update_emergency_status()`: Resolve emergencies
- `acknowledge_notification()`: Mark notifications as handled
- `get_action_history()`: Audit trail of staff actions
- `get_staff_workload()`: Staff performance and workload metrics

### 3. `app/routes/staff_dashboard_routes.py`
FastAPI routes exposing staff dashboard functionality.

**Endpoints:**
- `GET /staff/dashboard/summary` - System status overview
- `GET /staff/dashboard/gates` - Gate operations dashboard
- `GET /staff/dashboard/crowd/{location}` - Crowd analysis
- `GET /staff/dashboard/emergencies` - Active emergencies
- `GET /staff/dashboard/food-orders` - Food ordering status
- `GET /staff/dashboard/notifications` - Notification queue
- `GET /staff/dashboard/tickets-by-gate/{gate_id}` - User assignments
- `PUT /staff/gates/{gate_id}/open` - Open gate
- `PUT /staff/gates/{gate_id}/close` - Close gate
- `PUT /staff/gates/{gate_id}/capacity-override` - Override capacity
- `POST /staff/reassign-user` - Manual reassignment
- `POST /staff/emergency/respond` - Respond to emergency
- `PUT /staff/emergency/{emergency_id}/status` - Update emergency status
- `PUT /staff/notification/{notification_id}/acknowledge` - Acknowledge notification
- `GET /staff/actions/history` - Action audit trail
- `GET /staff/workload` - Staff workload metrics

---

## Data Model

### Gateway Summary Structure
```
GateSummary {
    gate_id: str
    capacity: int
    current_occupancy: int
    utilization_percent: float (0-100)
    entry_time_minutes: int
    status: "OPERATIONAL" | "CLOSED" | "MAINTENANCE"
    crowding_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    recent_events: List[str]
}
```

### Staff Action Log Structure
```
StaffActionLog {
    action_id: str (UUID-based)
    timestamp: datetime
    staff_id: str
    action_type: "gate_open" | "gate_close" | "capacity_override" | "reassignment" | "emergency_response" | "notification_acknowledged"
    related_entity_id: str (gate_id, emergency_id, ticket_id, etc.)
    reason: str
    affected_users: int (optional)
    duration_seconds: int (optional)
    notes: str (optional)
}
```

### Emergency Response Context
```
EmergencyContext {
    emergency_id: str
    user_id: UUID
    location: str
    emergency_type: str
    reported_at: datetime
    status: "reported" | "responding" | "resolved"
    staff_assigned: str (staff_id)
    response_start_time: datetime
    completion_time: Optional[datetime]
    resolution_notes: str
}
```

---

## Key Features

### 1. Real-Time Monitoring Dashboard
- **Gate Status**: Live utilization, capacity, entry times, crowding levels
- **Crowd Metrics**: Current occupancy, arrival/departure rates, trends
- **Emergency Overview**: Active emergencies with priority and location
- **Food System Health**: Order queue, booth status, processing times
- **Notification Queue**: Unacknowledged critical alerts

### 2. Gate Management Operations
- **Open/Close Gates**: Staff can operationally control gate access
- **Capacity Overrides**: Emergency override for evacuation scenarios
- **Status Transitions**: Automatic user redistribution when gates change status
- **Closure Notifications**: Affected users informed of gate closures

### 3. User Reassignment Control
- **Manual Reassignment**: Staff override for user gate assignments
- **Reason Tracking**: Why reassignment was requested
- **Validation**: Ensure new gate has available capacity
- **Audit Trail**: Every reassignment logged with staff identification

### 4. Emergency Response Coordination
- **Real-Time Assignment**: Staff claim emergencies and begin response
- **Status Updates**: Progress tracking from reported → responding → resolved
- **Response Time Metrics**: Track effectiveness of emergency handling
- **Escalation Path**: Ability to escalate if needed

### 5. Notification Management
- **Acknowledgment System**: Staff confirm receipt and action
- **Action Tracking**: What action staff took in response
- **Priority Filtering**: Focus on CRITICAL and HIGH priority alerts
- **Audit Trail**: All staff notifications tracked

### 6. Comprehensive Action Logging
- **Audit Trail**: Every staff action recorded with timestamp
- **Staff Attribution**: Which staff member took action
- **Reason Documentation**: Why action was taken
- **Impact Tracking**: Numbers of users affected, resources consumed
- **Time-Based Filtering**: View historical actions by date range

### 7. Staff Workload Monitoring
- **Individual Metrics**: Active emergencies, actions today, response times
- **Zone Assignment**: Track which staff monitor which areas
- **Workload Percentage**: Visual indication of staff utilization
- **Performance Tracking**: Response time averages, action frequency

### 8. Cross-Module Integration
Integrates with all previous modules:
- **gate_service**: Get current status, open/close, reassign
- **crowd_service**: Real-time occupancy and trends
- **emergency_service**: Get active emergencies, respond, update status
- **food_service**: Get booth status and order queue
- **notification_service**: Display and acknowledge notifications
- **reassignment_service**: Track manual reassignments

### 9. Actionable Recommendations
- **Crowd Recommendations**: Suggest gate opening/closing based on utilization
- **Exit Strategy**: Recommend actions for emergency scenarios
- **Food System**: Alert staff to booth bottlenecks
- **Load Balancing**: Suggest user redistributions

### 10. Smart Data Aggregation
- **Real-Time Summary**: Single dashboard shows all critical metrics
- **Trend Analysis**: Crowd arrival/departure rates, peak times
- **Capacity Planning**: Forecast when gates reach threshold
- **Resource Optimization**: Show utilization patterns

---

## Validation Rules

### Path Parameters
- `gate_id`: Must be valid gate (A, B, C, D)
- `emergency_id`: UUID-based emergency ID format
- `notification_id`: UUID-based notification ID format
- `location`: Valid location string (gate_a, gate_b, etc.)

### Request Body Validation
- `staff_id`: Non-empty string, max 50 chars
- `reason`: Non-empty string, max 500 chars
- `notes`: Optional, max 1000 chars
- `new_capacity`: Must be > 0, typically > current_occupancy
- `duration_minutes`: Positive integer, max 480 (8 hours)

### Query Parameters
- `priority`: One of CRITICAL, HIGH, MEDIUM, LOW
- `status`: Valid status for context (gate: OPERATIONAL/CLOSED, emergency: reported/responding/resolved)
- `limit`: 1-1000 (default 100)
- `skip`: 0-100000 (default 0)
- `time_window`: "1h", "24h", "7d"

---

## Next Steps

### STEP 12: Integration Layer
- Create orchestration service connecting all components
- Implement workflows that tie together user journey from entry to exit
- Auto-trigger notifications from key events
- Auto-reassign users based on thresholds
- Coordinate crowd management across all gates

### Dependencies
- STEP 11 staff_dashboard_service.py must be tested before STEP 12
- STEP 12 will call staff_dashboard endpoints from admin UI
- STEP 13 simulation will use staff dashboard for scenario management

### Integration Points
- Dashboard queries will refresh every 5-10 seconds in real implement
- Staff actions will trigger automatic notifications via notification_service
- Emergency responses will auto-notify affected users
- Gate closures will auto-reassign tickets

---

## Testing Checklist

- [ ] Get dashboard summary and verify all fields populated
- [ ] Get gates dashboard and verify occupancy calculations
- [ ] Get crowd analysis for each gate
- [ ] Get active emergencies list
- [ ] Get food order status
- [ ] Get notifications queue
- [ ] Get tickets assigned to each gate
- [ ] Open a gate and verify status change
- [ ] Close a gate and verify users are reassigned
- [ ] Override gate capacity
- [ ] Manually reassign user to different gate
- [ ] Respond to emergency as staff
- [ ] Update emergency status to resolved
- [ ] Acknowledge notification
- [ ] View action history
- [ ] Get staff workload metrics
- [ ] Verify staff_id attribution on all actions
- [ ] Test pagination on history endpoint
- [ ] Test time_window filtering
- [ ] Test priority filtering on emergencies

---

## Implementation Notes

### Data Source Integration
- **gates_db**: From gate_service (current occupancy, capacity, status)
- **crowd_db**: From crowd_service (real-time occupancy per gate)
- **emergencies_db**: From emergency_service (active emergencies)
- **orders_db**: From food_service (pending food orders)
- **notifications_db**: From notification_service (unacknowledged alerts)
- **tickets_db**: From ticket_service (user assignments)

### Real-Time Updates
In production, should implement:
- WebSocket connections for live dashboard updates
- Server-sent events (SSE) for real-time alerts
- Polling interval of 5 seconds for demo purposes
- Event-driven notifications on state changes

### Staff Authentication
Current implementation uses staff_id from request bodies. In production:
- Implement OAuth2 with JWT tokens
- Role-based access control (security staff, gate operators, managers)
- Verify staff credentials before allowing state changes
- Track authenticated user, not just staff_id

### Capacity Management
Gate capacity override strategy:
- Temporary override for emergency (default 15-30 minutes)
- Automatic revert when emergency resolved
- Manual revert option available
- Audit trail of all override changes

### Audit Trail
All staff actions logged with:
- Timestamp (exact second)
- Staff ID who performed action
- Action type and target
- Before/after state
- Reason provided by staff
- Affected entities (users, gates, etc.)
- Duration of action if applicable

