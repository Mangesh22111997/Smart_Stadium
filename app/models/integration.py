"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Literal
from uuid import UUID
from datetime import datetime


class RegisterAndBookRequest(BaseModel):
    """Request to register user and book ticket in single workflow"""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=100, description="User full name")
    phone: str = Field(..., description="User phone number")
    commute_mode: Literal["CAR", "TRAIN", "BUS", "WALK"] = Field(
        ..., description="Preferred commute mode"
    )
    parking_required: bool = Field(default=False, description="Whether parking is needed")
    event_date: str = Field(..., description="Event date (YYYY-MM-DD)")
    arrival_time: datetime = Field(..., description="Planned arrival time")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "full_name": "John Doe",
                "phone": "9876543210",
                "commute_mode": "CAR",
                "parking_required": True,
                "event_date": "2024-03-15",
                "arrival_time": "2024-03-15T10:00:00Z"
            }
        }


class WorkflowStepStatus(BaseModel):
    """Status of a single workflow step"""
    step_name: str = Field(..., description="Name of step")
    status: Literal["COMPLETED", "FAILED", "PENDING", "SKIPPED"] = Field(
        ..., description="Step status"
    )
    timestamp: Optional[datetime] = Field(None, description="When step completed")
    error_message: Optional[str] = Field(None, description="Error if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "step_name": "user_registration",
                "status": "COMPLETED",
                "timestamp": "2024-03-15T09:30:00Z"
            }
        }


class RegisterAndBookResponse(BaseModel):
    """Response from register + book workflow"""
    user_id: UUID = Field(..., description="New user UUID")
    ticket_id: str = Field(..., description="New ticket ID")
    assigned_gate: str = Field(..., description="Assigned gate")
    entry_time_minutes: int = Field(..., description="Estimated entry time in minutes")
    notifications_sent: List[str] = Field(..., description="Notifications triggered")
    status: Literal["READY_TO_ENTER", "WAITING", "ERROR"] = Field(..., description="Journey status")
    journey_id: str = Field(..., description="Journey tracking ID")
    workflow_steps: Dict[str, str] = Field(..., description="Status of each workflow step")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "ticket_id": "ticket-xxx",
                "assigned_gate": "A",
                "entry_time_minutes": 15,
                "notifications_sent": ["GATE_ASSIGNMENT"],
                "status": "READY_TO_ENTER",
                "journey_id": "journey-xxx",
                "workflow_steps": {
                    "user_registration": "COMPLETED",
                    "ticket_booking": "COMPLETED",
                    "gate_assignment": "COMPLETED"
                }
            }
        }


class UserJourneyEvent(BaseModel):
    """Single event in user's journey"""
    timestamp: datetime = Field(..., description="When event occurred")
    event_type: str = Field(..., description="Type of event")
    details: str = Field(..., description="Event details")
    related_entity_id: Optional[str] = Field(None, description="Related entity ID")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-03-15T09:30:00Z",
                "event_type": "USER_REGISTERED",
                "details": "User account created"
            }
        }


class FoodOrderSummary(BaseModel):
    """Summary of user's food order"""
    order_id: str = Field(..., description="Order ID")
    items: List[str] = Field(..., description="Item descriptions")
    status: Literal["placed", "preparing", "ready", "pickup", "completed"] = Field(
        ..., description="Order status"
    )
    booth_id: Optional[str] = Field(None, description="Booth location")
    estimated_ready_time: Optional[datetime] = Field(None, description="When order will be ready")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "order-xxx",
                "items": ["Margherita Pizza"],
                "status": "ready",
                "booth_id": "B03",
                "estimated_ready_time": "2024-03-15T11:00:00Z"
            }
        }


class UserJourneyResponse(BaseModel):
    """Complete user journey status and history"""
    user_id: UUID = Field(..., description="User UUID")
    full_name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    journey_status: Literal["STARTED", "IN_PROGRESS", "COMPLETED", "ERROR"] = Field(
        ..., description="Overall journey status"
    )
    current_gate: Optional[str] = Field(None, description="Currently assigned gate")
    current_utilization: Optional[str] = Field(None, description="Gate utilization")
    entry_time_estimate: Optional[str] = Field(None, description="Entry time estimate")
    events: List[UserJourneyEvent] = Field(..., description="Journey events")
    food_orders: List[FoodOrderSummary] = Field(default_factory=list, description="Food orders")
    active_emergencies: int = Field(default=0, description="Active emergencies affecting user")
    notifications_history: List[Dict] = Field(default_factory=list, description="Sent notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "John Doe",
                "email": "john@example.com",
                "journey_status": "IN_PROGRESS",
                "current_gate": "A",
                "current_utilization": "67%",
                "entry_time_estimate": "15 minutes",
                "events": [],
                "food_orders": [],
                "active_emergencies": 0
            }
        }


class ReassignmentRequest(BaseModel):
    """Request to check and redistribute users"""
    utilization_threshold: int = Field(
        default=75, ge=0, le=99, description="Threshold percentage for overcrowding"
    )
    max_users_to_move: int = Field(
        default=50, ge=1, le=1000, description="Maximum users to move in single pass"
    )
    prefer_preferences: bool = Field(
        default=True, description="Respect user preferences when reassigning"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "utilization_threshold": 75,
                "max_users_to_move": 50,
                "prefer_preferences": True
            }
        }


class GateRedistributionSummary(BaseModel):
    """Gate-level redistribution results"""
    gate_id: str = Field(..., description="Gate ID")
    before_utilization: float = Field(..., description="Utilization before redistribution")
    after_utilization: float = Field(..., description="Utilization after redistribution")
    users_moved_out: int = Field(..., description="Users moved from this gate")
    users_moved_in: int = Field(..., description="Users moved to this gate")

    class Config:
        json_schema_extra = {
            "example": {
                "gate_id": "A",
                "before_utilization": 89,
                "after_utilization": 78,
                "users_moved_out": 12,
                "users_moved_in": 0
            }
        }


class ReassignmentResponse(BaseModel):
    """Response from redistribution orchestration"""
    reassignments_made: int = Field(..., description="Total reassignments")
    users_affected: int = Field(..., description="Total users affected")
    redistribution_summary: Dict[str, Dict] = Field(..., description="Per-gate summary")
    notifications_sent: int = Field(..., description="Notifications sent")
    timestamp: datetime = Field(..., description="When redistribution occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "reassignments_made": 12,
                "users_affected": 12,
                "redistribution_summary": {},
                "notifications_sent": 12,
                "timestamp": "2024-03-15T10:45:00Z"
            }
        }


class EvacuationAffectedUser(BaseModel):
    """User affected by evacuation"""
    user_id: UUID = Field(..., description="User UUID")
    ticket_id: str = Field(..., description="Ticket ID")
    previous_gate: str = Field(..., description="Original gate")
    new_gate: str = Field(..., description="Evacuation gate")
    reassignment_type: Literal["EMERGENCY_EVACUATION"] = Field(
        ..., description="Type of reassignment"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "ticket_id": "ticket-xxx",
                "previous_gate": "A",
                "new_gate": "C",
                "reassignment_type": "EMERGENCY_EVACUATION"
            }
        }


class EvacuationRequest(BaseModel):
    """Request to orchestrate evacuation"""
    location: str = Field(..., description="Gate/location to evacuate")
    emergency_type: str = Field(..., description="Reason for evacuation")
    target_gates: Optional[List[str]] = Field(
        None, description="Specific gates to use (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "location": "gate_a",
                "emergency_type": "FIRE",
                "target_gates": ["C", "D"]
            }
        }


class EvacuationResponse(BaseModel):
    """Response from evacuation orchestration"""
    users_evacuated: int = Field(..., description="Users moved")
    evacuation_id: str = Field(..., description="Evacuation tracking ID")
    affected_users: List[EvacuationAffectedUser] = Field(..., description="Users moved")
    notifications_sent: int = Field(..., description="Notifications sent")
    emergency_id: str = Field(..., description="Related emergency ID")
    status: Literal["COMPLETED", "PARTIAL", "FAILED"] = Field(..., description="Evacuation status")
    timestamp: datetime = Field(..., description="When evacuation occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "users_evacuated": 67,
                "evacuation_id": "evac-xxx",
                "affected_users": [],
                "notifications_sent": 67,
                "emergency_id": "emerg-xxx",
                "status": "COMPLETED",
                "timestamp": "2024-03-15T10:45:00Z"
            }
        }


class FoodOrderingWorkflowRequest(BaseModel):
    """Request for food ordering workflow"""
    user_id: UUID = Field(..., description="User ordering food")
    items: List[Dict] = Field(..., description="Items to order ([{'item_id': '...', 'quantity': 1}])")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "items": [{"item_id": "pizza_margherita", "quantity": 1}]
            }
        }


class FoodOrderingWorkflowResponse(BaseModel):
    """Response from food ordering workflow"""
    order_id: str = Field(..., description="Order ID")
    booth_id: str = Field(..., description="Assigned booth")
    estimated_prep_time_minutes: int = Field(..., description="Time to prepare")
    pickup_time: datetime = Field(..., description="When order ready")
    booth_crowd_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="Booth crowd status"
    )
    user_notifications_sent: List[str] = Field(..., description="Notifications sent")
    workflow_steps: Dict[str, str] = Field(..., description="Step statuses")
    status: Literal["PREPARED", "FAILED", "PENDING"] = Field(..., description="Overall status")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "order-xxx",
                "booth_id": "B03",
                "estimated_prep_time_minutes": 15,
                "pickup_time": "2024-03-15T11:00:00Z",
                "booth_crowd_level": "MEDIUM",
                "user_notifications_sent": ["order_placed"],
                "workflow_steps": {},
                "status": "PREPARED"
            }
        }


class EmergencySOSWorkflowRequest(BaseModel):
    """Request for emergency SOS workflow"""
    user_id: UUID = Field(..., description="User reporting emergency")
    emergency_type: str = Field(..., description="Type of emergency")
    location: str = Field(..., description="Emergency location")
    description: str = Field(..., max_length=500, description="Emergency details")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "emergency_type": "CROWD_CRUSH",
                "location": "gate_b",
                "description": "Large crowd buildup"
            }
        }


class EvacuationPlan(BaseModel):
    """Evacuation route plan"""
    primary_exit: str = Field(..., description="Primary exit")
    secondary_exits: List[str] = Field(..., description="Backup exits")
    route_distances: Dict[str, int] = Field(..., description="Distance to each exit")

    class Config:
        json_schema_extra = {
            "example": {
                "primary_exit": "exit_2",
                "secondary_exits": ["exit_1", "exit_4"],
                "route_distances": {"exit_2": 60, "exit_1": 100}
            }
        }


class EmergencySOSWorkflowResponse(BaseModel):
    """Response from emergency SOS workflow"""
    emergency_id: str = Field(..., description="Emergency ID")
    status: Literal["reported", "responding", "resolved"] = Field(..., description="Status")
    staff_assigned: Optional[str] = Field(None, description="Assigned staff member")
    nearest_exit: str = Field(..., description="Nearest exit")
    exit_distance_meters: int = Field(..., description="Distance to exit")
    affected_users_count: int = Field(..., description="Users in area")
    notifications_sent: Dict[str, int] = Field(..., description="Notification counts by type")
    workflow_steps: Dict[str, str] = Field(..., description="Step statuses")
    evacuation_plan: EvacuationPlan = Field(..., description="Evacuation routes")
    timestamp: datetime = Field(..., description="When emergency occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "emergency_id": "emerg-xxx",
                "status": "responding",
                "staff_assigned": "staff-01",
                "nearest_exit": "exit_2",
                "exit_distance_meters": 60,
                "affected_users_count": 67,
                "notifications_sent": {"critical_alerts": 67},
                "workflow_steps": {},
                "evacuation_plan": {},
                "timestamp": "2024-03-15T10:45:00Z"
            }
        }


class SyncResult(BaseModel):
    """Result of syncing a single module"""
    module_name: str = Field(..., description="Module name")
    status: Literal["SYNCED", "ERROR", "SKIPPED"] = Field(..., description="Sync status")
    details: Dict = Field(default_factory=dict, description="Sync details")

    class Config:
        json_schema_extra = {
            "example": {
                "module_name": "crowd_service",
                "status": "SYNCED",
                "details": {"gates_updated": 4}
            }
        }


class SyncAllSystemsResponse(BaseModel):
    """Response from syncing all systems"""
    sync_timestamp: datetime = Field(..., description="When sync occurred")
    modules_synced: List[str] = Field(..., description="Modules synced")
    sync_results: Dict[str, Dict] = Field(..., description="Per-module results")
    total_events_processed: int = Field(..., description="Total events")

    class Config:
        json_schema_extra = {
            "example": {
                "sync_timestamp": "2024-03-15T10:45:00Z",
                "modules_synced": ["crowd_service"],
                "sync_results": {},
                "total_events_processed": 145
            }
        }


class ModuleHealth(BaseModel):
    """Health status of single module"""
    status: Literal["HEALTHY", "DEGRADED", "CRITICAL"] = Field(..., description="Module health")
    details: Dict = Field(default_factory=dict, description="Health details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "HEALTHY",
                "details": {"users_count": 1250}
            }
        }


class SystemHealthResponse(BaseModel):
    """Health status of all modules"""
    overall_status: Literal["HEALTHY", "DEGRADED", "CRITICAL"] = Field(
        ..., description="System status"
    )
    timestamp: datetime = Field(..., description="Health check time")
    modules: Dict[str, ModuleHealth] = Field(..., description="Per-module health")

    class Config:
        json_schema_extra = {
            "example": {
                "overall_status": "HEALTHY",
                "timestamp": "2024-03-15T10:45:00Z",
                "modules": {}
            }
        }


class EventLogEntry(BaseModel):
    """Entry in workflow event log"""
    event_id: str = Field(..., description="Event ID")
    timestamp: datetime = Field(..., description="When event occurred")
    event_type: str = Field(..., description="Type of event")
    source_module: str = Field(..., description="Module that generated event")
    trigger: str = Field(..., description="What triggered event")
    affected_users: Optional[int] = Field(None, description="Users affected")
    notifications_triggered: List[str] = Field(default_factory=list, description="Notifications")
    status: Literal["COMPLETED", "FAILED", "PENDING"] = Field(..., description="Event status")

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt-xxx",
                "timestamp": "2024-03-15T10:45:00Z",
                "event_type": "GATE_REASSIGNMENT_ORCHESTRATED",
                "source_module": "crowd_service",
                "trigger": "Utilization exceeded 75%",
                "affected_users": 12,
                "notifications_triggered": ["GATE_REASSIGNMENT"],
                "status": "COMPLETED"
            }
        }


class JourneyAnalyticsResponse(BaseModel):
    """Analytics summary on user journeys"""
    total_users_today: int = Field(..., description="Total users")
    average_entry_time_minutes: float = Field(..., description="Average entry time")
    users_reassigned: int = Field(..., description="Users reassigned")
    reassignment_rate_percent: float = Field(..., description="Reassignment rate")
    reasons_for_reassignment: Dict[str, int] = Field(..., description="Reasons breakdown")
    average_journey_satisfaction: float = Field(..., description="User satisfaction rating")
    food_orders_placed: int = Field(..., description="Food orders")
    emergencies_responded: int = Field(..., description="Emergencies handled")
    notifications_sent: int = Field(..., description="Total notifications")
    timestamp: datetime = Field(..., description="Analytics timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_users_today": 1250,
                "average_entry_time_minutes": 18,
                "users_reassigned": 156,
                "reassignment_rate_percent": 12.5,
                "reasons_for_reassignment": {"congestion": 120},
                "average_journey_satisfaction": 4.2,
                "food_orders_placed": 450,
                "emergencies_responded": 2,
                "notifications_sent": 4523,
                "timestamp": "2024-03-15T23:59:00Z"
            }
        }
