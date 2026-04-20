# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.staff_dashboard import (
    GateManagementRequest, GateCloseRequest, GateCapacityOverrideRequest,
    ManualReassignmentRequest, EmergencyResponseRequest, EmergencyStatusUpdateRequest,
    NotificationAcknowledgmentRequest
)
from app.services.staff_dashboard_service import StaffDashboardService

router = APIRouter(prefix="/staff", tags=["staff-dashboard"])


# ============================================================================
# READ-ONLY ENDPOINTS (Monitoring & Reporting)
# ============================================================================

@router.get(
    "/dashboard/summary",
    summary="Get system status summary",
    description="Get high-level control room overview of system status"
)
async def get_dashboard_summary():
    """
    Get overall system status summary for control room
    
    Returns:
    - Total gates and users
    - Average gate utilization
    - Active emergencies count
    - System health status
    """
    try:
        summary = StaffDashboardService.get_dashboard_summary()
        return summary.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/gates",
    summary="Get all gates dashboard",
    description="Get real-time status and capacity for all gates"
)
async def get_gates_dashboard():
    """
    Get dashboard view for all gates
    
    Returns:
    - Real-time occupancy and utilization
    - Entry time estimates
    - Crowding levels
    - Recent events
    """
    try:
        gates = StaffDashboardService.get_gates_dashboard()
        return {
            "gates": [g.dict() for g in gates],
            "total_capacity": sum(g.capacity for g in gates),
            "total_occupancy": sum(g.current_occupancy for g in gates),
            "average_utilization": round(sum(g.utilization_percent for g in gates) / len(gates), 1) if gates else 0,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/crowd/{location}",
    summary="Get detailed crowd analysis",
    description="Get crowd metrics and trends for specific location"
)
async def get_crowd_analysis(
    location: str,
    include_history: bool = Query(False, description="Include historical data"),
    time_window: Optional[str] = Query(None, description="Time window: 1h, 24h, 7d")
):
    """
    Get detailed crowd analysis for a location
    
    - **location**: Gate location (e.g., gate_a, gate_b)
    - **include_history**: Include hourly trend data
    - **time_window**: Historical data time window
    
    Returns:
    - Current occupancy and capacity
    - Arrival/departure rates
    - Recommendations for crowd management
    - Historical trend data (optional)
    """
    try:
        analysis = StaffDashboardService.get_crowd_analysis(location, include_history)
        return analysis.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/emergencies",
    summary="Get active emergencies",
    description="Get list of all active emergencies with staff assignments"
)
async def get_active_emergencies(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get active emergencies on dashboard
    
    - **priority**: Filter by CRITICAL, HIGH, MEDIUM, LOW
    - **status**: Filter by reported, responding, resolved
    
    Returns:
    - List of active emergencies
    - Priority and status counts
    - Assigned staff members
    - Location and exit guidance
    """
    try:
        emergencies = StaffDashboardService.get_active_emergencies(priority, status)
        return {
            "active_emergencies": emergencies,
            "total_active": len(emergencies),
            "critical_count": sum(1 for e in emergencies if e["priority"] == "CRITICAL"),
            "high_count": sum(1 for e in emergencies if e["priority"] == "HIGH"),
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/food-orders",
    summary="Get food ordering status",
    description="Get overview of food ordering system and booth status"
)
async def get_food_order_status(
    booth_id: Optional[str] = Query(None, description="Filter by booth"),
    status_filter: Optional[str] = Query(None, description="Filter by order status")
):
    """
    Get food ordering system dashboard
    
    - **booth_id**: Optional filter for specific booth
    - **status_filter**: Filter by placed, preparing, ready, pickup
    
    Returns:
    - Total orders and pending count
    - Booth status and queue lengths
    - Ready orders count
    - System recommendations
    """
    try:
        food_status = StaffDashboardService.get_food_order_status()
        return food_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/notifications",
    summary="Get notification queue",
    description="Get active notifications for monitoring and acknowledgment"
)
async def get_notifications_queue(
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Get notification queue dashboard
    
    - **priority**: Optional filter by CRITICAL, HIGH, MEDIUM, LOW
    
    Returns:
    - Active notifications list
    - Priority breakdown
    - Unacknowledged count
    - Recent alerts
    """
    try:
        notifs = StaffDashboardService.get_notifications_queue(priority)
        return notifs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dashboard/tickets-by-gate/{gate_id}",
    summary="Get users by gate",
    description="Get all users assigned to a specific gate"
)
async def get_tickets_by_gate(gate_id: str):
    """
    Get list of all tickets/users assigned to a gate
    
    - **gate_id**: Gate identifier (A, B, C, D)
    
    Returns:
    - List of assigned tickets with user details
    - Entry times and preferences
    - Parking requirements
    """
    try:
        tickets = StaffDashboardService.get_tickets_by_gate(gate_id)
        return {
            "gate_id": gate_id,
            "total_tickets": len(tickets),
            "tickets": tickets,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WRITE ENDPOINTS (Staff Control Actions)
# ============================================================================

@router.put(
    "/gates/{gate_id}/open",
    status_code=200,
    summary="Open a gate",
    description="Staff action to operationally open a gate"
)
async def open_gate(gate_id: str, request: GateManagementRequest):
    """
    Open a gate for operations
    
    - **gate_id**: Gate to open (A, B, C, D)
    - **reason**: Reason for opening gate
    - **staff_id**: Staff member performing action
    - **notes**: Optional additional notes
    """
    try:
        result = StaffDashboardService.open_gate(
            gate_id=gate_id,
            staff_id=request.staff_id,
            reason=request.reason,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/gates/{gate_id}/close",
    status_code=200,
    summary="Close a gate",
    description="Staff action to close a gate and handle affected users"
)
async def close_gate(gate_id: str, request: GateCloseRequest):
    """
    Close a gate with automatic user handling
    
    - **gate_id**: Gate to close (A, B, C, D)
    - **reason**: Reason for closing
    - **staff_id**: Staff member performing action
    - **affected_users_action**: How to handle users (reassign_to_nearest, hold, redirect)
    - **estimated_reopening_minutes**: Expected reopening time
    """
    try:
        result = StaffDashboardService.close_gate(
            gate_id=gate_id,
            staff_id=request.staff_id,
            reason=request.reason,
            estimated_reopening_minutes=request.estimated_reopening_minutes,
            affected_users_action=request.affected_users_action,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/gates/{gate_id}/capacity-override",
    status_code=200,
    summary="Override gate capacity",
    description="Temporarily increase gate capacity for emergency"
)
async def override_gate_capacity(gate_id: str, request: GateCapacityOverrideRequest):
    """
    Override gate capacity temporarily (emergency situations)
    
    - **gate_id**: Gate to override
    - **new_capacity**: Temporary capacity limit
    - **duration_minutes**: How long override is active
    - **reason**: Reason for override
    - **staff_id**: Staff member performing action
    """
    try:
        result = StaffDashboardService.override_gate_capacity(
            gate_id=gate_id,
            new_capacity=request.new_capacity,
            duration_minutes=request.duration_minutes,
            staff_id=request.staff_id,
            reason=request.reason,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/reassign-user",
    status_code=200,
    summary="Manually reassign user",
    description="Staff override to reassign user to different gate"
)
async def manual_reassignment(request: ManualReassignmentRequest):
    """
    Manually reassign a user to a different gate
    
    - **ticket_id**: User's ticket ID to reassign
    - **new_gate_id**: Destination gate
    - **reason**: Reason for reassignment
    - **staff_id**: Staff member performing action
    """
    try:
        result = StaffDashboardService.manual_reassignment(
            ticket_id=request.ticket_id,
            new_gate_id=request.new_gate_id,
            staff_id=request.staff_id,
            reason=request.reason,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/emergency/respond",
    status_code=200,
    summary="Respond to emergency",
    description="Staff claim and begin responding to emergency"
)
async def respond_to_emergency(request: EmergencyResponseRequest):
    """
    Begin emergency response as staff member
    
    - **emergency_id**: Emergency to respond to
    - **staff_id**: Responding staff member
    - **response_type**: immediate, scheduled, or monitoring
    - **initial_notes**: Initial assessment notes
    """
    try:
        result = StaffDashboardService.respond_to_emergency(
            emergency_id=request.emergency_id,
            staff_id=request.staff_id,
            response_type=request.response_type,
            initial_notes=request.initial_notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/emergency/{emergency_id}/status",
    status_code=200,
    summary="Update emergency status",
    description="Update emergency status from responding to resolved"
)
async def update_emergency_status(emergency_id: str, request: EmergencyStatusUpdateRequest):
    """
    Update emergency status during response
    
    - **emergency_id**: Emergency to update
    - **new_status**: reported, responding, resolved, escalated
    - **staff_id**: Staff member updating status
    - **resolution_notes**: Details about resolution
    - **evacuation_required**: Whether evacuation is needed
    """
    try:
        result = StaffDashboardService.update_emergency_status(
            emergency_id=emergency_id,
            new_status=request.new_status,
            staff_id=request.staff_id,
            resolution_notes=request.resolution_notes,
            evacuation_required=request.evacuation_required or False
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/notification/{notification_id}/acknowledge",
    status_code=200,
    summary="Acknowledge notification",
    description="Staff acknowledge receipt of notification and action taken"
)
async def acknowledge_notification(notification_id: str, request: NotificationAcknowledgmentRequest):
    """
    Acknowledge and mark notification as handled
    
    - **notification_id**: Notification to acknowledge
    - **staff_id**: Acknowledging staff member
    - **action_taken**: What action was taken in response
    - **notes**: Additional notes
    """
    try:
        result = StaffDashboardService.acknowledge_notification(
            notification_id=notification_id,
            staff_id=request.staff_id,
            action_taken=request.action_taken,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/actions/history",
    summary="Get action audit trail",
    description="View staff action history for auditing and analytics"
)
async def get_action_history(
    staff_id: Optional[str] = Query(None, description="Filter by staff member"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    hours: int = Query(24, ge=1, description="Hours of history to show")
):
    """
    Get staff action history for auditing
    
    - **staff_id**: Optional filter for specific staff member
    - **action_type**: Filter by gate_open, gate_close, reassignment, emergency_response
    - **limit**: Max results (default 100)
    - **skip**: Pagination offset
    - **hours**: How many hours of history to show (default 24)
    
    Returns:
    - Chronological list of staff actions
    - Total count for pagination
    - Summary of staff workload
    """
    try:
        actions, total_count = StaffDashboardService.get_action_history(
            staff_id=staff_id,
            action_type=action_type,
            limit=limit,
            skip=skip,
            hours=hours
        )
        
        # Count actions per staff
        from collections import Counter
        staff_action_counts = Counter(a.staff_id for a in actions) if actions else {}
        
        return {
            "actions": [a.dict() for a in actions],
            "total_count": total_count,
            "staff_action_counts": dict(staff_action_counts),
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total": total_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/workload",
    summary="Get staff workload metrics",
    description="View active staff workload and performance metrics"
)
async def get_staff_workload():
    """
    Get staff workload and performance dashboard
    
    Returns:
    - Active staff count
    - Individual staff metrics (workload %, active tasks)
    - Workload distribution
    - Pending critical alerts
    """
    try:
        workload = StaffDashboardService.get_staff_workload()
        return workload.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
