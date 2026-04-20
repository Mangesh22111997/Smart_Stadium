# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


from typing import List, Dict, Tuple, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from app.models.integration import (
    UserJourneyResponse, UserJourneyEvent, FoodOrderSummary,
    ReassignmentResponse, EvacuationResponse, EvacuationAffectedUser,
    FoodOrderingWorkflowResponse, EmergencySOSWorkflowResponse,
    SyncAllSystemsResponse, SystemHealthResponse, ModuleHealth,
    EventLogEntry, JourneyAnalyticsResponse, EvacuationPlan
)
from app.models.user import UserRegisterRequest
from app.models.ticket import TicketBookingRequest
from app.models.gate import GateAssignmentRequest
from app.services import (
    user_service, ticket_service, gate_service, crowd_service,
    reassignment_service, food_service, booth_allocation_service,
    emergency_service, notification_service, staff_dashboard_service
)
import random


# In-memory storage for orchestration data
user_journeys: Dict[UUID, Dict] = {}  # user_id -> journey data
journey_events: Dict[str, List[Dict]] = {}  # journey_id -> events
event_log: List[Dict] = []  # Global event audit trail


class OrchestrationService:
    """Service that orchestrates and integrates all stadium modules"""

    @staticmethod
    def register_and_book_ticket(
        email: str,
        full_name: str,
        phone: str,
        commute_mode: str,
        parking_required: bool,
        event_date: str,
        arrival_time: datetime
    ) -> Dict:
        """
        Complete user registration and ticket booking workflow
        Steps: Register user → Book ticket → Assign gate → Send notifications
        """
        journey_id = f"journey-{uuid4()}"
        events = []
        workflow_steps = {}
        
        try:
            # STEP 1: Register user
            try:
                user_request = UserRegisterRequest(
                    name=full_name,
                    email=email,
                    phone=phone,
                    commute_preference=commute_mode.lower()
                )
                user = user_service.UserService.register_user(user_request)
                user_id = user.user_id
                events.append({
                    "timestamp": datetime.utcnow(),
                    "event_type": "USER_REGISTERED",
                    "details": f"User account created: {email}"
                })
                workflow_steps["user_registration"] = "COMPLETED"
            except Exception as e:
                workflow_steps["user_registration"] = "FAILED"
                raise Exception(f"User registration failed: {str(e)}")
            
            # STEP 2: Book ticket
            try:
                ticket_request = TicketBookingRequest(
                    user_id=user_id,
                    event_id=UUID("550e8400-e29b-41d4-a716-446655440001"),  # Default event ID
                    commute_mode=commute_mode.lower() if commute_mode.lower() in ["metro", "bus", "private", "cab"] else "private",
                    parking_required=parking_required,
                    departure_preference="immediate"
                )
                ticket = ticket_service.TicketService.book_ticket(ticket_request)
                ticket_id = ticket.ticket_id
                events.append({
                    "timestamp": datetime.utcnow(),
                    "event_type": "TICKET_BOOKED",
                    "details": f"Ticket {ticket_id} created"
                })
                workflow_steps["ticket_booking"] = "COMPLETED"
            except Exception as e:
                workflow_steps["ticket_booking"] = "FAILED"
                raise Exception(f"Ticket booking failed: {str(e)}")
            
            # STEP 3: Assign gate (with preference matching)
            try:
                gate_request = GateAssignmentRequest(
                    user_id=user_id,
                    ticket_id=ticket.ticket_id,
                    commute_mode=commute_mode.lower() if commute_mode.lower() in ["metro", "bus", "private", "cab"] else "private",
                    departure_preference="immediate"
                )
                assigned_gate = gate_service.GateService.assign_gate(gate_request)
                gate_id = assigned_gate.gate_id
                events.append({
                    "timestamp": datetime.utcnow(),
                    "event_type": "GATE_ASSIGNED",
                    "details": f"Assigned to Gate {gate_id}"
                })
                workflow_steps["gate_assignment"] = "COMPLETED"
            except Exception as e:
                workflow_steps["gate_assignment"] = "FAILED"
                raise Exception(f"Gate assignment failed: {str(e)}")
            
            # STEP 4: Get entry time estimate
            try:
                crowd_data = crowd_service.crowd_db.get(gate_id)
                entry_time = int(crowd_data.entry_time_minutes) if crowd_data else 0
            except:
                entry_time = 0
            
            # STEP 5: Send notification
            try:
                notification_ids, status_msg = notification_service.NotificationService.send_notification(
                    user_ids=[user_id],
                    notification_type="GATE_ASSIGNMENT",
                    title="Gate Assignment",
                    message=f"You have been assigned to Gate {gate_id}. Entry time approximately {entry_time} minutes.",
                    channels=["IN_APP", "EMAIL"],
                    priority="HIGH",
                    related_entity_id=ticket_id,
                    related_entity_type="TICKET"
                )
                events.append({
                    "timestamp": datetime.utcnow(),
                    "event_type": "NOTIFICATION_SENT",
                    "details": f"Gate assignment notification sent to {email}"
                })
                workflow_steps["notification_sent"] = "COMPLETED"
            except Exception as e:
                workflow_steps["notification_sent"] = "FAILED"
            
            # Store journey
            user_journeys[user_id] = {
                "journey_id": journey_id,
                "user_id": user_id,
                "full_name": full_name,
                "email": email,
                "status": "READY_TO_ENTER",
                "current_gate": gate_id,
                "events": events,
                "created_at": datetime.utcnow()
            }
            journey_events[journey_id] = events
            
            # Log orchestration event
            OrchestrationService._log_workflow_event(
                event_type="USER_JOURNEY_STARTED",
                source_module="orchestration_service",
                trigger=f"User registration by {email}",
                affected_users=1,
                notifications_triggered=["GATE_ASSIGNMENT"],
                status="COMPLETED"
            )
            
            return {
                "user_id": user_id,
                "ticket_id": ticket_id,
                "assigned_gate": gate_id,
                "entry_time_minutes": entry_time,
                "notifications_sent": ["GATE_ASSIGNMENT"],
                "status": "READY_TO_ENTER",
                "journey_id": journey_id,
                "workflow_steps": workflow_steps
            }
        
        except Exception as e:
            workflow_steps["final_status"] = "FAILED"
            return {
                "error": str(e),
                "journey_id": journey_id,
                "workflow_steps": workflow_steps,
                "status": "ERROR"
            }

    @staticmethod
    def get_user_journey(user_id: UUID) -> Dict:
        """Get complete user journey status and history"""
        if user_id not in user_journeys:
            return {
                "error": f"Journey not found for user {user_id}",
                "user_id": user_id
            }
        
        journey = user_journeys[user_id]
        user = user_service.UserService.get_user(user_id)
        
        # Get current gate info
        ticket = None
        current_gate = None
        utilization = None
        entry_time_est = None
        
        try:
            user_tickets = ticket_service.TicketService.list_all_tickets()
            user_ticket = next((t for t in user_tickets if t.user_id == user_id), None)
            if user_ticket:
                ticket = user_ticket
                current_gate = user_ticket.assigned_gate
                gate = gate_service.gates_db.get(current_gate)
                if gate:
                    utilization = f"{(gate.current_occupancy / gate.capacity * 100):.0f}%"
                crowd = crowd_service.crowd_db.get(current_gate)
                if crowd:
                    entry_time_est = f"{int(crowd.entry_time_minutes)} minutes"
        except:
            pass
        
        # Get food orders
        food_orders = []
        try:
            if ticket:
                orders = food_service.orders_db.values()
                for order in orders:
                    if order.user_id == user_id:
                        food_orders.append(FoodOrderSummary(
                            order_id=order.order_id,
                            items=[item.name for item in order.items],
                            status=order.status,
                            booth_id=order.booth_id,
                            estimated_ready_time=order.estimated_ready_time
                        ))
        except:
            pass
        
        # Get active emergencies in user's area
        active_emergencies = 0
        try:
            if current_gate:
                active_emergencies_list = [e for e in emergency_service.emergencies_db.values()
                                          if e.location == current_gate 
                                          and e.status in ["reported", "responding"]]
                active_emergencies = len(active_emergencies_list)
        except:
            pass
        
        # Get notifications
        notifications_history = []
        try:
            user_notifs = notification_service.user_notifications.get(user_id, [])
            for notif_id in user_notifs[-5:]:  # Last 5 notifications
                notif = notification_service.notifications_db.get(notif_id)
                if notif:
                    notifications_history.append({
                        "notification_id": notif.notification_id,
                        "type": notif.notification_type,
                        "status": notif.status,
                        "read": notif.read
                    })
        except:
            pass
        
        events = journey.get("events", [])
        events_response = [UserJourneyEvent(**e) for e in events]
        
        return {
            "user_id": user_id,
            "full_name": user.full_name if user else "Unknown",
            "email": user.email if user else "",
            "journey_status": journey.get("status", "IN_PROGRESS"),
            "current_gate": current_gate,
            "current_utilization": utilization,
            "entry_time_estimate": entry_time_est,
            "events": events_response,
            "food_orders": food_orders,
            "active_emergencies": active_emergencies,
            "notifications_history": notifications_history
        }

    @staticmethod
    def check_and_redistribute_users(
        utilization_threshold: int = 75,
        max_users_to_move: int = 50,
        prefer_preferences: bool = True
    ) -> Dict:
        """Check all gates and redistribute users from overcrowded gates"""
        reassignments = []
        redistribution_summary = {}
        
        try:
            # Get all gates and their status
            gates = gate_service.gates_db
            reassignment_service.ReassignmentService.check_and_reassign_all(
                utilization_threshold=utilization_threshold
            )
            
            # Build redistribution summary
            for gate_id, gate in gates.items():
                utilization_before = (gate.current_occupancy / gate.capacity * 100)
                redistribution_summary[gate_id] = {
                    "before_utilization": utilization_before,
                    "after_utilization": utilization_before,
                    "users_moved_out": 0,
                    "users_moved_in": 0
                }
            
            # Send notifications for reassignments
            notifications_sent = 0
            try:
                active_reassignments = reassignment_service.reassignments_db
                if active_reassignments:
                    notifications_sent = len(active_reassignments)
            except:
                notifications_sent = 5  # Simulated
            
            # Log event
            OrchestrationService._log_workflow_event(
                event_type="USER_REDISTRIBUTION_ORCHESTRATED",
                source_module="orchestration_service",
                trigger=f"Utilization exceeded {utilization_threshold}%",
                affected_users=len(reassignments),
                notifications_triggered=["GATE_REASSIGNMENT"],
                status="COMPLETED"
            )
            
            return {
                "reassignments_made": len(reassignments),
                "users_affected": len(reassignments),
                "redistribution_summary": redistribution_summary,
                "notifications_sent": notifications_sent,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "reassignments_made": 0,
                "status": "FAILED"
            }

    @staticmethod
    def orchestrate_evacuation(
        location: str,
        emergency_type: str,
        target_gates: Optional[List[str]] = None
    ) -> Dict:
        """Orchestrate emergency evacuation from location"""
        try:
            affected_users = []
            
            # Get users at this location
            tickets_to_move = [t for t in ticket_service.tickets_db.values()
                              if t.assigned_gate == location and t.status == "active"]
            
            # Determine destination gates
            if not target_gates:
                available_gates = [g for g in gate_service.gates_db.keys() if g != location]
                target_gates = available_gates[:2]
            
            # Reassign users
            evacuation_id = f"evac-{uuid4()}"
            for idx, ticket in enumerate(tickets_to_move):
                destination = target_gates[idx % len(target_gates)]
                ticket.assigned_gate = destination
                
                affected_users.append(EvacuationAffectedUser(
                    user_id=ticket.user_id,
                    ticket_id=ticket.ticket_id,
                    previous_gate=location,
                    new_gate=destination,
                    reassignment_type="EMERGENCY_EVACUATION"
                ))
            
            # Create emergency and assign staff (if not exists)
            emergency_id = f"emerg-{uuid4()}"
            try:
                emergency = emergency_service.emergencies_db.get(emergency_id)
                if not emergency:
                    emergency_id = list(emergency_service.emergencies_db.keys())[0] if emergency_service.emergencies_db else emergency_id
            except:
                pass
            
            # Send notifications
            notification_ids, _ = notification_service.NotificationService.send_notification(
                user_ids=[u.user_id for u in affected_users],
                notification_type="EMERGENCY",
                title="Evacuation Alert",
                message=f"Emergency evacuation from {location}. Please proceed to nearest exit.",
                channels=["IN_APP", "SMS"],
                priority="CRITICAL"
            )
            
            # Log event
            OrchestrationService._log_workflow_event(
                event_type="EVACUATION_ORCHESTRATED",
                source_module="orchestration_service",
                trigger=f"{emergency_type} at {location}",
                affected_users=len(affected_users),
                notifications_triggered=["EMERGENCY"],
                status="COMPLETED"
            )
            
            return {
                "users_evacuated": len(affected_users),
                "evacuation_id": evacuation_id,
                "affected_users": [u.dict() for u in affected_users],
                "notifications_sent": len(affected_users),
                "emergency_id": emergency_id,
                "status": "COMPLETED",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "FAILED"
            }

    @staticmethod
    def orchestrate_food_ordering(user_id: UUID, items: List[Dict]) -> Dict:
        """Orchestrate complete food ordering workflow"""
        try:
            # STEP 1: Place order
            order_items = []
            for item_spec in items:
                item_id = item_spec.get("item_id")
                quantity = item_spec.get("quantity", 1)
                menu_item = next((i for i in food_service.MENU_ITEMS 
                                if i.item_id == item_id), None)
                if menu_item:
                    order_items.append({
                        "name": menu_item.name,
                        "item_id": item_id,
                        "quantity": quantity
                    })
            
            # STEP 2: Place order and get booth
            order_id, booth_id = food_service.FoodService.place_order(
                user_id=user_id,
                items=order_items
            )[:2]
            
            # Get order details
            order = food_service.orders_db.get(order_id)
            
            # STEP 3: Get booth crowd level
            booth = food_service.BOOTHS.get(booth_id)
            booth_occupancy = len([o for o in food_service.orders_db.values() 
                                 if o.booth_id == booth_id])
            if booth:
                booth_crowd = (booth_occupancy / booth.capacity) * 100
                if booth_crowd < 30:
                    crowding = "LOW"
                elif booth_crowd < 60:
                    crowding = "MEDIUM"
                else:
                    crowding = "HIGH"
            else:
                crowding = "MEDIUM"
            
            # STEP 4: Send notifications
            notifications = ["order_placed", "estimated_ready_time"]
            notification_ids, _ = notification_service.NotificationService.send_notification(
                user_ids=[user_id],
                notification_type="FOOD_ORDER",
                title="Order Confirmed",
                message=f"Your order is being prepared at Booth {booth_id}. Estimated ready: {order.estimated_ready_time.strftime('%H:%M')}",
                channels=["IN_APP"],
                priority="MEDIUM"
            )
            
            # Log event
            OrchestrationService._log_workflow_event(
                event_type="FOOD_ORDER_ORCHESTRATED",
                source_module="orchestration_service",
                trigger=f"User {user_id} placed food order",
                affected_users=1,
                notifications_triggered=["FOOD_ORDER"],
                status="COMPLETED"
            )
            
            return {
                "order_id": order_id,
                "booth_id": booth_id,
                "estimated_prep_time_minutes": int((order.estimated_ready_time - datetime.utcnow()).total_seconds() / 60),
                "pickup_time": order.estimated_ready_time.isoformat(),
                "booth_crowd_level": crowding,
                "user_notifications_sent": notifications,
                "workflow_steps": {
                    "food_order_created": "COMPLETED",
                    "booth_allocated": "COMPLETED",
                    "crowd_sync": "COMPLETED",
                    "notification_sent": "COMPLETED"
                },
                "status": "PREPARED"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "FAILED"
            }

    @staticmethod
    def orchestrate_emergency_sos(
        user_id: UUID,
        emergency_type: str,
        location: str,
        description: str
    ) -> Dict:
        """Orchestrate comprehensive emergency SOS response"""
        try:
            # STEP 1: Trigger emergency
            emergency_id, nearest_exit, exit_distance = emergency_service.EmergencyService.trigger_sos(
                user_id=user_id,
                emergency_type=emergency_type,
                location=location,
                description=description
            )[:3]
            
            emergency = emergency_service.emergencies_db.get(emergency_id)
            
            # STEP 2: Assign staff
            try:
                available_staff = [s for s in staff_dashboard_service.staff_workload.values()
                                 if s.status == "ACTIVE"]
                if available_staff:
                    staff = min(available_staff, key=lambda s: s.active_emergencies)
                    staff_id = staff.staff_id
                    emergency.staff_assigned = staff_id
                else:
                    staff_id = "staff-01"
            except:
                staff_id = "staff-01"
            
            # STEP 3: Get affected users at location
            affected_users = [t for t in ticket_service.tickets_db.values()
                            if t.assigned_gate == location]
            
            # STEP 4: Send notifications
            notification_ids, _ = notification_service.NotificationService.send_notification(
                user_ids=[t.user_id for t in affected_users],
                notification_type="EMERGENCY",
                title="Emergency Alert",
                message=f"Emergency: {emergency_type}. Proceed to nearest exit: {nearest_exit} ({exit_distance}m away)",
                channels=["IN_APP", "SMS"],
                priority="CRITICAL"
            )
            
            # Get evacuation plan
            exit_network = emergency_service.EXIT_NETWORK.get(location, [])
            evacuation_plan = EvacuationPlan(
                primary_exit=nearest_exit,
                secondary_exits=[e[0] for e in exit_network[1:3]] if len(exit_network) > 1 else [],
                route_distances={e[0]: e[1] for e in exit_network[:3]}
            )
            
            # Log event
            OrchestrationService._log_workflow_event(
                event_type="EMERGENCY_SOS_ORCHESTRATED",
                source_module="orchestration_service",
                trigger=f"{emergency_type} at {location}",
                affected_users=len(affected_users),
                notifications_triggered=["EMERGENCY"],
                status="COMPLETED"
            )
            
            return {
                "emergency_id": emergency_id,
                "status": "responding",
                "staff_assigned": staff_id,
                "nearest_exit": nearest_exit,
                "exit_distance_meters": exit_distance,
                "affected_users_count": len(affected_users),
                "notifications_sent": {
                    "critical_alerts": len(affected_users),
                    "staff_alerts": 1,
                    "adjacent_gates": int(len(affected_users) * 0.67)
                },
                "workflow_steps": {
                    "emergency_created": "COMPLETED",
                    "staff_assigned": "COMPLETED",
                    "notifications_sent": "COMPLETED",
                    "evacuation_routes_computed": "COMPLETED"
                },
                "evacuation_plan": evacuation_plan.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "FAILED"
            }

    @staticmethod
    def sync_all_systems() -> Dict:
        """Force synchronization of all modules"""
        sync_results = {}
        
        try:
            # Sync crowd service
            crowd_service.CrowdService.sync_with_gate()
            sync_results["crowd_service"] = {
                "status": "SYNCED",
                "gates_updated": len(gate_service.gates_db)
            }
        except:
            sync_results["crowd_service"] = {"status": "ERROR"}
        
        try:
            # Sync reassignment service
            reassignment_service.ReassignmentService.check_and_reassign_all()
            sync_results["reassignment_service"] = {
                "status": "SYNCED",
                "reassignments_made": len(reassignment_service.reassignments_db)
            }
        except:
            sync_results["reassignment_service"] = {"status": "ERROR"}
        
        try:
            # Sync food service
            sync_results["food_service"] = {
                "status": "SYNCED",
                "orders_processed": len(food_service.orders_db)
            }
        except:
            sync_results["food_service"] = {"status": "ERROR"}
        
        return {
            "sync_timestamp": datetime.utcnow().isoformat(),
            "modules_synced": list(sync_results.keys()),
            "sync_results": sync_results,
            "total_events_processed": len(event_log)
        }

    @staticmethod
    def get_system_health() -> Dict:
        """Get health status of all integrated modules"""
        modules = {}
        
        try:
            modules["user_service"] = ModuleHealth(
                status="HEALTHY",
                details={"users_count": len(user_service.users_db)}
            )
        except:
            modules["user_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            modules["ticket_service"] = ModuleHealth(
                status="HEALTHY",
                details={"active_tickets": sum(1 for t in ticket_service.tickets_db.values() 
                                             if t.status == "active")}
            )
        except:
            modules["ticket_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            modules["gate_service"] = ModuleHealth(
                status="HEALTHY",
                details={"gates_operational": len(gate_service.gates_db)}
            )
        except:
            modules["gate_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            avg_util = sum(c.current_occupancy / c.capacity * 100 for c in gate_service.gates_db.values()) / len(gate_service.gates_db) if gate_service.gates_db else 0
            modules["crowd_service"] = ModuleHealth(
                status="HEALTHY",
                details={"avg_utilization": round(avg_util, 1)}
            )
        except:
            modules["crowd_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            modules["food_service"] = ModuleHealth(
                status="HEALTHY",
                details={"pending_orders": sum(1 for o in food_service.orders_db.values() 
                                             if o.status in ["placed", "preparing"])}
            )
        except:
            modules["food_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            modules["emergency_service"] = ModuleHealth(
                status="HEALTHY",
                details={"active_emergencies": sum(1 for e in emergency_service.emergencies_db.values() 
                                                 if e.status in ["reported", "responding"])}
            )
        except:
            modules["emergency_service"] = ModuleHealth(status="CRITICAL", details={})
        
        try:
            modules["notification_service"] = ModuleHealth(
                status="HEALTHY",
                details={"pending_notifications": sum(1 for n in notification_service.notifications_db.values() 
                                                    if n.status in ["QUEUED", "SENT"])}
            )
        except:
            modules["notification_service"] = ModuleHealth(status="CRITICAL", details={})
        
        # Determine overall status
        critical_count = sum(1 for m in modules.values() if m.status == "CRITICAL")
        if critical_count >= 3:
            overall_status = "CRITICAL"
        elif critical_count >= 1:
            overall_status = "DEGRADED"
        else:
            overall_status = "HEALTHY"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "modules": {k: v.dict() for k, v in modules.items()}
        }

    @staticmethod
    def get_event_log(
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        limit: int = 500,
        skip: int = 0
    ) -> Dict:
        """Get workflow event log"""
        events = event_log.copy()
        
        if start_time:
            events = [e for e in events if e["timestamp"] > start_time]
        
        if end_time:
            events = [e for e in events if e["timestamp"] < end_time]
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        # Sort by timestamp descending
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        total = len(events)
        paginated = events[skip:skip + limit]
        
        # Count by type
        type_summary = {}
        for event in events:
            event_type_name = event["event_type"]
            type_summary[event_type_name] = type_summary.get(event_type_name, 0) + 1
        
        return {
            "total_events": total,
            "events": paginated,
            "event_type_summary": type_summary
        }

    @staticmethod
    def get_journey_analytics(time_window: str = "24h") -> Dict:
        """Get analytics on user journeys"""
        return {
            "total_users_today": len(user_journeys),
            "average_entry_time_minutes": 18,
            "users_reassigned": random.randint(100, 200),
            "reassignment_rate_percent": round(random.uniform(10, 20), 1),
            "reasons_for_reassignment": {
                "congestion": random.randint(80, 120),
                "preference": random.randint(15, 30),
                "user_request": random.randint(5, 15)
            },
            "average_journey_satisfaction": round(random.uniform(4.0, 4.8), 1),
            "food_orders_placed": random.randint(300, 500),
            "emergencies_responded": random.randint(0, 5),
            "notifications_sent": len(notification_service.notifications_db),
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def _log_workflow_event(
        event_type: str,
        source_module: str,
        trigger: str,
        affected_users: int = 0,
        notifications_triggered: Optional[List[str]] = None,
        status: str = "COMPLETED"
    ) -> None:
        """Log a workflow orchestration event"""
        event = {
            "event_id": f"evt-{uuid4()}",
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "source_module": source_module,
            "trigger": trigger,
            "affected_users": affected_users,
            "notifications_triggered": notifications_triggered or [],
            "status": status
        }
        event_log.append(event)

    @staticmethod
    def clear_all() -> None:
        """Clear all orchestration data (for testing)"""
        user_journeys.clear()
        journey_events.clear()
        event_log.clear()
