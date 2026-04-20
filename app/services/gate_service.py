# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Gate Service - Business logic for gate assignment
ML-Enhanced with predictive gate load forecasting
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from app.models.gate import Gate, GateAssignment, GateAssignmentRequest

# ML Inference
try:
    from app.ml.inference_server import get_inference_server
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False
    print("⚠️  ML models not available, using rule-based logic")

# ============================================================================
# IN-MEMORY GATE DATABASE
# ============================================================================

gates_db: Dict[str, Gate] = {
    "A": Gate(gate_id="A", current_count=0, max_capacity=100),
    "B": Gate(gate_id="B", current_count=0, max_capacity=100),
    "C": Gate(gate_id="C", current_count=0, max_capacity=100),
    "D": Gate(gate_id="D", current_count=0, max_capacity=100),
}

# Track assignments for quick lookup
ticket_assignments: Dict[UUID, GateAssignment] = {}


# ============================================================================
# GATE SERVICE CLASS
# ============================================================================

class GateService:
    """
    Service class for managing gate assignments
    """

    @staticmethod
    def _get_primary_gates(commute_mode: str) -> List[str]:
        """
        Get primary gates based on commute mode
        
        Args:
            commute_mode: Type of commute (metro, bus, private, cab)
            
        Returns:
            Ordered list of primary gate IDs
        """
        if commute_mode == "metro":
            return ["A", "B"]
        elif commute_mode == "bus":
            return ["C", "D"]
        else:  # private, cab
            return ["A", "B", "C", "D"]

    @staticmethod
    def _get_preference_gates(departure_preference: str) -> List[str]:
        """
        Get gate preference order based on departure preference
        
        Args:
            departure_preference: When user wants to depart (early, immediate, delayed)
            
        Returns:
            Ordered list of gate IDs
        """
        if departure_preference == "early":
            return ["A", "B", "C", "D"]  # Start from beginning
        elif departure_preference == "delayed":
            return ["D", "C", "B", "A"]  # Start from end
        else:  # immediate
            return ["B", "C", "A", "D"]  # Balanced

    @staticmethod
    def predict_gate_load_ml(gate_id: str, forecast_horizon: int = 10) -> Optional[Dict]:
        """
        Use ML model to predict queue depth at a gate
        
        Args:
            gate_id: Gate identifier
            forecast_horizon: Minutes ahead to predict (10 or 30)
        
        Returns:
            Prediction dict or None if ML not available
        """
        if not ML_ENABLED:
            return None
        
        try:
            server = get_inference_server()
            gate = gates_db[gate_id]
            
            # Build context for prediction
            prediction = server.predict_gate_load(
                gate_id=gate_id,
                timestamp_minute=0,  # Assuming event end (now)
                attendees_passed=gate.attendees_exited if hasattr(gate, 'attendees_exited') else 0,
                weather=getattr(gate, 'weather', 'clear'),
                event_type=getattr(gate, 'event_type', 'football'),
                day_of_week=datetime.now().weekday(),
                queue_depth=gate.current_count
            )
            return prediction
        except Exception as e:
            print(f"⚠️  ML prediction failed for gate {gate_id}: {e}")
            return None

    @staticmethod
    def assign_gate(request: GateAssignmentRequest) -> GateAssignment:
        """
        Assign a gate to a user based on commute mode and preference
        ML-Enhanced: Uses predictive gate load models when available
        
        Args:
            request: GateAssignmentRequest with user and preferences
            
        Returns:
            GateAssignment object with assigned gate
        """
        # Get preferred gates based on commute mode
        primary_gates = GateService._get_primary_gates(request.commute_mode)
        
        # Get preference-based ordering
        preference_gates = GateService._get_preference_gates(request.departure_preference)
        
        # Score gates based on both mode and preference
        gate_scores = {}
        ml_predictions = {}
        
        for gate_id in ["A", "B", "C", "D"]:
            gate = gates_db[gate_id]
            utilization = gate.current_count / gate.max_capacity
            
            # Base score: lower is better
            score = utilization * 100
            
            # Get ML prediction if available
            ml_pred = GateService.predict_gate_load_ml(gate_id, forecast_horizon=10)
            ml_predictions[gate_id] = ml_pred
            
            if ml_pred:  # ML-enhanced scoring
                # Incorporate predicted queue depth (30-minute lookahead)
                predicted_queue_t30 = ml_pred.get('predicted_queue_t30', 0)
                
                # Penalize gates with high predicted load
                predicted_utilization = predicted_queue_t30 / 100  # Normalized to 100-person capacity
                ml_score_component = predicted_utilization * 50  # Weight ML prediction
                
                score += ml_score_component
                
                # Strong penalty if ML predicts reroute needed
                if ml_pred.get('should_proactive_reroute', False):
                    score += 100  # Heavy penalty - avoid this gate
            
            # Bonus if gate matches commute mode
            if gate_id in primary_gates:
                score -= 10  # Prefer primary gates
            
            # Bonus if gate matches departure preference
            if gate_id in preference_gates[:2]:
                score -= 5  # Prefer based on departure time
            
            gate_scores[gate_id] = score
        
        # Find best gate (lowest score)
        assigned_gate_id = min(gate_scores.keys(), key=lambda x: gate_scores[x])
        assigned_gate = gates_db[assigned_gate_id]
        
        # Check if gate is critical (>90% full)
        utilization = assigned_gate.current_count / assigned_gate.max_capacity
        
        # Prevent assignment if gate is over capacity
        if utilization >= 1.0:
            # Try any non-full gate
            for gate_id in ["A", "B", "C", "D"]:
                gate = gates_db[gate_id]
                if gate.current_count < gate.max_capacity:
                    assigned_gate_id = gate_id
                    assigned_gate = gate
                    break
        
        # Update gate assignment
        assigned_gate.current_count += 1
        
        # Create assignment record
        assignment = GateAssignment(
            ticket_id=request.ticket_id,
            user_id=request.user_id,
            gate_id=assigned_gate_id,
            commute_mode=request.commute_mode,
            departure_preference=request.departure_preference,
            assigned_at=datetime.now(),
            assignment_reason=GateService._get_assignment_reason(
                request.commute_mode,
                request.departure_preference,
                assigned_gate_id,
                utilization,
                ml_predictions=ml_predictions
            )
        )
        
        # Store assignment
        ticket_assignments[request.ticket_id] = assignment
        assigned_gate.assignments[request.ticket_id] = assignment
        
        # Log with ML context if available
        ml_context = f" [ML: pred_q10={ml_predictions[assigned_gate_id].get('predicted_queue_t10', 'N/A') if ml_predictions[assigned_gate_id] else 'N/A'}]" if ML_ENABLED else ""
        print(f"✅ Gate assigned: {assigned_gate_id} to user {request.user_id} (Ticket: {request.ticket_id}){ml_context}")
        
        # Real-time Push Notification via FCM
        try:
            from app.services.fcm_service import FCMService
            from app.config.firebase_config import get_db_connection, Collections
            
            db = get_db_connection()
            # Retrieve user's FCM token (stored at registration)
            user_fcm_token = db.child(Collections.USERS).child(str(request.user_id)).child("fcm_token").get().val()
            
            if user_fcm_token:
                FCMService.send_gate_notification(
                    fcm_token=user_fcm_token,
                    gate_id=assigned_gate_id,
                    queue_depth=assigned_gate.current_count
                )
                print(f"📲 FCM notification sent to user {request.user_id}")
        except Exception as e:
            # Non-blocking FCM failure
            print(f"⚠️ FCM notification failed: {e}")
            
        return assignment

    @staticmethod
    def _get_assignment_reason(commute_mode: str, departure_preference: str, gate_id: str, utilization: float, ml_predictions: Dict = None) -> str:
        """
        Generate human-readable reason for gate assignment
        Enhanced with ML prediction context
        """
        reasons = []
        
        # Commute mode reason
        if commute_mode == "metro" and gate_id in ["A", "B"]:
            reasons.append(f"Metro users prefer Gate {gate_id}")
        elif commute_mode == "bus" and gate_id in ["C", "D"]:
            reasons.append(f"Bus users prefer Gate {gate_id}")
        else:
            reasons.append(f"Best available gate")
        
        # Utilization reason
        congestion = GateService._get_congestion_level(utilization)
        reasons.append(f"{congestion} current congestion")
        
        # ML Prediction reason
        if ml_predictions and gate_id in ml_predictions and ml_predictions[gate_id]:
            pred = ml_predictions[gate_id]
            reasons.append(f"ML forecast: {pred.get('predicted_queue_t30', 'N/A')} people in 30min")
            if pred.get('should_proactive_reroute', False):
                reasons.append("(ML alerts: future overflow risk)")
        
        return " | ".join(reasons)

    @staticmethod
    def _get_congestion_level(utilization: float) -> str:
        """
        Get congestion level based on utilization percentage
        """
        if utilization >= 0.9:
            return "critical"
        elif utilization >= 0.75:
            return "high"
        elif utilization >= 0.5:
            return "medium"
        else:
            return "low"

    @staticmethod
    def get_gate_status(gate_id: str) -> Optional[Dict]:
        """
        Get status of a specific gate
        
        Args:
            gate_id: Gate identifier (A, B, C, D)
            
        Returns:
            Gate status dictionary or None if not found
        """
        if gate_id not in gates_db:
            return None
        
        gate = gates_db[gate_id]
        utilization = (gate.current_count / gate.max_capacity) * 100
        
        return {
            "gate_id": gate_id,
            "current_count": gate.current_count,
            "max_capacity": gate.max_capacity,
            "utilization_percent": round(utilization, 2),
            "congestion_level": GateService._get_congestion_level(utilization / 100),
            "capacity_remaining": gate.max_capacity - gate.current_count
        }

    @staticmethod
    def get_gate_status_ml_enhanced(gate_id: str) -> Optional[Dict]:
        """
        Get ML-enhanced status of a specific gate including predictions
        
        Args:
            gate_id: Gate identifier (A, B, C, D)
        
        Returns:
            Gate status dictionary with ML predictions or None if not found
        """
        status = GateService.get_gate_status(gate_id)
        if not status:
            return None
        
        # Add ML predictions
        if ML_ENABLED:
            pred_t10 = GateService.predict_gate_load_ml(gate_id, forecast_horizon=10)
            
            if pred_t10:
                status["ml_predictions"] = {
                    "predicted_queue_t10": pred_t10.get('predicted_queue_t10', 0),
                    "predicted_queue_t30": pred_t10.get('predicted_queue_t30', 0),
                    "should_reroute": pred_t10.get('should_proactive_reroute', False),
                    "reroute_urgency": pred_t10.get('reroute_urgency', 'LOW'),
                    "recommended_staff": pred_t10.get('recommended_staff_t10', 2)
                }
            else:
                status["ml_predictions"] = None
        else:
            status["ml_predictions"] = None
        
        return status

    @staticmethod
    def get_all_gates_status() -> Dict:
        """
        Get status of all gates
        
        Returns:
            Dictionary with all gates status
        """
        gates_status = []
        total_assigned = 0
        total_capacity = 0
        
        for gate_id in ["A", "B", "C", "D"]:
            status = GateService.get_gate_status(gate_id)
            gates_status.append(status)
            total_assigned += status["current_count"]
            total_capacity += status["max_capacity"]
        
        system_utilization = (total_assigned / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "gates": gates_status,
            "total_capacity": total_capacity,
            "total_assigned": total_assigned,
            "system_utilization_percent": round(system_utilization, 2)
        }

    @staticmethod
    def get_all_gates_status_ml_enhanced() -> Dict:
        """
        Get ML-enhanced status of all gates with predictions
        Useful for admin dashboard to show predicted congestion
        
        Returns:
            Dictionary with all gates status + ML predictions
        """
        gates_status = []
        total_assigned = 0
        total_capacity = 0
        total_reroute_alerts = 0
        
        for gate_id in ["A", "B", "C", "D"]:
            status = GateService.get_gate_status_ml_enhanced(gate_id)
            gates_status.append(status)
            total_assigned += status["current_count"]
            total_capacity += status["max_capacity"]
            
            if status.get("ml_predictions") and status["ml_predictions"].get("should_reroute"):
                total_reroute_alerts += 1
        
        system_utilization = (total_assigned / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "gates": gates_status,
            "total_capacity": total_capacity,
            "total_assigned": total_assigned,
            "system_utilization_percent": round(system_utilization, 2),
            "ml_enabled": ML_ENABLED,
            "reroute_alerts": total_reroute_alerts,
            "system_status": "CRITICAL" if total_reroute_alerts > 1 else ("WARNING" if total_reroute_alerts > 0 else "NORMAL")
        }

    @staticmethod
    def get_assignment(ticket_id: UUID) -> Optional[GateAssignment]:
        """
        Get assignment for a specific ticket
        
        Args:
            ticket_id: UUID of the ticket
            
        Returns:
            GateAssignment or None if not found
        """
        return ticket_assignments.get(ticket_id)

    @staticmethod
    def reassign_gate(ticket_id: UUID, new_gate_id: str) -> Optional[GateAssignment]:
        """
        Reassign a ticket to a different gate
        
        Args:
            ticket_id: UUID of the ticket
            new_gate_id: New gate identifier
            
        Returns:
            Updated GateAssignment or None if not found
        """
        if ticket_id not in ticket_assignments:
            return None
        
        assignment = ticket_assignments[ticket_id]
        old_gate_id = assignment.gate_id
        
        # Remove from old gate
        gates_db[old_gate_id].current_count -= 1
        if ticket_id in gates_db[old_gate_id].assignments:
            del gates_db[old_gate_id].assignments[ticket_id]
        
        # Add to new gate
        gates_db[new_gate_id].current_count += 1
        assignment.gate_id = new_gate_id
        assignment.assigned_at = datetime.now()
        assignment.assignment_reason = f"Reassigned from {old_gate_id} to {new_gate_id} due to congestion"
        
        gates_db[new_gate_id].assignments[ticket_id] = assignment
        
        print(f"✅ Gate reassigned: {old_gate_id} → {new_gate_id} for ticket {ticket_id}")
        
        # Real-time Push Notification for Rerouting
        try:
            from app.services.fcm_service import FCMService
            from app.config.firebase_config import get_db_connection, Collections
            
            db = get_db_connection()
            user_fcm_token = db.child(Collections.USERS).child(str(assignment.user_id)).child("fcm_token").get().val()
            
            if user_fcm_token:
                FCMService.send_crowd_warning(
                    fcm_token=user_fcm_token,
                    gate_id=old_gate_id,
                    capacity_percent=95,  # Threshold for reassignment
                    alternate_gate=new_gate_id
                )
                print(f"📲 FCM reroute warning sent to user {assignment.user_id}")
        except Exception as e:
            print(f"⚠️ FCM reroute notification failed: {e}")
            
        return assignment

    @staticmethod
    def get_gate_assignments(gate_id: str) -> List[GateAssignment]:
        """
        Get all assignments for a specific gate
        
        Args:
            gate_id: Gate identifier
            
        Returns:
            List of GateAssignment objects
        """
        if gate_id not in gates_db:
            return []
        
        return list(gates_db[gate_id].assignments.values())

    @staticmethod
    def clear_all():
        """
        Clear all assignments (for testing)
        """
        gates_db["A"].current_count = 0
        gates_db["B"].current_count = 0
        gates_db["C"].current_count = 0
        gates_db["D"].current_count = 0
        
        gates_db["A"].assignments.clear()
        gates_db["B"].assignments.clear()
        gates_db["C"].assignments.clear()
        gates_db["D"].assignments.clear()
        
        ticket_assignments.clear()
        print("✅ All gate assignments cleared")
