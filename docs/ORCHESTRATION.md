# Orchestration Service Documentation

## Overview

The **Orchestration Service** is the central coordination layer that integrates all stadium management modules into cohesive workflows. It coordinates multiple independent services to handle complex user journeys and emergency scenarios.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Orchestration Service (Central Hub)               │
│  - Coordinates multi-module workflows                          │
│  - Manages user journeys end-to-end                            │
│  - Handles emergency coordination                              │
└────────┬──────────────────────────────────────────────────────┘
         │
    ┌────┴────┬────────┬──────────┬──────────┬────────────────┐
    │          │        │          │          │                │
    ▼          ▼        ▼          ▼          ▼                ▼
┌────────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────┐ ┌──────────────┐
│ User   │ │Ticket│ │Gate  │ │Crowd     │ │Food  │ │Emergency     │
│Service │ │Service│ │Service│ │Service   │ │Service│ │Service       │
└────────┘ └──────┘ └──────┘ └──────────┘ └──────┘ └──────────────┘
```

## Core Workflows

### 1. Register and Book Ticket Workflow
**Endpoint**: `POST /api/v1/orchestration/user-journey/register-and-book`

**Flow**:
```
User Registration
    ↓
Ticket Booking
    ↓
Gate Assignment (with Preference Matching)
    ↓
Entry Time Estimation
    ↓
Send Notifications
    ↓
User Ready to Enter
```

**Request**:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+91-9876543210",
  "commute_mode": "Drive",
  "parking_required": true,
  "event_date": "2024-12-20",
  "arrival_time": "2024-12-20T14:30:00"
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "ticket_id": "uuid",
  "assigned_gate": "Gate-A",
  "entry_time_minutes": 18,
  "notifications_sent": ["GATE_ASSIGNMENT"],
  "status": "READY_TO_ENTER",
  "journey_id": "journey-uuid",
  "workflow_steps": {
    "user_registration": "COMPLETED",
    "ticket_booking": "COMPLETED",
    "gate_assignment": "COMPLETED",
    "notification_sent": "COMPLETED"
  }
}
```

### 2. User Journey Tracking
**Endpoint**: `GET /api/v1/orchestration/user-journey/{user_id}`

**Returns**:
- Current status of user
- Events history
- Active food orders
- Emergency alerts
- Recent notifications

**Use Cases**:
- Real-time user status dashboard
- Customer service inquiries
- Journey analytics

### 3. User Redistribution Workflow
**Endpoint**: `POST /api/v1/orchestration/redistribute-users`

**Triggers**:
- Gate utilization exceeds threshold (default 75%)
- Preference-based matching
- Load balancing across gates

**Request**:
```json
{
  "utilization_threshold": 75,
  "max_users_to_move": 50,
  "prefer_preferences": true
}
```

**Response**:
```json
{
  "reassignments_made": 42,
  "users_affected": 42,
  "redistribution_summary": {
    "Gate-A": {
      "before_utilization": 85.5,
      "after_utilization": 72.3,
      "users_moved_out": 35,
      "users_moved_in": 5
    }
  },
  "notifications_sent": 42,
  "timestamp": "2024-12-20T14:45:00"
}
```

### 4. Emergency Evacuation Workflow
**Endpoint**: `POST /api/v1/orchestration/evacuation`

**Flow**:
```
Emergency Trigger
    ↓
Get Affected Users
    ↓
Determine Safe Exits
    ↓
Assign Destination Gates
    ↓
Reassign Users
    ↓
Send Critical Alerts
    ↓
Notify Staff
```

**Request**:
```json
{
  "location": "Gate-A",
  "emergency_type": "FIRE_ALARM",
  "target_gates": ["Gate-D", "Gate-E"]
}
```

**Response**:
```json
{
  "users_evacuated": 1250,
  "evacuation_id": "evac-uuid",
  "affected_users": [
    {
      "user_id": "uuid",
      "ticket_id": "uuid",
      "previous_gate": "Gate-A",
      "new_gate": "Gate-D",
      "reassignment_type": "EMERGENCY_EVACUATION"
    }
  ],
  "notifications_sent": 1250,
  "emergency_id": "emerg-uuid",
  "status": "COMPLETED"
}
```

### 5. Food Ordering Orchestration
**Endpoint**: `POST /api/v1/orchestration/food-ordering/{user_id}`

**Flow**:
```
Order Placement
    ↓
Booth Allocation
    ↓
Assess Crowd Level
    ↓
Queue Management
    ↓
Send Preparation Notification
```

**Request**:
```json
{
  "items": [
    {
      "item_id": "item-1",
      "quantity": 2
    },
    {
      "item_id": "item-3",
      "quantity": 1
    }
  ]
}
```

**Response**:
```json
{
  "order_id": "order-uuid",
  "booth_id": "booth-1",
  "estimated_prep_time_minutes": 15,
  "pickup_time": "2024-12-20T15:15:00",
  "booth_crowd_level": "MEDIUM",
  "user_notifications_sent": ["order_placed", "estimated_ready_time"],
  "workflow_steps": {
    "food_order_created": "COMPLETED",
    "booth_allocated": "COMPLETED",
    "crowd_sync": "COMPLETED",
    "notification_sent": "COMPLETED"
  },
  "status": "PREPARED"
}
```

### 6. Emergency SOS Response Workflow
**Endpoint**: `POST /api/v1/orchestration/emergency-sos/{user_id}`

**Flow**:
```
Emergency Trigger
    ↓
Compute Exit Routes
    ↓
Assign Staff
    ↓
Get Affected Users
    ↓
Send Multi-channel Alerts
    ↓
Track Response
```

**Request**:
```json
{
  "emergency_type": "MEDICAL_EMERGENCY",
  "location": "Section-B2",
  "description": "User collapsed, requires immediate assistance"
}
```

**Response**:
```json
{
  "emergency_id": "emerg-uuid",
  "status": "responding",
  "staff_assigned": "staff-uuid",
  "nearest_exit": "Exit-5",
  "exit_distance_meters": 45,
  "affected_users_count": 250,
  "notifications_sent": {
    "critical_alerts": 250,
    "staff_alerts": 1,
    "adjacent_gates": 167
  },
  "workflow_steps": {
    "emergency_created": "COMPLETED",
    "staff_assigned": "COMPLETED",
    "notifications_sent": "COMPLETED",
    "evacuation_routes_computed": "COMPLETED"
  },
  "evacuation_plan": {
    "primary_exit": "Exit-5",
    "secondary_exits": ["Exit-4", "Exit-6"],
    "route_distances": {
      "Exit-5": 45,
      "Exit-4": 62,
      "Exit-6": 58
    }
  },
  "timestamp": "2024-12-20T15:30:00"
}
```

## System Operations

### System Synchronization
**Endpoint**: `POST /api/v1/orchestration/sync-all-systems`

Forces real-time synchronization across all modules:
- Crowd service ↔ Gate service
- Reassignment service
- Food service queues
- Emergency service

**Response**:
```json
{
  "sync_timestamp": "2024-12-20T15:45:00",
  "modules_synced": [
    "crowd_service",
    "reassignment_service",
    "food_service"
  ],
  "sync_results": {
    "crowd_service": {
      "status": "SYNCED",
      "gates_updated": 12
    },
    "reassignment_service": {
      "status": "SYNCED",
      "reassignments_made": 25
    },
    "food_service": {
      "status": "SYNCED",
      "orders_processed": 87
    }
  },
  "total_events_processed": 1250
}
```

### System Health
**Endpoint**: `GET /api/v1/orchestration/system-health`

Returns real-time health status of all modules:

**Response**:
```json
{
  "overall_status": "HEALTHY",
  "timestamp": "2024-12-20T15:50:00",
  "modules": {
    "user_service": {
      "status": "HEALTHY",
      "details": {"users_count": 5000}
    },
    "ticket_service": {
      "status": "HEALTHY",
      "details": {"active_tickets": 4850}
    },
    "gate_service": {
      "status": "HEALTHY",
      "details": {"gates_operational": 12}
    },
    "crowd_service": {
      "status": "HEALTHY",
      "details": {"avg_utilization": 68.5}
    },
    "food_service": {
      "status": "HEALTHY",
      "details": {"pending_orders": 120}
    },
    "emergency_service": {
      "status": "HEALTHY",
      "details": {"active_emergencies": 0}
    },
    "notification_service": {
      "status": "HEALTHY",
      "details": {"pending_notifications": 25}
    }
  }
}
```

**Status Levels**:
- ✅ **HEALTHY**: All systems operating normally
- ⚠️ **DEGRADED**: 1-2 modules experiencing issues
- 🔴 **CRITICAL**: 3+ modules affected or critical failures

## Analytics & Monitoring

### Event Log
**Endpoint**: `GET /api/v1/orchestration/event-log`

**Query Parameters**:
- `event_type`: Filter by event type
- `limit`: Max results (default 500)
- `skip`: Pagination offset

**Response**:
```json
{
  "total_events": 2500,
  "events": [
    {
      "event_id": "evt-uuid",
      "timestamp": "2024-12-20T15:45:00",
      "event_type": "EMERGENCY_SOS_ORCHESTRATED",
      "source_module": "orchestration_service",
      "trigger": "MEDICAL_EMERGENCY at Section-B2",
      "affected_users": 250,
      "notifications_triggered": ["EMERGENCY"],
      "status": "COMPLETED"
    }
  ],
  "event_type_summary": {
    "USER_JOURNEY_STARTED": 5000,
    "USER_REDISTRIBUTION_ORCHESTRATED": 42,
    "EVACUATION_ORCHESTRATED": 2,
    "FOOD_ORDER_ORCHESTRATED": 875,
    "EMERGENCY_SOS_ORCHESTRATED": 15
  }
}
```

### Journey Analytics
**Endpoint**: `GET /api/v1/orchestration/journey-analytics`

**Query Parameters**:
- `time_window`: `1h`, `6h`, `24h`, or `7d`

**Response**:
```json
{
  "total_users_today": 5000,
  "average_entry_time_minutes": 18,
  "users_reassigned": 150,
  "reassignment_rate_percent": 12.5,
  "reasons_for_reassignment": {
    "congestion": 95,
    "preference": 45,
    "user_request": 10
  },
  "average_journey_satisfaction": 4.6,
  "food_orders_placed": 420,
  "emergencies_responded": 2,
  "notifications_sent": 8750,
  "timestamp": "2024-12-20T16:00:00"
}
```

## Event Types

### Workflow Events
- `USER_JOURNEY_STARTED` - User registration & booking complete
- `USER_REDISTRIBUTION_ORCHESTRATED` - Load balancing executed
- `EVACUATION_ORCHESTRATED` - Emergency evacuation completed
- `FOOD_ORDER_ORCHESTRATED` - Food order workflow completed
- `EMERGENCY_SOS_ORCHESTRATED` - Emergency response activated

### Module Sync Events
- `CROWD_SERVICE_SYNCED` - Crowd levels synchronized
- `FOOD_SERVICE_SYNCED` - Order queues synchronized
- `NOTIFICATION_QUEUE_PROCESSED` - Notifications sent

## Error Handling

### Common Errors

| Error | Status | Resolution |
|-------|--------|-----------|
| User not found | 404 | Register user first |
| Gate capacity exceeded | 400 | Trigger redistribution |
| Food booth closed | 503 | Try different booth/time |
| Emergency service unavailable | 503 | Fallback to manual response |
| Notification delivery failed | 202 | Retry with exponential backoff |

## Integration Points

### With User Service
- User registration & profile updates
- Authentication for journey access

### With Ticket Service
- Ticket booking coordination
- Entry time computation

### With Gate Service
- Gate assignment with preferences
- Capacity monitoring
- Utilization tracking

### With Crowd Service
- Real-time density updates
- Entry time estimation
- Congestion detection

### With Food Service
- Order placement
- Booth allocation
- Queue management

### With Emergency Service
- Emergency detection
- Exit route computation
- Staff assignment
- Response tracking

### With Notification Service
- Multi-channel notifications
- Priority-based delivery
- Retry logic

### With Staff Dashboard
- Workload tracking
- Resource allocation
- Performance monitoring

## Best Practices

1. **Always use orchestration endpoints for complex workflows** - Don't call individual services directly for multi-step operations

2. **Monitor event log regularly** - Catch systemic issues early

3. **Set up alerts for**:
   - System health degradation
   - High emergency rates
   - Gate overcrowding
   - Food queue backlogs

4. **Batch operations when possible** - Use redistribution endpoint instead of individual reassignments

5. **Test failover scenarios** - Ensure emergency workflows work without dependent services

6. **Rate limit orchestration endpoints** - Prevent cascade failures from massive request spikes

## Performance Metrics

### Expected Latencies (P95)

| Endpoint | Latency |
|----------|---------|
| Register & Book | 800ms |
| Get User Journey | 200ms |
| Redistribute Users | 2s |
| Emergency Evacuation | 500ms |
| Food Ordering | 1s |
| Emergency SOS | 300ms |
| System Health | 150ms |

### Throughput

- Register: 100 users/second
- Redistribution: Batch process 500 users
- Emergency SOS: 50 incidents/second
- Food Orders: 200 orders/minute
- Notifications: 5,000/second

## Future Enhancements

1. **Predictive Orchestration** - Use ML to predict bottlenecks
2. **Multi-event Aggregation** - Combine related events
3. **Workflow Simulation** - Test impact of decisions
4. **Custom Workflows** - Allow dynamic orchestration rules
5. **Distributed Tracing** - Full request visibility across services
6. **Machine Learning Integration** - Optimize resource allocation
7. **Real-time Analytics Dashboard** - Live event stream visualization
