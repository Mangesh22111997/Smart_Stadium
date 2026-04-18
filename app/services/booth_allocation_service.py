"""
Booth Allocation Service - Smart booth allocation logic
"""
from typing import Dict, List, Optional, Literal
from app.models.booth_allocation import BoothAllocationData
from app.services.food_service import FoodService
from app.services.gate_service import GateService

# ============================================================================
# BOOTH DISTANCE MATRIX
# ============================================================================

DISTANCE_MATRIX = {
    "B01": {"pillar_1": 10, "pillar_2": 25, "pillar_3": 25, "pillar_4": 10, "center": 15},
    "B02": {"pillar_1": 15, "pillar_2": 15, "pillar_3": 25, "pillar_4": 25, "center": 15},
    "B03": {"pillar_1": 20, "pillar_2": 10, "pillar_3": 20, "pillar_4": 25, "center": 15},
    "B04": {"pillar_1": 25, "pillar_2": 25, "pillar_3": 10, "pillar_4": 15, "center": 15},
    "B05": {"pillar_1": 25, "pillar_2": 15, "pillar_3": 15, "pillar_4": 25, "center": 15},
}

# Zone preferences (which booths are primary)
ZONE_PREFERENCES = {
    "pillar_1": ["B01", "B02"],
    "pillar_2": ["B03", "B05", "B02"],
    "pillar_3": ["B04", "B05"],
    "pillar_4": ["B01", "B04"],
    "center": ["B01", "B02", "B03", "B04", "B05"],
}


# ============================================================================
# BOOTH ALLOCATION SERVICE CLASS
# ============================================================================

class BoothAllocationService:
    """
    Service class for smart booth allocation
    """

    @staticmethod
    def _get_distance_score(booth_id: str, zone: str) -> float:
        """
        Get distance score for booth from zone
        
        Args:
            booth_id: Booth identifier
            zone: User zone
            
        Returns:
            Distance score (0-30, lower is better)
        """
        if booth_id not in DISTANCE_MATRIX:
            return 30.0
        
        distance = DISTANCE_MATRIX[booth_id].get(zone, 30)
        
        # Convert distance to score (0-30)
        if distance <= 10:
            return 5.0
        elif distance <= 15:
            return 10.0
        elif distance <= 20:
            return 15.0
        else:
            return 25.0

    @staticmethod
    def _get_crowd_score(booth_id: str) -> float:
        """
        Get crowd score for booth
        
        Args:
            booth_id: Booth identifier
            
        Returns:
            Crowd score (0-150, lower is better)
        """
        booth_status = FoodService.get_booth_status(booth_id)
        if not booth_status:
            return 100.0
        
        utilization = booth_status["utilization_percent"]
        
        # Score based on crowd level
        if utilization >= 90:
            return 150.0  # Critical - avoid
        elif utilization >= 75:
            return utilization + 25  # High - increase score
        elif utilization >= 50:
            return utilization + 10  # Medium - slight increase
        else:
            return utilization  # Low - use actual percentage

    @staticmethod
    def _calculate_total_score(distance_score: float, crowd_score: float) -> float:
        """
        Calculate total allocation score
        
        Args:
            distance_score: Distance component (0-30)
            crowd_score: Crowd component (0-150)
            
        Returns:
            Total score (lower is better)
        """
        # Weighted combination
        # 60% crowd weight, 40% distance weight
        crowd_weight = 0.6
        distance_weight = 0.4
        
        total = (crowd_score * crowd_weight) + (distance_score * distance_weight)
        return round(total, 2)

    @staticmethod
    def _get_distance_category(distance: float) -> str:
        """
        Get distance category
        
        Args:
            distance: Distance value
            
        Returns:
            Distance category
        """
        if distance <= 10:
            return "very_close"
        elif distance <= 15:
            return "close"
        elif distance <= 20:
            return "medium"
        else:
            return "far"

    @staticmethod
    def allocate_booth(user_id: str, zone: str) -> Optional[BoothAllocationData]:
        """
        Find best booth for user based on zone and crowd
        
        Args:
            user_id: User identifier (for logging)
            zone: User's delivery zone
            
        Returns:
            BoothAllocationData with best booth or None
        """
        best_booth = None
        best_score = float('inf')
        
        # Get preferred booths for this zone
        preferred = ZONE_PREFERENCES.get(zone, ["B01", "B02", "B03", "B04", "B05"])
        
        # Score all booths
        booth_scores = {}
        
        for booth_id in ["B01", "B02", "B03", "B04", "B05"]:
            booth_status = FoodService.get_booth_status(booth_id)
            if not booth_status:
                continue
            
            # Get scores
            distance_score = BoothAllocationService._get_distance_score(booth_id, zone)
            crowd_score = BoothAllocationService._get_crowd_score(booth_id)
            
            # Skip if booth is critical and preferred booths available
            if crowd_score >= 150 and len(preferred) > 1:
                continue
            
            # Calculate total score
            total_score = BoothAllocationService._calculate_total_score(distance_score, crowd_score)
            
            booth_scores[booth_id] = {
                "distance_score": distance_score,
                "crowd_score": crowd_score,
                "total_score": total_score,
                "queue_size": booth_status["current_orders"],
                "estimated_wait": booth_status["estimated_wait_time"]
            }
            
            # Update best booth
            if total_score < best_score:
                best_score = total_score
                best_booth = booth_id
        
        if not best_booth:
            return None
        
        # Create allocation data
        scores = booth_scores[best_booth]
        distance = DISTANCE_MATRIX[best_booth].get(zone, 30)
        
        # Generate reason
        reason = f"Lowest score ({scores['total_score']}), "
        reason += f"Crowd: {scores['crowd_score']:.1f}, Distance: {scores['distance_score']:.1f} "
        reason += f"to {zone.title()}"
        
        allocation = BoothAllocationData(
            booth_id=best_booth,
            zone=zone,
            distance_score=scores["distance_score"],
            crowd_score=scores["crowd_score"],
            total_score=scores["total_score"],
            queue_size=scores["queue_size"],
            estimated_wait_minutes=scores["estimated_wait"],
            reason=reason
        )
        
        print(f"✅ Booth allocated: {best_booth} for user at {zone} (score: {best_score})")
        return allocation

    @staticmethod
    def get_top_booths(zone: str, top_n: int = 3) -> List[BoothAllocationData]:
        """
        Get top N best booths for a zone
        
        Args:
            zone: User's delivery zone
            top_n: Number of top booths to return
            
        Returns:
            List of top booths
        """
        booth_scores = []
        
        for booth_id in ["B01", "B02", "B03", "B04", "B05"]:
            booth_status = FoodService.get_booth_status(booth_id)
            if not booth_status:
                continue
            
            # Get scores
            distance_score = BoothAllocationService._get_distance_score(booth_id, zone)
            crowd_score = BoothAllocationService._get_crowd_score(booth_id)
            total_score = BoothAllocationService._calculate_total_score(distance_score, crowd_score)
            
            booth_scores.append((
                booth_id,
                total_score,
                distance_score,
                crowd_score,
                booth_status["current_orders"],
                booth_status["estimated_wait_time"]
            ))
        
        # Sort by total score (ascending)
        booth_scores.sort(key=lambda x: x[1])
        
        # Create allocation data for top N
        results = []
        for booth_id, total_score, dist_score, crowd_score, queue, wait_time in booth_scores[:top_n]:
            reason = f"Top option {len(results) + 1}: "
            if DISTANCE_MATRIX[booth_id].get(zone, 30) <= 10:
                reason += "Very close, "
            reason += f"Crowd: {crowd_score:.1f}"
            
            results.append(BoothAllocationData(
                booth_id=booth_id,
                zone=zone,
                distance_score=dist_score,
                crowd_score=crowd_score,
                total_score=total_score,
                queue_size=queue,
                estimated_wait_minutes=wait_time,
                reason=reason
            ))
        
        return results

    @staticmethod
    def get_distance_to_booth(booth_id: str, zone: str) -> Dict:
        """
        Get distance metrics between booth and zone
        
        Args:
            booth_id: Booth identifier
            zone: User zone
            
        Returns:
            Distance metrics dictionary
        """
        if booth_id not in DISTANCE_MATRIX:
            return None
        
        distance = DISTANCE_MATRIX[booth_id].get(zone, 30)
        distance_score = BoothAllocationService._get_distance_score(booth_id, zone)
        distance_category = BoothAllocationService._get_distance_category(distance)
        
        return {
            "booth_id": booth_id,
            "zone": zone,
            "distance_units": float(distance),
            "distance_score": distance_score,
            "distance_category": distance_category
        }

    @staticmethod
    def reallocate_order(order_id: str, reason: str) -> Optional[BoothAllocationData]:
        """
        Reallocate an order to a better booth
        
        Args:
            order_id: Order ID
            reason: Reason for reallocation
            
        Returns:
            New booths allocation or None if order not found
        """
        from uuid import UUID
        from app.services.food_service import orders_db
        
        try:
            order_uuid = UUID(order_id) if isinstance(order_id, str) else order_id
        except:
            return None
        
        order = orders_db.get(order_uuid)
        if not order:
            return None
        
        # Get new best booth for order's zone
        zone = order.delivery_zone
        new_allocation = BoothAllocationService.allocate_booth(str(order.user_id), zone)
        
        if new_allocation and new_allocation.booth_id != order.booth_id:
            # Update order's booth
            old_booth = order.booth_id
            new_booth = new_allocation.booth_id
            
            from app.services.food_service import BOOTHS
            
            # Remove from old booth
            if old_booth in BOOTHS:
                booth = BOOTHS[old_booth]
                if order_uuid in booth.orders:
                    booth.orders.remove(order_uuid)
                    booth.current_orders = max(0, booth.current_orders - 1)
            
            # Add to new booth
            if new_booth in BOOTHS:
                booth = BOOTHS[new_booth]
                booth.orders.append(order_uuid)
                booth.current_orders += 1
            
            # Update order
            order.booth_id = new_booth
            
            print(f"✅ Order reallocated: {order_id} {old_booth}→{new_booth} ({reason})")
            return new_allocation
        
        return new_allocation
