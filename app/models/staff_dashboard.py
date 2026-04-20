# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from uuid import UUID
from datetime import datetime


class GateSummary(BaseModel):
    """Real-time gate status for dashboard"""
    gate_id: str = Field(..., description="Gate identifier")
    capacity: int = Field(..., description="Total capacity of gate")
    current_occupancy: int = Field(..., description="Current number of people")
    utilization_percent: float = Field(..., description="Percentage of capacity used")
    entry_time_minutes: int = Field(..., description="Estimated entry time in minutes")
    status: Literal["OPERATIONAL", "CLOSED", "MAINTENANCE"] = Field(
        default="OPERATIONAL", description="Current gate status"
    )
    crowding_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="Crowding assessment"
    )
    recent_events: List[str] = Field(default_factory=list, description="Recent gate events")

    class Config:
        json_schema_extra = {
            "example": {
                "gate_id": "A",
                "capacity": 100,
                "current_occupancy": 67,
                "utilization_percent": 67.0,
                "entry_time_minutes": 20,
                "status": "OPERATIONAL",
                "crowding_level": "MEDIUM",
                "recent_events": ["Gate reassignment triggered at 11:20", "3 users reassigned at 11:15"]
            }
        }


class ControlRoomSummary(BaseModel):
    """High-level system status summary"""
    timestamp: datetime = Field(..., description="Summary timestamp")
    total_gates: int = Field(..., description="Total gates in stadium")
    total_users_in_stadium: int = Field(..., description="Total users currently inside")
    average_gate_utilization: float = Field(..., description="Average utilization across gates")
    total_active_emergencies: int = Field(..., description="Total active emergencies")
    critical_emergencies: int = Field(..., description="Count of CRITICAL priority emergencies")
    pending_notifications: int = Field(..., description="Unacknowledged notifications")
    food_orders_pending: int = Field(..., description="Food orders awaiting pickup")
    gate_status: Literal["OPERATIONAL", "DEGRADED", "CRITICAL"] = Field(
        ..., description="Overall gate system health"
    )
    system_status: Literal["HEALTHY", "WARNING", "CRITICAL"] = Field(
        ..., description="Overall system health"
    )

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class CrowdAnalysis(BaseModel):
    """Detailed crowd metrics with recommendations"""
    location: str = Field(..., description="Gate/zone location")
    current_occupancy: int = Field(..., description="Current occupancy")
    capacity: int = Field(..., description="Maximum capacity")
    utilization_percent: float = Field(..., description="Percentage utilized")
    crowding_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    entry_time_minutes: int = Field(..., description="Estimated entry time")
    peak_time: Optional[str] = Field(None, description="Timestamp of peak occupancy")
    arrival_rate: float = Field(..., description="People per minute arriving")
    departure_rate: float = Field(..., description="People per minute departing")
    net_change: float = Field(..., description="Net change per minute")
    recommendations: List[str] = Field(default_factory=list, description="Staff recommendations")
    history: List[Dict] = Field(default_factory=list, description="Historical occupancy")

    class Config:
        json_schema_extra = {
            "example": {
                "location": "gate_a",
                "current_occupancy": 67,
                "capacity": 100,
                "utilization_percent": 67.0,
                "crowding_level": "MEDIUM",
                "entry_time_minutes": 20,
                "peak_time": "11:15",
                "arrival_rate": 5.2,
                "departure_rate": 3.8,
                "net_change": 1.4,
                "recommendations": [
                    "Consider opening alternate gates",
                    "Current entry time acceptable"
                ]
            }
        }


class GateManagementRequest(BaseModel):
    """Request to manage gate operations"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for action")
    staff_id: str = Field(..., min_length=1, max_length=50, description="Staff member ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Redistribute crowd flow",
                "staff_id": "staff-01",
                "notes": "Opening Gate C to balance with Gate A"
            }
        }


class GateCloseRequest(GateManagementRequest):
    """Request to close a gate"""
    estimated_reopening_minutes: Optional[int] = Field(
        None, ge=0, le=480, description="Estimated minutes until reopening"
    )
    affected_users_action: Literal["reassign_to_nearest", "hold", "redirect"] = Field(
        default="reassign_to_nearest", description="How to handle affected users"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Maintenance required",
                "staff_id": "staff-01",
                "estimated_reopening_minutes": 30,
                "affected_users_action": "reassign_to_nearest"
            }
        }


class GateCapacityOverrideRequest(GateManagementRequest):
    """Request to override gate capacity"""
    new_capacity: int = Field(..., gt=0, description="New temporary capacity")
    duration_minutes: int = Field(15, ge=1, le=480, description="Duration of override")

    class Config:
        json_schema_extra = {
            "example": {
                "new_capacity": 120,
                "reason": "Emergency evacuation capacity",
                "staff_id": "staff-01",
                "duration_minutes": 15
            }
        }


class GateActionResponse(BaseModel):
    """Response from gate management action"""
    gate_id: str = Field(..., description="Gate ID")
    action: Literal["OPENED", "CLOSED", "CAPACITY_OVERRIDE"] = Field(..., description="Action taken")
    previous_status: Optional[str] = Field(None, description="Previous gate status")
    new_status: str = Field(..., description="New gate status")
    affected_users: Optional[int] = Field(None, description="Number of affected users")
    users_reassigned: Optional[int] = Field(None, description="Number of reassigned users")
    action_timestamp: datetime = Field(..., description="When action was taken")
    staff_id: str = Field(..., description="Staff who performed action")
    reason: Optional[str] = Field(None, description="Reason for action")

    class Config:
        json_schema_extra = {
            "example": {
                "gate_id": "C",
                "action": "OPENED",
                "previous_status": "CLOSED",
                "new_status": "OPERATIONAL",
                "action_timestamp": "2024-03-15T11:30:30Z",
                "staff_id": "staff-01",
                "reason": "Redistribute crowd flow"
            }
        }


class ManualReassignmentRequest(BaseModel):
    """Request to manually reassign a user"""
    ticket_id: str = Field(..., description="Ticket ID to reassign")
    new_gate_id: str = Field(..., description="New gate ID")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for reassignment")
    staff_id: str = Field(..., min_length=1, max_length=50, description="Staff member ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "ticket-xxx",
                "new_gate_id": "C",
                "reason": "Crowd management - user opted for less crowded gate",
                "staff_id": "staff-01"
            }
        }


class StaffReassignmentResponse(BaseModel):
    """Response from manual reassignment"""
    ticket_id: str = Field(..., description="Ticket ID")
    user_id: UUID = Field(..., description="User ID")
    previous_gate: str = Field(..., description="Previous gate")
    new_gate: str = Field(..., description="New gate")
    reassignment_type: Literal["MANUAL", "AUTOMATIC"] = Field(
        ..., description="Type of reassignment"
    )
    reassignment_timestamp: datetime = Field(..., description="When reassignment occurred")
    staff_id: str = Field(..., description="Staff who performed reassignment")
    reason: str = Field(..., description="Reason for reassignment")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "ticket-xxx",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "previous_gate": "A",
                "new_gate": "C",
                "reassignment_type": "MANUAL",
                "reassignment_timestamp": "2024-03-15T11:30:30Z",
                "staff_id": "staff-01",
                "reason": "Crowd management"
            }
        }


class EmergencyResponseRequest(BaseModel):
    """Request to respond to emergency"""
    emergency_id: str = Field(..., description="Emergency ID")
    staff_id: str = Field(..., min_length=1, max_length=50, description="Responding staff ID")
    response_type: Literal["immediate", "scheduled", "monitoring"] = Field(
        default="immediate", description="Type of response"
    )
    initial_notes: Optional[str] = Field(None, max_length=1000, description="Initial response notes")

    class Config:
        json_schema_extra = {
            "example": {
                "emergency_id": "emerg-12345",
                "staff_id": "staff-01",
                "response_type": "immediate",
                "initial_notes": "Crowd dispersal in progress"
            }
        }


class EmergencyResponseAction(BaseModel):
    """Response from emergency response action"""
    emergency_id: str = Field(..., description="Emergency ID")
    staff_id: str = Field(..., description="Responding staff ID")
    status: Literal["reported", "responding", "resolved"] = Field(..., description="Emergency status")
    response_time_seconds: int = Field(..., description="Time from report to response")
    initial_notes: Optional[str] = Field(None, description="Response notes")
    timestamp: datetime = Field(..., description="Action timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "emergency_id": "emerg-12345",
                "staff_id": "staff-01",
                "status": "responding",
                "response_time_seconds": 45,
                "initial_notes": "Crowd dispersal in progress",
                "timestamp": "2024-03-15T11:30:30Z"
            }
        }


class EmergencyStatusUpdateRequest(BaseModel):
    """Request to update emergency status"""
    new_status: Literal["reported", "responding", "resolved", "escalated"] = Field(
        ..., description="New emergency status"
    )
    staff_id: str = Field(..., min_length=1, max_length=50, description="Staff member ID")
    resolution_notes: Optional[str] = Field(None, max_length=1000, description="Resolution details")
    evacuation_required: Optional[bool] = Field(None, description="Is evacuation needed")

    class Config:
        json_schema_extra = {
            "example": {
                "new_status": "resolved",
                "staff_id": "staff-01",
                "resolution_notes": "Crowd redirected, no injuries",
                "evacuation_required": False
            }
        }


class NotificationAcknowledgmentRequest(BaseModel):
    """Request to acknowledge notification"""
    staff_id: str = Field(..., min_length=1, max_length=50, description="Acknowledging staff ID")
    action_taken: Optional[str] = Field(None, max_length=500, description="Action taken in response")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "staff_id": "staff-01",
                "action_taken": "reassigned_2_users_to_gate_c",
                "notes": "Coordinated with gate staff"
            }
        }


class StaffActionLog(BaseModel):
    """Audit log entry for staff action"""
    action_id: str = Field(..., description="Unique action ID")
    timestamp: datetime = Field(..., description="When action occurred")
    staff_id: str = Field(..., description="Staff member ID")
    action_type: Literal[
        "gate_open", "gate_close", "capacity_override", "reassignment",
        "emergency_response", "notification_acknowledged"
    ] = Field(..., description="Type of action")
    related_entity_id: Optional[str] = Field(None, description="Related entity (gate, ticket, etc.)")
    reason: Optional[str] = Field(None, description="Reason for action")
    affected_users: Optional[int] = Field(None, description="Number of users affected")
    duration_seconds: Optional[int] = Field(None, description="How long action was active")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "action_id": "act-xxx",
                "timestamp": "2024-03-15T11:30:30Z",
                "staff_id": "staff-01",
                "action_type": "gate_close",
                "related_entity_id": "B",
                "reason": "Maintenance",
                "affected_users": 23,
                "duration_seconds": 300
            }
        }


class StaffWorkloadMetrics(BaseModel):
    """Individual staff member workload"""
    staff_id: str = Field(..., description="Staff member ID")
    status: Literal["ACTIVE", "BREAK", "OFFLINE"] = Field(..., description="Current status")
    assigned_zone: Optional[str] = Field(None, description="Zone assignment")
    active_emergencies: int = Field(default=0, description="Number of active emergencies")
    actions_today: int = Field(default=0, description="Actions performed today")
    last_action: Optional[datetime] = Field(None, description="Timestamp of last action")
    response_time_average_seconds: float = Field(
        default=0, description="Average response time to emergencies"
    )
    workload_percent: float = Field(default=0, ge=0, le=100, description="Workload percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "staff_id": "staff-01",
                "status": "ACTIVE",
                "assigned_zone": "gates_a_b",
                "active_emergencies": 1,
                "actions_today": 23,
                "last_action": "2024-03-15T11:30:30Z",
                "response_time_average_seconds": 45,
                "workload_percent": 75
            }
        }


class StaffWorkloadResponse(BaseModel):
    """Overall staff workload summary"""
    active_staff: int = Field(..., description="Number of active staff members")
    staff_members: List[StaffWorkloadMetrics] = Field(..., description="Individual staff details")
    total_workload_percent: float = Field(..., ge=0, le=100, description="Overall team workload")
    critical_alerts_pending: int = Field(..., description="Unresolved critical alerts")
    timestamp: datetime = Field(..., description="Summary timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "active_staff": 3,
                "staff_members": [
                    {
                        "staff_id": "staff-01",
                        "status": "ACTIVE",
                        "assigned_zone": "gates_a_b",
                        "active_emergencies": 1,
                        "actions_today": 23,
                        "workload_percent": 75
                    }
                ],
                "total_workload_percent": 68,
                "critical_alerts_pending": 2,
                "timestamp": "2024-03-15T11:30:00Z"
            }
        }
