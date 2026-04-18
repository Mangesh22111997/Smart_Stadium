"""
Emergency Service - Business logic for emergency handling
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from app.models.emergency import Emergency, EmergencySOSRequest, EmergencyStatusUpdateRequest

# ============================================================================
# EXIT NETWORK DATABASE
# ============================================================================

EXIT_NETWORK = {
    "gate_a": [("exit_1", 50), ("exit_4", 100), ("exit_main", 150)],
    "gate_b": [("exit_2", 60), ("exit_1", 120), ("exit_main", 140)],
    "gate_c": [("exit_3", 55), ("exit_2", 110), ("exit_main", 160)],
    "gate_d": [("exit_4", 65), ("exit_3", 100), ("exit_main", 170)],
    "gate_center": [("exit_main", 40), ("exit_1", 100), ("exit_2", 100)],
    "pillar_1": [("exit_1", 80), ("exit_main", 60)],
    "pillar_2": [("exit_2", 75), ("exit_main", 70)],
    "pillar_3": [("exit_3", 70), ("exit_main", 80)],
    "pillar_4": [("exit_4", 85), ("exit_main", 90)],
    "center": [("exit_main", 40)],
}

# Emergency priority levels
EMERGENCY_PRIORITY = {
    "medical": "CRITICAL",
    "fire": "CRITICAL",
    "crowd": "CRITICAL",
    "threat": "CRITICAL",
    "lost_child": "HIGH",
    "harassment": "HIGH",
    "evacuation": "HIGH",
    "lost": "MEDIUM",
    "other": "LOW"
}

# ============================================================================
# EMERGENCY DATABASE
# ============================================================================

emergencies_db: Dict[UUID, Emergency] = {}
user_emergencies: Dict[UUID, List[UUID]] = {}


# ============================================================================
# EMERGENCY SERVICE CLASS
# ============================================================================

class EmergencyService:
    """
    Service class for managing emergency incidents
    """

    @staticmethod
    def _find_nearest_exit(location: str) -> Tuple[str, int]:
        """
        Find nearest exit from location
        
        Args:
            location: Current location
            
        Returns:
            Tuple of (exit_id, distance_in_meters)
        """
        if location not in EXIT_NETWORK:
            return ("exit_main", 100)  # Default fallback
        
        exits = EXIT_NETWORK[location]
        # Already sorted by distance (closest first)
        return exits[0] if exits else ("exit_main", 100)

    @staticmethod
    def _get_priority_level(emergency_type: str) -> str:
        """
        Get priority level for emergency type
        
        Args:
            emergency_type: Type of emergency
            
        Returns:
            Priority level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        return EMERGENCY_PRIORITY.get(emergency_type, "LOW")

    @staticmethod
    def trigger_sos(request: EmergencySOSRequest) -> Emergency:
        """
        Trigger an emergency SOS
        
        Args:
            request: EmergencySOSRequest with emergency details
            
        Returns:
            Created Emergency object
        """
        # Find nearest exit
        exit_id, distance = EmergencyService._find_nearest_exit(request.location)
        
        # Get priority level
        priority = EmergencyService._get_priority_level(request.emergency_type)
        
        # Create emergency
        emergency_id = uuid4()
        emergency = Emergency(
            emergency_id=emergency_id,
            user_id=request.user_id,
            emergency_type=request.emergency_type,
            location=request.location,
            description=request.description,
            nearest_exit=exit_id,
            exit_distance_meters=distance,
            status="reported",
            priority_level=priority,
            staff_assigned=None,
            reported_at=datetime.now(),
            resolved_at=None
        )
        
        # Store emergency
        emergencies_db[emergency_id] = emergency
        
        # Track in user emergencies
        if request.user_id not in user_emergencies:
            user_emergencies[request.user_id] = []
        user_emergencies[request.user_id].append(emergency_id)
        
        print(f"🚨 EMERGENCY REPORTED: {emergency_id}")
        print(f"   Type: {request.emergency_type} | Priority: {priority}")
        print(f"   Location: {request.location} | Nearest Exit: {exit_id} ({distance}m)")
        
        return emergency

    @staticmethod
    def get_emergency(emergency_id: UUID) -> Optional[Emergency]:
        """
        Get emergency by ID
        
        Args:
            emergency_id: Emergency ID
            
        Returns:
            Emergency or None if not found
        """
        return emergencies_db.get(emergency_id)

    @staticmethod
    def get_user_emergencies(user_id: UUID) -> List[Emergency]:
        """
        Get all emergencies for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of Emergency objects
        """
        emergency_ids = user_emergencies.get(user_id, [])
        return [emergencies_db[eid] for eid in emergency_ids if eid in emergencies_db]

    @staticmethod
    def get_active_emergencies() -> List[Emergency]:
        """
        Get all active emergencies
        
        Returns:
            List of active Emergency objects
        """
        return [
            e for e in emergencies_db.values()
            if e.status in ["reported", "responding"]
        ]

    @staticmethod
    def get_emergencies_by_priority(priority: str) -> List[Emergency]:
        """
        Get emergencies by priority level
        
        Args:
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
            
        Returns:
            List of matching emergencies
        """
        return [
            e for e in emergencies_db.values()
            if e.priority_level == priority and e.status != "cancelled"
        ]

    @staticmethod
    def update_emergency_status(
        emergency_id: UUID,
        request: EmergencyStatusUpdateRequest
    ) -> Optional[Emergency]:
        """
        Update emergency status
        
        Args:
            emergency_id: Emergency ID
            request: Status update request
            
        Returns:
            Updated Emergency or None if not found
        """
        if emergency_id not in emergencies_db:
            return None
        
        emergency = emergencies_db[emergency_id]
        old_status = emergency.status
        emergency.status = request.status
        
        # Set resolved_at if resolving
        if request.status == "resolved" and emergency.resolved_at is None:
            emergency.resolved_at = datetime.now()
        
        print(f"✅ Emergency updated: {emergency_id}")
        print(f"   Status: {old_status} → {request.status}")
        if request.notes:
            print(f"   Notes: {request.notes}")
        
        return emergency

    @staticmethod
    def assign_staff(emergency_id: UUID, staff_id: str) -> Optional[Emergency]:
        """
        Assign staff to emergency
        
        Args:
            emergency_id: Emergency ID
            staff_id: Staff identifier
            
        Returns:
            Updated Emergency or None if not found
        """
        if emergency_id not in emergencies_db:
            return None
        
        emergency = emergencies_db[emergency_id]
        emergency.staff_assigned = staff_id
        emergency.status = "responding"
        
        print(f"✅ Staff assigned: {staff_id} to emergency {emergency_id}")
        return emergency

    @staticmethod
    def find_nearest_exit(location: str) -> Dict:
        """
        Find nearest exit from location
        
        Args:
            location: Current location
            
        Returns:
            Dictionary with exit details
        """
        if location not in EXIT_NETWORK:
            return {
                "exit_id": "exit_main",
                "location": location,
                "distance_meters": 100,
                "direction": "Main Emergency Exit",
                "coordinates": None
            }
        
        exits = EXIT_NETWORK[location]
        exit_id, distance = exits[0]
        
        # Determine direction (simplified)
        directions = {
            "exit_1": "North",
            "exit_2": "East",
            "exit_3": "South",
            "exit_4": "West",
            "exit_main": "Central"
        }
        
        direction = directions.get(exit_id, "Nearest Emergency Exit")
        
        return {
            "exit_id": exit_id,
            "location": location,
            "distance_meters": distance,
            "direction": direction,
            "coordinates": None  # Could add GPS coordinates if available
        }

    @staticmethod
    def get_emergency_statistics() -> Dict:
        """
        Get emergency statistics
        
        Returns:
            Dictionary with emergency statistics
        """
        active = EmergencyService.get_active_emergencies()
        
        priority_counts = {
            "CRITICAL": len(EmergencyService.get_emergencies_by_priority("CRITICAL")),
            "HIGH": len(EmergencyService.get_emergencies_by_priority("HIGH")),
            "MEDIUM": len(EmergencyService.get_emergencies_by_priority("MEDIUM")),
            "LOW": len(EmergencyService.get_emergencies_by_priority("LOW"))
        }
        
        type_counts = {}
        for emergency in emergencies_db.values():
            etype = emergency.emergency_type
            type_counts[etype] = type_counts.get(etype, 0) + 1
        
        return {
            "total_emergencies": len(emergencies_db),
            "active_emergencies": len(active),
            "by_priority": priority_counts,
            "by_type": type_counts
        }

    @staticmethod
    def clear_all():
        """
        Clear all emergencies (for testing)
        """
        emergencies_db.clear()
        user_emergencies.clear()
        print("✅ All emergencies cleared")
