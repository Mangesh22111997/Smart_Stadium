"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

from typing import List, Dict, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from app.models.notification import Notification, NotificationStatisticsResponse
import random


# In-memory storage for notifications
notifications_db: Dict[str, Notification] = {}

# Track notifications per user for fast lookup
user_notifications: Dict[UUID, List[str]] = {}

# Message templates for different notification types
MESSAGE_TEMPLATES = {
    "GATE_ASSIGNMENT": "You have been assigned to Gate {gate_id}. Entry time approximately {entry_minutes} minutes.",
    "GATE_REASSIGNMENT": "Your gate has been reassigned from {old_gate} to {new_gate} due to congestion. Please navigate to new gate.",
    "FOOD_ORDER": "Your order is ready for pickup at Booth {booth_id}. Prep time: {prep_time} minutes.",
    "EMERGENCY": "Emergency Alert: {emergency_type}. Please proceed to nearest exit: {exit_id}. Distance: {distance}m.",
    "CROWD_WARNING": "Gate {gate_id} is very crowded ({capacity_percent}% full). Please use alternate gates if available."
}

# Priority weights for sorting
PRIORITY_WEIGHTS = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4
}

# Delivery channel list
DELIVERY_CHANNELS = ["IN_APP", "EMAIL", "SMS"]


class NotificationService:
    """Service for managing notifications across all users and channels"""

    @staticmethod
    def send_notification(
        user_ids: List[UUID],
        notification_type: str,
        title: str,
        message: str,
        channels: List[str],
        priority: str,
        related_entity_id: Optional[str] = None,
        related_entity_type: Optional[str] = None
    ) -> Tuple[List[str], str]:
        """
        Send notification to one or more users
        Returns: (notification_ids, status_message)
        """
        notification_ids = []
        
        for user_id in user_ids:
            notification_id = NotificationService.generate_notification_id()
            now = datetime.utcnow()
            
            # Create notification object
            notification = Notification(
                notification_id=notification_id,
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                channels=channels,
                priority=priority,
                status="QUEUED",
                read=False,
                related_entity_id=related_entity_id,
                related_entity_type=related_entity_type,
                created_at=now,
                sent_at=None,
                read_at=None
            )
            
            # Store in database
            notifications_db[notification_id] = notification
            
            # Track for user
            if user_id not in user_notifications:
                user_notifications[user_id] = []
            user_notifications[user_id].append(notification_id)
            
            # Simulate sending on channels (in real impl, would call actual services)
            NotificationService._simulate_channel_send(notification_id, channels)
            
            notification_ids.append(notification_id)
        
        status_message = f"Notification sent to {len(user_ids)} user(s)"
        return notification_ids, status_message

    @staticmethod
    def get_user_notifications(
        user_id: UUID, 
        limit: int = 50, 
        skip: int = 0, 
        read_status: Optional[str] = None
    ) -> Tuple[List[Notification], int, int]:
        """
        Get paginated notifications for a user
        Returns: (notifications_list, total_count, unread_count)
        """
        if user_id not in user_notifications:
            return [], 0, 0
        
        # Get all notification IDs for user
        user_notif_ids = user_notifications[user_id]
        
        # Get notification objects
        user_notifs = [notifications_db[nid] for nid in user_notif_ids if nid in notifications_db]
        
        # Filter by read status if specified
        if read_status == "read":
            user_notifs = [n for n in user_notifs if n.read]
        elif read_status == "unread":
            user_notifs = [n for n in user_notifs if not n.read]
        
        # Sort by created_at descending (newest first)
        user_notifs.sort(key=lambda x: x.created_at, reverse=True)
        
        total_count = len(user_notifs)
        unread_count = sum(1 for n in user_notifs if not n.read)
        
        # Apply pagination
        paginated = user_notifs[skip:skip + limit]
        
        return paginated, total_count, unread_count

    @staticmethod
    def get_notification(notification_id: str) -> Optional[Notification]:
        """Get a specific notification by ID"""
        return notifications_db.get(notification_id)

    @staticmethod
    def get_active_notifications(
        priority_filter: Optional[str] = None,
        notification_type: Optional[str] = None
    ) -> Tuple[List[Notification], Dict[str, int]]:
        """
        Get all QUEUED/SENT notifications (active in system)
        Returns: (notifications_list, priority_counts)
        """
        active = [
            n for n in notifications_db.values() 
            if n.status in ["QUEUED", "SENT"]
        ]
        
        # Apply filters
        if notification_type:
            active = [n for n in active if n.notification_type == notification_type]
        
        if priority_filter:
            active = [n for n in active if n.priority == priority_filter]
        
        # Sort by priority, then by created_at (most recent first)
        active.sort(
            key=lambda x: (PRIORITY_WEIGHTS.get(x.priority, 999), -x.created_at.timestamp())
        )
        
        # Count by priority
        priority_counts = {
            "CRITICAL": sum(1 for n in active if n.priority == "CRITICAL"),
            "HIGH": sum(1 for n in active if n.priority == "HIGH"),
            "MEDIUM": sum(1 for n in active if n.priority == "MEDIUM"),
            "LOW": sum(1 for n in active if n.priority == "LOW")
        }
        
        return active, priority_counts

    @staticmethod
    def get_notifications_by_priority(
        priority: str,
        notification_type: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> Tuple[List[Notification], int]:
        """
        Get notifications filtered by priority level
        Returns: (notifications_list, total_count)
        """
        filtered = [
            n for n in notifications_db.values() 
            if n.priority == priority
        ]
        
        if notification_type:
            filtered = [n for n in filtered if n.notification_type == notification_type]
        
        # Sort by created_at descending
        filtered.sort(key=lambda x: x.created_at, reverse=True)
        
        total_count = len(filtered)
        paginated = filtered[skip:skip + limit]
        
        return paginated, total_count

    @staticmethod
    def mark_as_read(notification_id: str) -> Optional[Notification]:
        """Mark notification as read"""
        if notification_id not in notifications_db:
            return None
        
        notification = notifications_db[notification_id]
        notification.read = True
        notification.read_at = datetime.utcnow()
        notification.status = "READ"
        
        return notification

    @staticmethod
    def update_status(notification_id: str, new_status: str) -> Optional[Notification]:
        """Update notification delivery status"""
        if notification_id not in notifications_db:
            return None
        
        notification = notifications_db[notification_id]
        notification.status = new_status
        
        if new_status == "SENT" and notification.sent_at is None:
            notification.sent_at = datetime.utcnow()
        
        return notification

    @staticmethod
    def resend_notification(notification_id: str, channels: List[str]) -> Optional[Notification]:
        """Resend a notification to specified channels"""
        if notification_id not in notifications_db:
            return None
        
        notification = notifications_db[notification_id]
        
        # Update channels list
        notification.channels = channels
        
        # Simulate resending
        NotificationService._simulate_channel_send(notification_id, channels)
        
        # Update status
        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()
        
        return notification

    @staticmethod
    def delete_user_notifications(user_id: UUID, older_than_hours: Optional[int] = None) -> int:
        """
        Delete user's notifications, optionally filtered by age
        Returns: count of deleted notifications
        """
        if user_id not in user_notifications:
            return 0
        
        user_notif_ids = user_notifications[user_id].copy()
        deleted_count = 0
        cutoff_time = None
        
        if older_than_hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        for notif_id in user_notif_ids:
            if notif_id in notifications_db:
                notification = notifications_db[notif_id]
                
                # Check age if cutoff specified
                if cutoff_time and notification.created_at > cutoff_time:
                    continue
                
                # Delete notification
                del notifications_db[notif_id]
                user_notifications[user_id].remove(notif_id)
                deleted_count += 1
        
        # Clean up empty user entry
        if not user_notifications[user_id]:
            del user_notifications[user_id]
        
        return deleted_count

    @staticmethod
    def get_notification_statistics() -> NotificationStatisticsResponse:
        """Get system-wide notification statistics"""
        total_sent = len(notifications_db)
        total_users = len(user_notifications)
        avg_per_user = total_sent / total_users if total_users > 0 else 0.0
        
        # Count by type
        by_type = {}
        for notif in notifications_db.values():
            by_type[notif.notification_type] = by_type.get(notif.notification_type, 0) + 1
        
        # Count by priority
        by_priority = {
            "CRITICAL": sum(1 for n in notifications_db.values() if n.priority == "CRITICAL"),
            "HIGH": sum(1 for n in notifications_db.values() if n.priority == "HIGH"),
            "MEDIUM": sum(1 for n in notifications_db.values() if n.priority == "MEDIUM"),
            "LOW": sum(1 for n in notifications_db.values() if n.priority == "LOW")
        }
        
        # Count by status
        by_status = {}
        for notif in notifications_db.values():
            by_status[notif.status] = by_status.get(notif.status, 0) + 1
        
        # Count active (queued)
        active_queued = sum(1 for n in notifications_db.values() if n.status == "QUEUED")
        
        # Count by channel (each notification can use multiple channels)
        by_channel = {"IN_APP": 0, "EMAIL": 0, "SMS": 0}
        for notif in notifications_db.values():
            for channel in notif.channels:
                by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return NotificationStatisticsResponse(
            total_notifications_sent=total_sent,
            total_users=total_users,
            average_notifications_per_user=round(avg_per_user, 2),
            notifications_by_type=by_type,
            notifications_by_priority=by_priority,
            notifications_by_status=by_status,
            active_queued=active_queued,
            delivery_channels=by_channel,
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def generate_notification_id() -> str:
        """Generate unique notification ID"""
        return f"notif-{int(datetime.utcnow().timestamp() * 1000)}-{random.randint(1000, 9999)}"

    @staticmethod
    def _simulate_channel_send(notification_id: str, channels: List[str]) -> None:
        """
        Simulate sending notification to various channels
        In production, would integrate with SendGrid (email), Twilio (SMS), etc.
        """
        if notification_id not in notifications_db:
            return
        
        notification = notifications_db[notification_id]
        
        # Simulate successful send to all channels (in reality would be async)
        for channel in channels:
            if channel == "IN_APP":
                # Already stored in database
                pass
            elif channel == "EMAIL":
                # Simulate email sending
                success = random.random() > 0.05  # 95% success rate
                if success:
                    pass  # In real impl: call SendGrid API
            elif channel == "SMS":
                # Simulate SMS sending
                success = random.random() > 0.10  # 90% success rate
                if success:
                    pass  # In real impl: call Twilio API
        
        # Mark as sent after simulation
        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()

    @staticmethod
    def clear_all() -> None:
        """Clear all notifications (for testing)"""
        notifications_db.clear()
        user_notifications.clear()
