# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Reassignment Service - Business logic for dynamic gate reassignment
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from app.models.reassignment import Reassignment, ManualReassignmentRequest
from app.services.gate_service import GateService
from app.services.crowd_service import CrowdService

# ============================================================================
# IN-MEMORY REASSIGNMENT DATABASE
# ============================================================================

reassignments_db: List[Reassignment] = []
ticket_reassignments: Dict[UUID, List[UUID]] = {}  # track reassignments per ticket


# ============================================================================
# REASSIGNMENT SERVICE CLASS
# ============================================================================

class ReassignmentService:
    """
    Service class for managing dynamic gate reassignments
    """

    # Gate proximity mapping
    NEARBY_GATES = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["D", "A"],
        "D": ["C", "B"]
    }

    @staticmethod
    def _calculate_gate_score(gate_id: str, current_gate_id: str) -> float:
        """
        Calculate score for target gate (lower is better)
        
        Args:
            gate_id: Target gate to evaluate
            current_gate_id: Current gate
            
        Returns:
            Score based on congestion, proximity, etc.
        """
        crowd_data = CrowdService.get_crowd_status(gate_id)
        if not crowd_data:
            return float('inf')
        
        # Base score: congestion percentage
        score = crowd_data.capacity_percent
        
        # Bonus if nearby gate
        if gate_id in ReassignmentService.NEARBY_GATES.get(current_gate_id, []):
            score -= 5  # Prefer nearby gates
        
        return score

    @staticmethod
    def _find_best_target_gate(from_gate_id: str) -> Optional[str]:
        """
        Find best target gate for reassignment
        
        Args:
            from_gate_id: Current gate
            
        Returns:
            Best target gate ID or None
        """
        # Get nearby gates
        nearby = ReassignmentService.NEARBY_GATES.get(from_gate_id, ["A", "B", "C", "D"])
        
        best_gate = None
        best_score = float('inf')
        
        for gate_id in nearby + ["A", "B", "C", "D"]:
            crowd_data = CrowdService.get_crowd_status(gate_id)
            if not crowd_data:
                continue
            
            # Skip if target gate is full or critical
            if crowd_data.capacity_percent >= 90:
                continue
            
            # Skip if target gate has similar or worse congestion
            from_crowd = CrowdService.get_crowd_status(from_gate_id)
            if from_crowd and crowd_data.capacity_percent >= from_crowd.capacity_percent - 15:
                continue
            
            score = ReassignmentService._calculate_gate_score(gate_id, from_gate_id)
            
            if score < best_score:
                best_score = score
                best_gate = gate_id
        
        return best_gate

    @staticmethod
    def _get_reassignments_from_gate(gate_id: str) -> List[UUID]:
        """
        Get list of tickets assigned to a gate that could be reassigned
        
        Args:
            gate_id: Gate ID
            
        Returns:
            List of ticket IDs
        """
        assignments = GateService.get_gate_assignments(gate_id)
        return [a.ticket_id for a in assignments]

    @staticmethod
    def check_and_reassign_all() -> Dict:
        """
        Check all gates for high congestion and auto-reassign if needed
        
        Returns:
            Dictionary with reassignment details
        """
        reassignments_made = []
        gates_checked = 0
        gates_high = 0
        
        for gate_id in ["A", "B", "C", "D"]:
            gates_checked += 1
            crowd_data = CrowdService.get_crowd_status(gate_id)
            
            if not crowd_data:
                continue
            
            # Check if gate is in high congestion (>75%) or critical (>85%)
            if crowd_data.capacity_percent >= 75:
                gates_high += 1
                
                # Get tickets to potentially reassign
                tickets = ReassignmentService._get_reassignments_from_gate(gate_id)
                
                # Reassign up to 50% of tickets at high congestion
                reassign_count = max(1, len(tickets) // 2)
                
                for i in range(min(reassign_count, len(tickets))):
                    ticket_id = tickets[i]
                    
                    # Get assignment details
                    assignment = GateService.get_assignment(ticket_id)
                    if not assignment:
                        continue
                    
                    # Find best target gate
                    target_gate = ReassignmentService._find_best_target_gate(gate_id)
                    if not target_gate or target_gate == gate_id:
                        continue
                    
                    # Perform reassignment
                    reason = f"Automatic: High congestion at Gate {gate_id} ({crowd_data.capacity_percent:.1f}%)"
                    reassignment = ReassignmentService.reassign(
                        ticket_id,
                        target_gate,
                        reason
                    )
                    
                    if reassignment:
                        reassignments_made.append(reassignment)
        
        return {
            "reassignments_made": len(reassignments_made),
            "gates_checked": gates_checked,
            "gates_with_high_congestion": gates_high,
            "message": f"Checked {gates_checked} gates, made {len(reassignments_made)} reassignments",
            "details": reassignments_made
        }

    @staticmethod
    def reassign(ticket_id: UUID, new_gate_id: str, reason: str) -> Optional[Reassignment]:
        """
        Reassign a ticket to a new gate
        
        Args:
            ticket_id: Ticket to reassign
            new_gate_id: New gate
            reason: Reason for reassignment
            
        Returns:
            Reassignment object or None if failed
        """
        # Get current assignment
        current_assignment = GateService.get_assignment(ticket_id)
        if not current_assignment:
            return None
        
        from_gate_id = current_assignment.gate_id
        
        # Get congestion before
        from_crowd = CrowdService.get_crowd_status(from_gate_id)
        congestion_before = from_crowd.capacity_percent if from_crowd else 0
        
        # Reassign in gate service
        GateService.reassign_gate(ticket_id, new_gate_id)
        
        # Get congestion after
        to_crowd = CrowdService.get_crowd_status(new_gate_id)
        congestion_after = to_crowd.capacity_percent if to_crowd else 0
        
        # Calculate disruption score (improvement achieved)
        disruption_score = congestion_before - congestion_after  # Higher is better
        
        # Create reassignment record
        reassignment = Reassignment(
            reassignment_id=uuid4(),
            ticket_id=ticket_id,
            user_id=current_assignment.user_id,
            from_gate=from_gate_id,
            to_gate=new_gate_id,
            reason=reason,
            reassigned_at=datetime.now(),
            congestion_before_percent=congestion_before,
            congestion_after_percent=congestion_after,
            disruption_score=disruption_score
        )
        
        # Store reassignment
        reassignments_db.append(reassignment)
        
        # Track in ticket history
        if ticket_id not in ticket_reassignments:
            ticket_reassignments[ticket_id] = []
        ticket_reassignments[ticket_id].append(reassignment.reassignment_id)
        
        print(f"✅ Reassignment: Ticket {ticket_id} moved {from_gate_id}→{new_gate_id} ({congestion_before:.1f}%→{congestion_after:.1f}%)")
        return reassignment

    @staticmethod
    def manual_reassign(request: ManualReassignmentRequest) -> Optional[Reassignment]:
        """
        Manually reassign a ticket to a different gate
        
        Args:
            request: ManualReassignmentRequest
            
        Returns:
            Reassignment object or None if failed
        """
        # Validate new gate
        if request.new_gate_id not in ["A", "B", "C", "D"]:
            return None
        
        # Reassign
        return ReassignmentService.reassign(
            request.ticket_id,
            request.new_gate_id,
            request.reason
        )

    @staticmethod
    def get_reassignment(reassignment_id: UUID) -> Optional[Reassignment]:
        """
        Get reassignment by ID
        
        Args:
            reassignment_id: Reassignment ID
            
        Returns:
            Reassignment or None if not found
        """
        for reassignment in reassignments_db:
            if reassignment.reassignment_id == reassignment_id:
                return reassignment
        return None

    @staticmethod
    def get_ticket_reassignments(ticket_id: UUID) -> List[Reassignment]:
        """
        Get all reassignments for a ticket
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            List of Reassignment objects
        """
        result = []
        for reassignment in reassignments_db:
            if reassignment.ticket_id == ticket_id:
                result.append(reassignment)
        return result

    @staticmethod
    def get_gate_reassignments(gate_id: str) -> List[Reassignment]:
        """
        Get all reassignments from a gate
        
        Args:
            gate_id: Gate ID
            
        Returns:
            List of Reassignment objects
        """
        result = []
        for reassignment in reassignments_db:
            if reassignment.from_gate == gate_id:
                result.append(reassignment)
        return result

    @staticmethod
    def get_all_reassignments() -> List[Reassignment]:
        """
        Get all reassignments
        
        Returns:
            List of all Reassignment objects
        """
        return reassignments_db.copy()

    @staticmethod
    def clear_all():
        """
        Clear all reassignment records (for testing)
        """
        reassignments_db.clear()
        ticket_reassignments.clear()
        print("✅ All reassignments cleared")
