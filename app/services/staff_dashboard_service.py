from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from app.models.staff_dashboard import (
    ControlRoomSummary, GateSummary, CrowdAnalysis, StaffActionLog,
    StaffWorkloadMetrics, StaffWorkloadResponse
)
from app.services import (
    gate_service, crowd_service, emergency_service,
    food_service, notification_service, ticket_service
)
import random


# In-memory storage for staff actions (audit trail)
staff_actions_db: Dict[str, StaffActionLog] = {}

# Track staff workload
staff_workload: Dict[str, StaffWorkloadMetrics] = {
    "staff-01": StaffWorkloadMetrics(staff_id="staff-01", status="ACTIVE", assigned_zone="gates_a_b"),
    "staff-02": StaffWorkloadMetrics(staff_id="staff-02", status="ACTIVE", assigned_zone="gates_c_d"),
    "staff-03": StaffWorkloadMetrics(staff_id="staff-03", status="BREAK", assigned_zone="gates_a_b")
}

# Gate capacity overrides (temporary)
gate_capacity_overrides: Dict[str, Dict] = {}


class StaffDashboardService:
    """Service for staff dashboard operations and monitoring"""

    @staticmethod
    def get_dashboard_summary() -> ControlRoomSummary:
        """Get high-level system status for control room"""
        gates = gate_service.gates_db
        crowd = crowd_service.crowd_db
        total_users = sum(g.current_occupancy for g in gates.values())
        avg_util = (total_users / sum(g.capacity for g in gates.values() if g)) * 100 if gates else 0
        
        active_emergencies = emergency_service.emergencies_db.values()
        active_emerg_list = [e for e in active_emergencies if e.status in ["reported", "responding"]]
        critical_count = sum(1 for e in active_emerg_list if e.priority == "CRITICAL")
        
        pending_notifs = sum(1 for n in notification_service.notifications_db.values() 
                            if n.status in ["QUEUED", "SENT"] and not n.read)
        
        food_pending = sum(1 for o in food_service.orders_db.values() 
                          if o.status in ["placed", "preparing"])
        
        # Determine gate system status
        overcrowded_gates = sum(1 for g in gates.values() if g.current_occupancy / g.capacity > 0.85)
        if overcrowded_gates >= 2:
            gate_status = "CRITICAL"
        elif overcrowded_gates >= 1:
            gate_status = "DEGRADED"
        else:
            gate_status = "OPERATIONAL"
        
        # Determine overall system status
        if critical_count > 0 or gate_status == "CRITICAL":
            system_status = "CRITICAL"
        elif gate_status == "DEGRADED" or len(active_emerg_list) > 1:
            system_status = "WARNING"
        else:
            system_status = "HEALTHY"
        
        return ControlRoomSummary(
            timestamp=datetime.utcnow(),
            total_gates=len(gates),
            total_users_in_stadium=total_users,
            average_gate_utilization=round(avg_util, 1),
            total_active_emergencies=len(active_emerg_list),
            critical_emergencies=critical_count,
            pending_notifications=pending_notifs,
            food_orders_pending=food_pending,
            gate_status=gate_status,
            system_status=system_status
        )

    @staticmethod
    def get_gates_dashboard() -> List[GateSummary]:
        """Get real-time status of all gates"""
        gates_summary = []
        
        for gate_id, gate in gate_service.gates_db.items():
            # Check for capacity override
            effective_capacity = gate.capacity
            if gate_id in gate_capacity_overrides:
                override_info = gate_capacity_overrides[gate_id]
                if datetime.utcnow() < override_info["expires_at"]:
                    effective_capacity = override_info["new_capacity"]
            
            utilization = (gate.current_occupancy / effective_capacity * 100) if effective_capacity else 0
            
            # Determine crowding level
            if utilization < 30:
                crowding = "LOW"
            elif utilization < 60:
                crowding = "MEDIUM"
            elif utilization < 85:
                crowding = "HIGH"
            else:
                crowding = "CRITICAL"
            
            # Get crowd data for entry time calculation
            crowd_data = crowd_service.crowd_db.get(gate_id)
            entry_time = crowd_data.entry_time_minutes if crowd_data else 0
            
            # Get recent events from action log
            recent_events = []
            for action_id, action in list(staff_actions_db.items())[-10:]:
                if action.related_entity_id == gate_id and \
                   datetime.utcnow() - action.timestamp < timedelta(hours=1):
                    recent_events.append(
                        f"{action.action_type.replace('_', ' ').title()} at {action.timestamp.strftime('%H:%M')}"
                    )
            
            gates_summary.append(GateSummary(
                gate_id=gate_id,
                capacity=effective_capacity,
                current_occupancy=gate.current_occupancy,
                utilization_percent=round(utilization, 1),
                entry_time_minutes=int(entry_time),
                status=gate.status,
                crowding_level=crowding,
                recent_events=recent_events[-3:]  # Last 3 events
            ))
        
        return gates_summary

    @staticmethod
    def get_crowd_analysis(location: str, include_history: bool = False) -> CrowdAnalysis:
        """Get detailed crowd analysis for a location"""
        crowd_data = crowd_service.crowd_db.get(location)
        gate_data = gate_service.gates_db.get(location)
        
        if not crowd_data or not gate_data:
            raise ValueError(f"Location {location} not found")
        
        utilization = (crowd_data.current_occupancy / gate_data.capacity * 100)
        
        # Determine crowding level
        if utilization < 30:
            crowding = "LOW"
        elif utilization < 60:
            crowding = "MEDIUM"
        elif utilization < 85:
            crowding = "HIGH"
        else:
            crowding = "CRITICAL"
        
        # Generate recommendations
        recommendations = []
        if utilization > 80:
            recommendations.append("Consider opening alternate gates to distribute crowd")
        elif utilization < 30:
            recommendations.append("Gate is underutilized, could handle more traffic")
        
        if crowd_data.entry_time_minutes > 25:
            recommendations.append("Entry time exceeds target, consider crowd redistribution")
        
        if utilization > 0:
            recommendations.append(f"Current entry time acceptable at {crowd_data.entry_time_minutes} minutes")
        
        # Create history data (simulated)
        history = []
        if include_history:
            for i in range(6):
                hours_ago = 5 - i
                simulated_occupancy = max(5, crowd_data.current_occupancy + random.randint(-15, 15))
                history.append({
                    "time": (datetime.utcnow() - timedelta(hours=hours_ago)).strftime("%H:%M"),
                    "occupancy": simulated_occupancy
                })
        
        return CrowdAnalysis(
            location=location,
            current_occupancy=crowd_data.current_occupancy,
            capacity=gate_data.capacity,
            utilization_percent=round(utilization, 1),
            crowding_level=crowding,
            entry_time_minutes=int(crowd_data.entry_time_minutes),
            peak_time=(datetime.utcnow() - timedelta(hours=1)).strftime("%H:%M"),
            arrival_rate=random.uniform(2, 8),
            departure_rate=random.uniform(1, 5),
            net_change=random.uniform(-2, 3),
            recommendations=recommendations,
            history=history
        )

    @staticmethod
    def get_active_emergencies(
        priority_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get all active emergencies with details"""
        emergencies_list = []
        
        for emergency_id, emergency in emergency_service.emergencies_db.items():
            # Check status
            if status_filter and emergency.status != status_filter:
                continue
            
            # Check priority
            if priority_filter and emergency.priority != priority_filter:
                continue
            
            # Only show active (reported or responding)
            if emergency.status not in ["reported", "responding"]:
                continue
            
            # Calculate response time
            response_time = 0
            if emergency.sent_at:
                response_time = int((emergency.sent_at - emergency.created_at).total_seconds())
            
            emergencies_list.append({
                "emergency_id": emergency.emergency_id,
                "user_id": str(emergency.user_id),
                "emergency_type": emergency.emergency_type,
                "priority": emergency.priority,
                "location": emergency.location,
                "description": emergency.description,
                "nearest_exit": emergency.nearest_exit,
                "exit_distance_meters": emergency.exit_distance_meters,
                "status": emergency.status,
                "staff_assigned": emergency.staff_assigned,
                "reported_at": emergency.created_at.isoformat(),
                "response_time_seconds": response_time
            })
        
        # Sort by priority (CRITICAL first)
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        emergencies_list.sort(key=lambda x: priority_order.get(x["priority"], 999))
        
        return emergencies_list

    @staticmethod
    def get_food_order_status() -> Dict:
        """Get food ordering system status"""
        total_orders = len(food_service.orders_db)
        pending_orders = sum(1 for o in food_service.orders_db.values() 
                            if o.status in ["placed", "preparing"])
        ready_orders = sum(1 for o in food_service.orders_db.values() 
                          if o.status == "ready")
        
        booths_info = []
        for booth_id, booth in food_service.BOOTHS.items():
            booth_orders = [o for o in food_service.orders_db.values() 
                           if o.booth_id == booth_id]
            queue_count = sum(1 for o in booth_orders 
                            if o.status in ["placed", "preparing"])
            ready_count = sum(1 for o in booth_orders if o.status == "ready")
            
            oldest_minutes = 0
            if queue_count > 0:
                oldest = min((datetime.utcnow() - o.created_at).total_seconds() 
                           for o in booth_orders 
                           if o.status in ["placed", "preparing"])
                oldest_minutes = int(oldest / 60)
            
            booths_info.append({
                "booth_id": booth_id,
                "capacity": booth.capacity,
                "current_queue": queue_count,
                "average_prep_time_minutes": 15,
                "status": "OPERATIONAL",
                "orders_ready": ready_count,
                "oldest_waiting_minutes": oldest_minutes
            })
        
        # Recommendations
        recommendations = []
        max_queue = max((sum(1 for o in food_service.orders_db.values() 
                           if o.booth_id == b) for b in food_service.BOOTHS.keys()), default=0)
        if max_queue > 5:
            recommendations.append("Some booths have long queues. Consider directing orders elsewhere.")
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "ready_for_pickup": ready_orders,
            "booths": booths_info,
            "system_status": "OPERATIONAL",
            "recommendations": recommendations
        }

    @staticmethod
    def get_notifications_queue(
        priority_filter: Optional[str] = None
    ) -> Dict:
        """Get active notification queue"""
        active_notifs = [n for n in notification_service.notifications_db.values() 
                        if n.status in ["QUEUED", "SENT"]]
        
        if priority_filter:
            active_notifs = [n for n in active_notifs if n.priority == priority_filter]
        
        priority_counts = {
            "CRITICAL": sum(1 for n in active_notifs if n.priority == "CRITICAL"),
            "HIGH": sum(1 for n in active_notifs if n.priority == "HIGH"),
            "MEDIUM": sum(1 for n in active_notifs if n.priority == "MEDIUM"),
            "LOW": sum(1 for n in active_notifs if n.priority == "LOW")
        }
        
        unacknowledged = [n for n in active_notifs if not n.read]
        
        notif_list = []
        for n in sorted(active_notifs, 
                       key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x.priority, 999))[:20]:
            notif_list.append({
                "notification_id": n.notification_id,
                "notification_type": n.notification_type,
                "title": n.title,
                "priority": n.priority,
                "status": n.status,
                "created_at": n.created_at.isoformat(),
                "acknowledged": n.read
            })
        
        return {
            "total_notifications": len(active_notifs),
            "unacknowledged_count": len(unacknowledged),
            "active_critical": priority_counts["CRITICAL"],
            "active_high": priority_counts["HIGH"],
            "notifications": notif_list
        }

    @staticmethod
    def get_tickets_by_gate(gate_id: str) -> List[Dict]:
        """Get all tickets assigned to a gate"""
        tickets = [t for t in ticket_service.tickets_db.values() 
                  if t.assigned_gate == gate_id]
        
        gate_data = gate_service.gates_db.get(gate_id)
        if not gate_data:
            raise ValueError(f"Gate {gate_id} not found")
        
        tickets_list = []
        for ticket in sorted(tickets, key=lambda x: x.entry_time):
            tickets_list.append({
                "ticket_id": ticket.ticket_id,
                "user_id": str(ticket.user_id),
                "assigned_gate": ticket.assigned_gate,
                "entry_time": ticket.entry_time.isoformat(),
                "parking_required": ticket.parking_required,
                "commute_mode": ticket.commute_mode,
                "status": ticket.status
            })
        
        return tickets_list

    @staticmethod
    def open_gate(gate_id: str, staff_id: str, reason: str, notes: Optional[str] = None) -> Dict:
        """Open a gate"""
        gate = gate_service.gates_db.get(gate_id)
        if not gate:
            raise ValueError(f"Gate {gate_id} not found")
        
        previous_status = gate.status
        gate.status = "OPERATIONAL"
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="gate_open",
            related_entity_id=gate_id,
            reason=reason,
            notes=notes
        )
        
        return {
            "gate_id": gate_id,
            "action": "OPENED",
            "previous_status": previous_status,
            "new_status": gate.status,
            "action_timestamp": datetime.utcnow().isoformat(),
            "staff_id": staff_id,
            "reason": reason
        }

    @staticmethod
    def close_gate(
        gate_id: str, staff_id: str, reason: str,
        estimated_reopening_minutes: Optional[int] = None,
        affected_users_action: str = "reassign_to_nearest",
        notes: Optional[str] = None
    ) -> Dict:
        """Close a gate and handle affected users"""
        gate = gate_service.gates_db.get(gate_id)
        if not gate:
            raise ValueError(f"Gate {gate_id} not found")
        
        # Get affected tickets
        affected_tickets = [t for t in ticket_service.tickets_db.values() 
                           if t.assigned_gate == gate_id and t.status == "active"]
        affected_count = len(affected_tickets)
        
        # Handle user redirects
        reassigned_count = 0
        if affected_users_action == "reassign_to_nearest":
            for ticket in affected_tickets:
                # Reassign to gate with lowest utilization
                best_gate = min(gate_service.gates_db.values(),
                              key=lambda g: g.current_occupancy / g.capacity if g.gate_id != gate_id else float('inf'))
                if best_gate:
                    ticket.assigned_gate = best_gate.gate_id
                    reassigned_count += 1
        
        previous_status = gate.status
        gate.status = "CLOSED"
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="gate_close",
            related_entity_id=gate_id,
            reason=reason,
            affected_users=affected_count,
            notes=notes
        )
        
        return {
            "gate_id": gate_id,
            "action": "CLOSED",
            "previous_status": previous_status,
            "new_status": gate.status,
            "affected_users": affected_count,
            "users_reassigned": reassigned_count,
            "action_timestamp": datetime.utcnow().isoformat(),
            "staff_id": staff_id
        }

    @staticmethod
    def override_gate_capacity(
        gate_id: str, new_capacity: int, duration_minutes: int,
        staff_id: str, reason: str, notes: Optional[str] = None
    ) -> Dict:
        """Temporarily override gate capacity"""
        gate = gate_service.gates_db.get(gate_id)
        if not gate:
            raise ValueError(f"Gate {gate_id} not found")
        
        previous_capacity = gate.capacity
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        # Store override
        gate_capacity_overrides[gate_id] = {
            "new_capacity": new_capacity,
            "expires_at": expires_at
        }
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="capacity_override",
            related_entity_id=gate_id,
            reason=reason,
            duration_seconds=duration_minutes * 60,
            notes=notes
        )
        
        return {
            "gate_id": gate_id,
            "previous_capacity": previous_capacity,
            "new_capacity": new_capacity,
            "override_active": True,
            "expires_at": expires_at.isoformat(),
            "reason": reason
        }

    @staticmethod
    def manual_reassignment(
        ticket_id: str, new_gate_id: str, staff_id: str,
        reason: str, notes: Optional[str] = None
    ) -> Dict:
        """Manually reassign a user to different gate"""
        ticket = ticket_service.tickets_db.get(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        new_gate = gate_service.gates_db.get(new_gate_id)
        if not new_gate:
            raise ValueError(f"Gate {new_gate_id} not found")
        
        previous_gate = ticket.assigned_gate
        ticket.assigned_gate = new_gate_id
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="reassignment",
            related_entity_id=ticket_id,
            reason=reason,
            notes=notes
        )
        
        return {
            "ticket_id": ticket_id,
            "user_id": str(ticket.user_id),
            "previous_gate": previous_gate,
            "new_gate": new_gate_id,
            "reassignment_type": "MANUAL",
            "reassignment_timestamp": datetime.utcnow().isoformat(),
            "staff_id": staff_id,
            "reason": reason
        }

    @staticmethod
    def respond_to_emergency(
        emergency_id: str, staff_id: str,
        response_type: str = "immediate",
        initial_notes: Optional[str] = None
    ) -> Dict:
        """Staff begin response to emergency"""
        emergency = emergency_service.emergencies_db.get(emergency_id)
        if not emergency:
            raise ValueError(f"Emergency {emergency_id} not found")
        
        emergency.staff_assigned = staff_id
        emergency.status = "responding"
        
        response_time = int((datetime.utcnow() - emergency.created_at).total_seconds())
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="emergency_response",
            related_entity_id=emergency_id,
            reason=f"Emergency response - {emergency.emergency_type}",
            notes=initial_notes
        )
        
        return {
            "emergency_id": emergency_id,
            "staff_id": staff_id,
            "status": "responding",
            "response_time_seconds": response_time,
            "initial_notes": initial_notes,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def update_emergency_status(
        emergency_id: str, new_status: str, staff_id: str,
        resolution_notes: Optional[str] = None,
        evacuation_required: bool = False
    ) -> Dict:
        """Update emergency status"""
        emergency = emergency_service.emergencies_db.get(emergency_id)
        if not emergency:
            raise ValueError(f"Emergency {emergency_id} not found")
        
        previous_status = emergency.status
        emergency.status = new_status
        
        # Calculate resolution time
        resolution_time = 0
        if new_status == "resolved":
            resolution_time = int((datetime.utcnow() - emergency.created_at).total_seconds())
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="emergency_response",
            related_entity_id=emergency_id,
            reason=f"Emergency status update to {new_status}",
            duration_seconds=resolution_time if resolution_time > 0 else None,
            notes=resolution_notes
        )
        
        return {
            "emergency_id": emergency_id,
            "previous_status": previous_status,
            "new_status": new_status,
            "resolution_time_seconds": resolution_time,
            "staff_id": staff_id,
            "resolved_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def acknowledge_notification(
        notification_id: str, staff_id: str,
        action_taken: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Staff acknowledge a notification"""
        notification = notification_service.get_notification(notification_id)
        if not notification:
            raise ValueError(f"Notification {notification_id} not found")
        
        notification_service.mark_as_read(notification_id)
        
        # Log action
        StaffDashboardService._log_action(
            staff_id=staff_id,
            action_type="notification_acknowledged",
            related_entity_id=notification_id,
            reason="Staff acknowledged notification",
            notes=f"{action_taken}: {notes}" if action_taken else notes
        )
        
        return {
            "notification_id": notification_id,
            "acknowledged": True,
            "acknowledged_by": staff_id,
            "acknowledged_at": datetime.utcnow().isoformat(),
            "action_taken": action_taken
        }

    @staticmethod
    def get_action_history(
        staff_id: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
        hours: int = 24
    ) -> Tuple[List[StaffActionLog], int]:
        """Get staff action history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        actions = [a for a in staff_actions_db.values() 
                  if a.timestamp > cutoff_time]
        
        if staff_id:
            actions = [a for a in actions if a.staff_id == staff_id]
        
        if action_type:
            actions = [a for a in actions if a.action_type == action_type]
        
        # Sort by timestamp descending
        actions.sort(key=lambda x: x.timestamp, reverse=True)
        
        total_count = len(actions)
        paginated = actions[skip:skip + limit]
        
        return paginated, total_count

    @staticmethod
    def get_staff_workload() -> StaffWorkloadResponse:
        """Get overall staff workload metrics"""
        active_staff = sum(1 for s in staff_workload.values() if s.status == "ACTIVE")
        
        # Update staff metrics
        for staff in staff_workload.values():
            # Count active emergencies assigned to this staff
            staff.active_emergencies = sum(1 for e in emergency_service.emergencies_db.values()
                                          if e.staff_assigned == staff.staff_id 
                                          and e.status in ["reported", "responding"])
            
            # Count actions today
            today = datetime.utcnow().date()
            staff.actions_today = sum(1 for a in staff_actions_db.values()
                                    if a.staff_id == staff.staff_id 
                                    and a.timestamp.date() == today)
            
            # Get last action time
            staff_actions = [a for a in staff_actions_db.values() 
                           if a.staff_id == staff.staff_id]
            if staff_actions:
                staff.last_action = max(a.timestamp for a in staff_actions)
            
            # Estimate workload (simplified)
            base_workload = (staff.actions_today / 50) * 100  # Scale to 50 actions as full
            emergency_workload = staff.active_emergencies * 20
            staff.workload_percent = min(100, base_workload + emergency_workload)
        
        total_workload = sum(s.workload_percent for s in staff_workload.values()) / len(staff_workload) if staff_workload else 0
        
        critical_alerts = sum(1 for n in notification_service.notifications_db.values()
                            if n.priority == "CRITICAL" and not n.read)
        
        return StaffWorkloadResponse(
            active_staff=active_staff,
            staff_members=list(staff_workload.values()),
            total_workload_percent=round(total_workload, 1),
            critical_alerts_pending=critical_alerts,
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def _log_action(
        staff_id: str, action_type: str, related_entity_id: str,
        reason: str, affected_users: Optional[int] = None,
        duration_seconds: Optional[int] = None, notes: Optional[str] = None
    ) -> None:
        """Log a staff action for audit trail"""
        import random
        import string
        
        action_id = f"act-{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        
        action = StaffActionLog(
            action_id=action_id,
            timestamp=datetime.utcnow(),
            staff_id=staff_id,
            action_type=action_type,
            related_entity_id=related_entity_id,
            reason=reason,
            affected_users=affected_users,
            duration_seconds=duration_seconds,
            notes=notes
        )
        
        staff_actions_db[action_id] = action

    @staticmethod
    def clear_all() -> None:
        """Clear all data (for testing)"""
        staff_actions_db.clear()
        gate_capacity_overrides.clear()
