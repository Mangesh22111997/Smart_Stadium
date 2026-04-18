# STEP 12: Build Integration Layer

## Status
✅ COMPLETED

## Objective
Create an orchestration service that ties together all 10 previous modules (users, tickets, gates, crowd, reassignment, food, booth allocation, emergency, notifications, staff dashboard) into cohesive workflows. The integration layer manages:
- End-to-end user journeys from stadium entry to exit
- Automatic triggering of notifications from key events
- Intelligent user reassignment based on crowd thresholds
- Coordinated crowd management across all gates
- Real-time event propagation between modules
- Complete audit trail of all orchestrated actions

---

## Requirements Met

### 1. User Journey Orchestration
- **Complete Entry Flow**: Register user → Book ticket → Assign gate → Monitor crowd → Real-time reassignment
- **Exit Flow**: Auto-acknowledge food pickup → Generate exit summary → Notification of successful exit
- **Error Handling**: Graceful fallbacks if any module unavailable

### 2. Event-Driven Notifications
- Auto-trigger GATE_ASSIGNMENT notifications when user books ticket
- Auto-trigger GATE_REASSIGNMENT when system reassigns user
- Auto-trigger FOOD_ORDER notifications when order placed/ready
- Auto-trigger EMERGENCY notifications immediately on SOS
- Auto-trigger CROWD_WARNING at >80% capacity per gate
- Priority-based notification queuing

### 3. Intelligent Reassignment System
- Monitor all gates for >75% utilization
- Auto-reassign users from overcrowded gates
- Preference-aware reassignment (respect commute_mode preference)
- Evacuation support (instant reassignment to exits)
- Smooth handoff notifications

### 4. Workflow Orchestration Endpoints
- Multi-step workflows exposed as single endpoints
- User journey tracking
- Real-time status progression
- Event replay capability for debugging

### 5. Cross-Module Synchronization
- Gate crowd data synced with ticket assignments
- Reassignment events sync tickets and gates
- Food order booth assignments sync with crowd
- Emergency exit network aligned with gate locations

---

## API Endpoints

### User Journey Orchestration

#### 1. POST /orchestration/user-journey/register-and-book
**Complete entry workflow: register user + book ticket + assign gate**
```
Request:
{
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "9876543210",
    "commute_mode": "CAR",
    "parking_required": true,
    "event_date": "2024-03-15",
    "arrival_time": "2024-03-15T10:00:00Z"
}

Response (201 Created):
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "ticket_id": "ticket-xxx",
    "assigned_gate": "A",
    "entry_time_minutes": 15,
    "notifications_sent": [
        "GATE_ASSIGNMENT to email"
    ],
    "status": "READY_TO_ENTER",
    "journey_id": "journey-xxx",
    "workflow_steps": {
        "user_registration": "COMPLETED",
        "ticket_booking": "COMPLETED",
        "gate_assignment": "COMPLETED",
        "notification_sent": "COMPLETED"
    }
}
```

#### 2. GET /orchestration/user-journey/{user_id}
**Get user's complete journey status and history**
```
Response (200 OK):
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "user@example.com",
    "journey_status": "IN_PROGRESS",
    "current_gate": "A",
    "current_utilization": "67%",
    "entry_time_estimate": "15 minutes",
    "events": [
        {
            "timestamp": "2024-03-15T09:30:00Z",
            "event_type": "USER_REGISTERED",
            "details": "User account created"
        },
        {
            "timestamp": "2024-03-15T09:32:00Z",
            "event_type": "TICKET_BOOKED",
            "details": "Ticket ticket-xxx created"
        },
        {
            "timestamp": "2024-03-15T09:32:05Z",
            "event_type": "GATE_ASSIGNED",
            "details": "Assigned to Gate A"
        },
        {
            "timestamp": "2024-03-15T09:32:10Z",
            "event_type": "NOTIFICATION_SENT",
            "details": "Gate assignment notification sent"
        },
        {
            "timestamp": "2024-03-15T09:40:00Z",
            "event_type": "GATE_REASSIGNMENT",
            "details": "Gate reassigned from A to C due to congestion"
        }
    ],
    "food_orders": [
        {
            "order_id": "order-xxx",
            "status": "ready",
            "booth_id": "B03"
        }
    ],
    "active_emergencies": 0,
    "notifications_history": [
        {
            "notification_id": "notif-xxx",
            "type": "GATE_REASSIGNMENT",
            "status": "DELIVERED"
        }
    ]
}
```

### Intelligent Reassignment

#### 3. POST /orchestration/reassignment/check-and-redistribute
**Check all gates and redistribute users from overcrowded gates**
```
Query Parameters:
- utilization_threshold: 75 (default, percentage)
- max_users_to_move: 50 (default)
- prefer_preferences: true (default, respect preferences)

Response (200 OK):
{
    "reassignments_made": 12,
    "users_affected": 12,
    "redistribution_summary": {
        "gate_a": {
            "before_utilization": 89,
            "after_utilization": 78,
            "users_moved_out": 12,
            "users_moved_in": 0
        },
        "gate_b": {
            "before_utilization": 45,
            "after_utilization": 55,
            "users_moved_out": 0,
            "users_moved_in": 12
        }
    },
    "notifications_sent": 12,
    "timestamp": "2024-03-15T10:45:00Z"
}
```

#### 4. POST /orchestration/reassignment/evacuation
**Orchestrate emergency evacuation from specific location**
```
Query Parameters:
- location: "gate_a" (gate to evacuate)
- emergency_type: "FIRE" (reason)
- target_gates: ["C", "D"] (optional, specific gates to use)

Response (200 OK):
{
    "users_evacuated": 67,
    "evacuation_id": "evac-xxx",
    "affected_users": [
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticket_id": "ticket-xxx",
            "previous_gate": "A",
            "new_gate": "C",
            "reassignment_type": "EMERGENCY_EVACUATION"
        }
    ],
    "notifications_sent": 67,
    "emergency_id": "emerg-xxx",
    "status": "COMPLETED",
    "timestamp": "2024-03-15T10:45:00Z"
}
```

### Automated Event-Driven Flows

#### 5. GET /orchestration/workflows/event-log
**Get complete event log for all orchestrated actions**
```
Query Parameters:
- start_time: ISO datetime (optional)
- end_time: ISO datetime (optional)
- event_type: optional filter
- limit: 500 (default)
- skip: 0 (default)

Response (200 OK):
{
    "total_events": 4523,
    "events": [
        {
            "event_id": "evt-xxx",
            "timestamp": "2024-03-15T10:45:00Z",
            "event_type": "GATE_REASSIGNMENT_ORCHESTRATED",
            "source_module": "crowd_service",
            "trigger": "Utilization exceeded 75%",
            "affected_users": 12,
            "notifications_triggered": ["GATE_REASSIGNMENT"],
            "status": "COMPLETED"
        }
    ],
    "event_type_summary": {
        "GATE_REASSIGNMENT_ORCHESTRATED": 156,
        "NOTIFICATION_SENT": 4200,
        "EMERGENCY_RESPONSE_ORCHESTRATED": 23,
        "FOOD_ORDER_FULFILLED": 1850
    }
}
```

#### 6. POST /orchestration/workflows/food-ordering-flow
**End-to-end workflow: Place food order → Assign booth → Send notification**
```
Request:
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [
        {"item_id": "pizza_margherita", "quantity": 1}
    ]
}

Response (201 Created):
{
    "order_id": "order-xxx",
    "booth_id": "B03",
    "estimated_prep_time_minutes": 15,
    "pickup_time": "2024-03-15T11:00:00Z",
    "booth_crowd_level": "MEDIUM",
    "user_notifications_sent": [
        "order_placed",
        "estimated_ready_time"
    ],
    "workflow_steps": {
        "food_order_created": "COMPLETED",
        "booth_allocated": "COMPLETED",
        "crowd_sync": "COMPLETED",
        "notification_sent": "COMPLETED"
    },
    "status": "PREPARED"
}
```

#### 7. POST /orchestration/workflows/emergency-sos
**Comprehensive emergency response: Create SOS → Assign staff → Notify users → Prepare evacuation**
```
Request:
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "emergency_type": "CROWD_CRUSH",
    "location": "gate_b",
    "description": "Large crowd buildup causing safety concern"
}

Response (201 Created):
{
    "emergency_id": "emerg-xxx",
    "status": "responding",
    "staff_assigned": "staff-01",
    "nearest_exit": "exit_2",
    "exit_distance_meters": 60,
    "affected_users_count": 67,
    "notifications_sent": {
        "critical_alerts": 67,
        "staff_alerts": 3,
        "adjacent_gates": 45
    },
    "workflow_steps": {
        "emergency_created": "COMPLETED",
        "staff_assigned": "COMPLETED",
        "notifications_sent": "COMPLETED",
        "evacuation_routes_computed": "COMPLETED",
        "adjacent_gates_notified": "COMPLETED"
    },
    "evacuation_plan": {
        "primary_exit": "exit_2",
        "secondary_exits": ["exit_1", "exit_4"],
        "route_distances": {"exit_2": 60, "exit_1": 100, "exit_4": 80}
    },
    "timestamp": "2024-03-15T10:45:00Z"
}
```

### System Synchronization

#### 8. POST /orchestration/sync/all-systems
**Force synchronization of all modules**
```
Query Parameters:
- include_crowd_update: true (optional)
- include_reassignment_check: true (optional)
- include_notification_queue: true (optional)

Response (200 OK):
{
    "sync_timestamp": "2024-03-15T10:45:00Z",
    "modules_synced": [
        "crowd_service",
        "gate_service",
        "ticket_service",
        "reassignment_service",
        "food_service",
        "emergency_service",
        "notification_service"
    ],
    "sync_results": {
        "crowd_service": {
            "gates_updated": 4,
            "status": "SYNCED"
        },
        "reassignment_service": {
            "reassignments_made": 8,
            "status": "SYNCED"
        },
        "food_service": {
            "orders_processed": 23,
            "status": "SYNCED"
        }
    },
    "total_events_processed": 145
}
```

#### 9. GET /orchestration/health
**Get health status of all integrated modules**
```
Response (200 OK):
{
    "overall_status": "HEALTHY",
    "timestamp": "2024-03-15T10:45:00Z",
    "modules": {
        "user_service": {"status": "HEALTHY", "users_count": 1250},
        "ticket_service": {"status": "HEALTHY", "active_tickets": 1250},
        "gate_service": {"status": "HEALTHY", "gates_operational": 4},
        "crowd_service": {"status": "HEALTHY", "avg_utilization": 67},
        "reassignment_service": {"status": "HEALTHY", "pending_reassignments": 0},
        "food_service": {"status": "HEALTHY", "pending_orders": 23},
        "booth_allocation_service": {"status": "HEALTHY", "booths_operational": 5},
        "emergency_service": {"status": "HEALTHY", "active_emergencies": 0},
        "notification_service": {"status": "HEALTHY", "pending_notifications": 15},
        "staff_dashboard_service": {"status": "HEALTHY", "active_staff": 3}
    }
}
```

### Analytics & Reporting

#### 10. GET /orchestration/analytics/journey-summary
**Summary statistics on user journeys**
```
Query Parameters:
- time_window: "24h" (or "1h", "7d")

Response (200 OK):
{
    "total_users_today": 1250,
    "average_entry_time_minutes": 18,
    "users_reassigned": 156,
    "reassignment_rate_percent": 12.5,
    "reasons_for_reassignment": {
        "congestion": 120,
        "preference": 25,
        "user_request": 11
    },
    "average_journey_satisfaction": 4.2,
    "food_orders_placed": 450,
    "emergencies_responded": 2,
    "notifications_sent": 4523,
    "timestamp": "2024-03-15T23:59:00Z"
}
```

---

## Files Created

### 1. `app/models/integration.py`
Pydantic models for integration and orchestration.

**Models:**
- `RegisterAndBookRequest`: User registration + ticket booking in one step
- `UserJourneyResponse`: Complete user journey status and history
- `UserJourneyEvent`: Individual event in user journey
- `ReassignmentRequest`: Redistribution orchestration
- `ReassignmentResponse`: Results of redistribution
- `EvacuationRequest`: Emergency evacuation workflow
- `EvacuationResponse`: Evacuation results
- `FoodOrderingWorkflowRequest`: End-to-end food ordering
- `FoodOrderingWorkflowResponse`: Food ordering results
- `EmergencySOSWorkflowRequest`: Complete emergency workflow
- `EmergencySOSWorkflowResponse`: Emergency workflow results
- `SyncAllSystemsResponse`: Multi-system synchronization results
- `SystemHealthResponse`: Health status of all modules
- `EventLogEntry`: Event audit trail entry
- `JourneyAnalyticsResponse`: User journey analytics

### 2. `app/services/orchestration_service.py`
Core orchestration and integration logic.

**Key Methods:**
- `register_and_book_ticket()`: Complete entry workflow
- `get_user_journey()`: Retrieve user journey status
- `check_and_redistribute_users()`: Smart crowd redistribution
- `orchestrate_evacuation()`: Emergency evacuation flow
- `orchestrate_food_ordering()`: Complete food order workflow
- `orchestrate_emergency_sos()`: Comprehensive emergency response
- `sync_all_systems()`: Force synchronization
- `get_system_health()`: Module health check
- `get_event_log()`: Event audit trail
- `get_journey_analytics()`: User journey analytics
- `_log_workflow_event()`: Internal event logging
- `_propagate_notification()`: Auto-trigger notifications

### 3. `app/routes/integration_routes.py`
FastAPI routes exposing integration workflows.

**Endpoints (10 total):**
- `POST /orchestration/user-journey/register-and-book`
- `GET /orchestration/user-journey/{user_id}`
- `POST /orchestration/reassignment/check-and-redistribute`
- `POST /orchestration/reassignment/evacuation`
- `GET /orchestration/workflows/event-log`
- `POST /orchestration/workflows/food-ordering-flow`
- `POST /orchestration/workflows/emergency-sos`
- `POST /orchestration/sync/all-systems`
- `GET /orchestration/health`
- `GET /orchestration/analytics/journey-summary`

---

## Data Model

### Workflow Event Structure
```
WorkflowEvent {
    event_id: str (UUID-based)
    timestamp: datetime
    event_type: str (e.g., "USER_REGISTERED", "GATE_ASSIGNED", "NOTIFICATION_SENT")
    source_module: str ("user_service", "gate_service", etc.)
    trigger_reason: str (what caused this event)
    affected_entities: List[str] (user_ids, ticket_ids, etc.)
    notifications_triggered: List[str] (notification types sent)
    workflow_context: Dict (journey_id, emergency_id, etc.)
    status: "COMPLETED" | "FAILED" | "PENDING"
}
```

### User Journey Structure
```
UserJourney {
    user_id: UUID
    journey_id: str
    journey_status: "STARTED" | "IN_PROGRESS" | "COMPLETED" | "ERROR"
    current_gate: str
    entry_time_estimate: int
    events: List[WorkflowEvent]
    food_orders: List[OrderSummary]
    active_emergencies: int
    notifications_sent_count: int
    reassignment_count: int
}
```

---

## Key Features

### 1. Multi-Step Workflow Orchestration
- **Register + Book + Assign**: Single endpoint for complete entry flow
- **Food Ordering**: Order placement → Booth allocation → Notifications
- **Emergency Response**: SOS → Staff assignment → User notification → Evacuation planning
- **Evacuation**: Coordinate users across gates, maintain crowd balance

### 2. Automatic Event Propagation
- Gate assignment → Send notification
- Crowd exceeds threshold → Trigger reassignment
- Food ready → Send notification
- Emergency triggered → Multi-step escalation
- User reassignment → Update all related services

### 3. Intelligent Crowd Redistribution
- Monitor all gates continuously
- Identify overcrowded gates (>75% utilization)
- Calculate optimal redistributions
- Respect user preferences (commute_mode)
- Maintain emergency exit capacity
- Smooth handoff with notifications

### 4. Complete Event Audit Trail
- Every workflow step logged with timestamp
- Track which module initiated action
- Reason for each decision recorded
- Affected entities captured
- Notifications spawned tracked
- Full debugging capability

### 5. Real-Time Synchronization
- Gates synced with current crowd data
- Tickets synced with gate assignments
- Food orders synced with booth crowd
- Emergencies synced with gate status
- Notifications synced with all events
- Cross-module consistency maintained

### 6. Emergency Coordination
- Activate SOS with multi-step response
- Auto-assign staff from available pool
- Compute evacuation routes
- Notify affected users with exit info
- Coordinate evacuation from overcrowded areas
- Support partial/full evacuations

### 7. Food Service Integration
- Auto-select optimal booth based on crowd
- Sync booth occupancy with crowd_service
- Estimate prep and pickup times
- Notify user when ready
- Coordinate food orders with entry times

### 8. Analytics & Insights
- Track average entry times per gate
- Measure reassignment effectiveness
- Monitor user satisfaction
- Identify crowd patterns
- Emergency response metrics
- Staff workload distribution

### 9. System Health Monitoring
- Sample each service's data
- Report module-level health
- Identify connectivity issues
- Verify data consistency
- Performance metrics per module

### 10. Graceful Degradation
- Continue if one module unavailable
- Fallback workflows for failures
- Retry logic for transient errors
- Error propagation with context
- Transaction-like semantics where possible

---

## Validation Rules

### Path Parameters
- `user_id`: Valid UUID format
- `location`: Valid location string (gate_a, gate_b, etc.)

### Request Body Validation
- `email`: Valid email format
- `full_name`: 1-100 characters
- `phone`: 10-15 digits
- `commute_mode`: One of CAR, TRAIN, BUS, WALK
- `parking_required`: Boolean
- `utilization_threshold`: 0-99 (percentage)
- `max_users_to_move`: 1-1000

### Query Parameters
- `include_crowd_update`: Boolean
- `time_window`: "1h", "24h", "7d"
- `limit`: 1-1000
- `skip`: 0-100000

---

## Next Steps

### STEP 13: End-to-End Simulation Script
- Create comprehensive demo scenario
- Execute all 10 integrated modules
- Show complete user journey
- Trigger emergencies and responses
- Demonstrate crowd redistribution
- Generate performance metrics

### Dependencies
- STEP 12 orchestration_service.py must be fully tested
- STEP 13 simulation will call all orchestration endpoints
- STEP 14 Streamlit UI will use registration + booking endpoint

### Integration Points
- Simulation will use high-level orchestration endpoints
- UI will call orchestration for user flows
- Staff dashboard will query event_log for activities
- Analytics dashboards will use journey_analytics endpoint

---

## Testing Checklist

- [ ] Register new user and book ticket in single flow
- [ ] Verify gateway assignment matches preferences
- [ ] Verify gate assignment notification sent
- [ ] Get user journey and verify complete event log
- [ ] Check redistribution of users from overcrowded gate
- [ ] Verify reassignment notifications sent
- [ ] Trigger emergency SOS workflow
- [ ] Verify staff assigned to emergency
- [ ] Verify emergency notifications to affected users
- [ ] Orchestrate evacuation from gate
- [ ] Verify users moved to safe gates
- [ ] Complete food ordering workflow
- [ ] Verify booth allocated and notifications sent
- [ ] Check event log for all workflow events
- [ ] Get system health and verify all modules
- [ ] Get journey analytics
- [ ] Force system synchronization
- [ ] Verify event propagation across modules
- [ ] Test with multiple concurrent users
- [ ] Test emergency with partial evacuation

---

## Implementation Notes

### Event Logging
All orchestrated workflows emit events for auditability:
- Workflow initiated (with parameters)
- Each step completed (with results)
- Notifications triggered (with details)
- Errors encountered (with recovery path)
- Final status (success/failure with reason)

### Notification Triggering
Automatic notification logic:
- Gate assignment: Send immediately after assignment
- Reassignment: Send notification of change with reason
- Food order placed: Send estimated wait time
- Food ready: Send booth location + pickup window
- Emergency: Send escalation levels (critical)
- Crowd warning: Send at >80% but not >90% to avoid spam

### Crowd Redistribution Algorithm
1. Identify gates with utilization > threshold
2. Calculate available capacity in other gates
3. Select users to move (prioritize non-preference users)
4. Move in batches to smooth impact
5. Update all related data (tickets, crowd, notifications)
6. Log redistribution event with reasons

### Transaction Semantics
While not true ACID transactions (in-memory storage), maintain semantics:
- All-or-nothing: Complete workflow or fail atomically
- Durability: Event log captures all state changes
- Isolation: Lock at module level where needed
- Consistency: Cross-module sync ensures coherence

