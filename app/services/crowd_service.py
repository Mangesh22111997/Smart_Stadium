"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
Crowd Service - Business logic for crowd monitoring and simulation
"""
from datetime import datetime
from typing import Dict, List, Optional
import random

from app.models.crowd import CrowdData, CrowdUpdateRequest

# ============================================================================
# IN-MEMORY CROWD DATABASE (linked to gates)
# ============================================================================

crowd_db: Dict[str, CrowdData] = {
    "A": CrowdData(
        gate_id="A",
        current_crowd=0,
        peak_capacity=100,
        congestion_level="low",
        capacity_percent=0.0,
        estimated_entry_time_minutes=0.0,
        flow_rate=20,
        trend="stable",
        last_updated=datetime.now(),
        previous_crowd=0
    ),
    "B": CrowdData(
        gate_id="B",
        current_crowd=0,
        peak_capacity=100,
        congestion_level="low",
        capacity_percent=0.0,
        estimated_entry_time_minutes=0.0,
        flow_rate=20,
        trend="stable",
        last_updated=datetime.now(),
        previous_crowd=0
    ),
    "C": CrowdData(
        gate_id="C",
        current_crowd=0,
        peak_capacity=100,
        congestion_level="low",
        capacity_percent=0.0,
        estimated_entry_time_minutes=0.0,
        flow_rate=20,
        trend="stable",
        last_updated=datetime.now(),
        previous_crowd=0
    ),
    "D": CrowdData(
        gate_id="D",
        current_crowd=0,
        peak_capacity=100,
        congestion_level="low",
        capacity_percent=0.0,
        estimated_entry_time_minutes=0.0,
        flow_rate=20,
        trend="stable",
        last_updated=datetime.now(),
        previous_crowd=0
    ),
}


# ============================================================================
# CROWD SERVICE CLASS
# ============================================================================

class CrowdService:
    """
    Service class for managing crowd monitoring
    """

    @staticmethod
    def _calculate_metrics(gate_id: str, current_crowd: int) -> tuple:
        """
        Calculate congestion metrics based on crowd
        
        Args:
            gate_id: Gate identifier
            current_crowd: Current number of people
            
        Returns:
            Tuple of (congestion_level, capacity_percent, entry_time, flow_rate)
        """
        crowd_data = crowd_db[gate_id]
        peak_capacity = crowd_data.peak_capacity
        
        # Calculate capacity percentage
        capacity_percent = (current_crowd / peak_capacity) * 100
        
        # Determine congestion level
        if capacity_percent >= 90:
            congestion_level = "critical"
        elif capacity_percent >= 75:
            congestion_level = "high"
        elif capacity_percent >= 50:
            congestion_level = "medium"
        else:
            congestion_level = "low"
        
        # Calculate entry time (in minutes)
        # Formula: (crowd / capacity) * 30 minutes (max expected wait)
        entry_time = (capacity_percent / 100) * 30
        
        # Calculate flow rate (people per minute)
        if congestion_level == "critical":
            flow_rate = random.randint(2, 4)
        elif congestion_level == "high":
            flow_rate = random.randint(5, 10)
        elif congestion_level == "medium":
            flow_rate = random.randint(10, 15)
        else:  # low
            flow_rate = random.randint(15, 20)
        
        return congestion_level, capacity_percent, entry_time, flow_rate

    @staticmethod
    def _calculate_trend(gate_id: str, current_crowd: int) -> str:
        """
        Calculate trend based on previous crowd
        
        Args:
            gate_id: Gate identifier
            current_crowd: Current crowd count
            
        Returns:
            Trend string (increasing, stable, decreasing)
        """
        previous_crowd = crowd_db[gate_id].previous_crowd
        
        # Calculate percentage change
        if previous_crowd == 0:
            return "stable"
        
        percent_change = ((current_crowd - previous_crowd) / previous_crowd) * 100
        
        if percent_change > 2:
            return "increasing"
        elif percent_change < -2:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def update_crowd(gate_id: str, new_crowd: int) -> Optional[CrowdData]:
        """
        Update crowd count for a gate
        
        Args:
            gate_id: Gate identifier
            new_crowd: New crowd count
            
        Returns:
            Updated CrowdData or None if gate not found
        """
        if gate_id not in crowd_db:
            return None
        
        crowd_data = crowd_db[gate_id]
        
        # Store previous for trend
        crowd_data.previous_crowd = crowd_data.current_crowd
        
        # Ensure crowd doesn't exceed capacity
        crowd_data.current_crowd = min(new_crowd, crowd_data.peak_capacity)
        
        # Calculate metrics
        congestion_level, capacity_percent, entry_time, flow_rate = \
            CrowdService._calculate_metrics(gate_id, crowd_data.current_crowd)
        
        # Calculate trend
        trend = CrowdService._calculate_trend(gate_id, crowd_data.current_crowd)
        
        # Update data
        crowd_data.congestion_level = congestion_level
        crowd_data.capacity_percent = capacity_percent
        crowd_data.estimated_entry_time_minutes = entry_time
        crowd_data.flow_rate = flow_rate
        crowd_data.trend = trend
        crowd_data.last_updated = datetime.now()
        
        print(f"✅ Crowd updated: Gate {gate_id} = {crowd_data.current_crowd} ({congestion_level})")
        return crowd_data

    @staticmethod
    def simulate_crowd_update() -> Dict[str, CrowdData]:
        """
        Simulate crowd updates for all gates
        Random changes within realistic bounds
        
        Returns:
            Dictionary of updated CrowdData for all gates
        """
        updated_gates = {}
        
        for gate_id in ["A", "B", "C", "D"]:
            crowd_data = crowd_db[gate_id]
            current = crowd_data.current_crowd
            
            # 60% chance of increase, 40% chance of decrease
            if random.random() < 0.6:
                # People arriving
                change = random.randint(5, 15)
            else:
                # People leaving
                change = -random.randint(3, 8)
            
            # Calculate new crowd
            new_crowd = max(0, current + change)  # Can't go below 0
            new_crowd = min(new_crowd, crowd_data.peak_capacity)  # Can't exceed capacity
            
            # Update crowd
            updated = CrowdService.update_crowd(gate_id, new_crowd)
            updated_gates[gate_id] = updated
        
        print("✅ Crowd simulation completed for all gates")
        return updated_gates

    @staticmethod
    def get_crowd_status(gate_id: str) -> Optional[CrowdData]:
        """
        Get current crowd status for a gate
        
        Args:
            gate_id: Gate identifier
            
        Returns:
            CrowdData or None if gate not found
        """
        return crowd_db.get(gate_id)

    @staticmethod
    def get_all_crowd_status() -> Dict:
        """
        Get crowd status for all gates
        
        Returns:
            Dictionary with all gates and system metrics
        """
        gates_status = []
        total_crowd = 0
        total_capacity = 0
        congestion_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for gate_id in ["A", "B", "C", "D"]:
            crowd_data = crowd_db[gate_id]
            gates_status.append(crowd_data)
            total_crowd += crowd_data.current_crowd
            total_capacity += crowd_data.peak_capacity
            congestion_counts[crowd_data.congestion_level] += 1
        
        system_utilization = (total_crowd / total_capacity * 100) if total_capacity > 0 else 0
        
        # Determine average congestion
        if congestion_counts["critical"] > 0:
            avg_congestion = "critical"
        elif congestion_counts["high"] > 0:
            avg_congestion = "high"
        elif congestion_counts["medium"] > 0:
            avg_congestion = "medium"
        else:
            avg_congestion = "low"
        
        return {
            "gates": gates_status,
            "total_crowd": total_crowd,
            "total_capacity": total_capacity,
            "system_utilization_percent": round(system_utilization, 2),
            "average_congestion_level": avg_congestion,
            "congestion_counts": congestion_counts
        }

    @staticmethod
    def get_crowd_metrics() -> Dict:
        """
        Get detailed crowd metrics across system
        
        Returns:
            Dictionary with crowd metrics
        """
        all_status = CrowdService.get_all_crowd_status()
        gates_status = all_status["gates"]
        
        # Calculate averages
        avg_entry_time = sum(g.estimated_entry_time_minutes for g in gates_status) / 4
        total_flow_rate = sum(g.flow_rate for g in gates_status)
        
        return {
            "total_crowd": all_status["total_crowd"],
            "total_capacity": all_status["total_capacity"],
            "system_utilization_percent": all_status["system_utilization_percent"],
            "average_entry_time_minutes": round(avg_entry_time, 2),
            "total_flow_rate": total_flow_rate,
            "gates_critical": all_status["congestion_counts"]["critical"],
            "gates_high": all_status["congestion_counts"]["high"],
            "gates_medium": all_status["congestion_counts"]["medium"],
            "gates_low": all_status["congestion_counts"]["low"]
        }

    @staticmethod
    def manual_crowd_change(gate_id: str, request: CrowdUpdateRequest) -> Optional[CrowdData]:
        """
        Manually change crowd count for a gate
        
        Args:
            gate_id: Gate identifier
            request: CrowdUpdateRequest with change amount
            
        Returns:
            Updated CrowdData or None if gate not found
        """
        if gate_id not in crowd_db:
            return None
        
        crowd_data = crowd_db[gate_id]
        new_crowd = crowd_data.current_crowd + request.crowd_change
        
        return CrowdService.update_crowd(gate_id, max(0, new_crowd))

    @staticmethod
    def sync_with_gate(gate_id: str, gate_assignment_count: int):
        """
        Sync crowd data with gate assignment count
        
        Args:
            gate_id: Gate identifier
            gate_assignment_count: Number of people assigned to gate
        """
        if gate_id in crowd_db:
            CrowdService.update_crowd(gate_id, gate_assignment_count)

    @staticmethod
    def clear_all():
        """
        Clear all crowd data (for testing)
        """
        for gate_id in crowd_db:
            crowd_db[gate_id].current_crowd = 0
            crowd_db[gate_id].previous_crowd = 0
            crowd_db[gate_id].congestion_level = "low"
        print("✅ All crowd data cleared")
