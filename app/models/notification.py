# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from uuid import UUID
from datetime import datetime


class NotificationSendRequest(BaseModel):
    """Request model for sending notifications to one or more users"""
    user_ids: List[UUID] = Field(..., description="List of user IDs to receive notification")
    notification_type: Literal["GATE_ASSIGNMENT", "GATE_REASSIGNMENT", "FOOD_ORDER", "EMERGENCY", "CROWD_WARNING"] = Field(
        ..., description="Type of notification being sent"
    )
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, max_length=1000, description="Notification message content")
    channels: List[Literal["IN_APP", "EMAIL", "SMS"]] = Field(
        ..., min_items=1, description="Delivery channels for notification"
    )
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(
        default="MEDIUM", description="Priority level for notification"
    )
    related_entity_id: Optional[str] = Field(
        default=None, max_length=100, description="ID of related entity (ticket, order, emergency, etc.)"
    )
    related_entity_type: Optional[str] = Field(
        default=None, max_length=50, description="Type of related entity"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "notification_type": "GATE_ASSIGNMENT",
                "title": "Gate Assignment",
                "message": "You have been assigned to Gate A. Entry time approximately 8 minutes.",
                "channels": ["IN_APP", "EMAIL"],
                "priority": "HIGH",
                "related_entity_id": "ticket-123",
                "related_entity_type": "TICKET"
            }
        }


class NotificationResponse(BaseModel):
    """Response model containing full notification details"""
    notification_id: str = Field(..., description="Unique notification ID")
    user_id: UUID = Field(..., description="User who received the notification")
    notification_type: Literal["GATE_ASSIGNMENT", "GATE_REASSIGNMENT", "FOOD_ORDER", "EMERGENCY", "CROWD_WARNING"] = Field(
        ..., description="Type of notification"
    )
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    channels: List[Literal["IN_APP", "EMAIL", "SMS"]] = Field(..., description="Delivery channels")
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(..., description="Priority level")
    status: Literal["QUEUED", "SENT", "DELIVERED", "FAILED", "READ"] = Field(
        default="QUEUED", description="Current delivery status"
    )
    read: bool = Field(default=False, description="Whether user has read the notification")
    related_entity_id: Optional[str] = Field(default=None, description="Related entity ID")
    related_entity_type: Optional[str] = Field(default=None, description="Related entity type")
    created_at: datetime = Field(..., description="When notification was created")
    sent_at: Optional[datetime] = Field(default=None, description="When notification was sent")
    read_at: Optional[datetime] = Field(default=None, description="When user read the notification")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_id": "notif-550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "notification_type": "GATE_ASSIGNMENT",
                "title": "Gate Assignment",
                "message": "You have been assigned to Gate A. Entry time approximately 8 minutes.",
                "channels": ["IN_APP", "EMAIL"],
                "priority": "HIGH",
                "status": "DELIVERED",
                "read": False,
                "related_entity_id": "ticket-123",
                "related_entity_type": "TICKET",
                "created_at": "2024-03-15T10:30:00Z",
                "sent_at": "2024-03-15T10:30:05Z",
                "read_at": None
            }
        }


class NotificationUserResponse(BaseModel):
    """Response model for user's notification list (paginated)"""
    notifications: List[NotificationResponse] = Field(..., description="List of notifications")
    total_count: int = Field(..., description="Total notifications for user")
    unread_count: int = Field(..., description="Count of unread notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "notifications": [
                    {
                        "notification_id": "notif-xxx",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "notification_type": "GATE_ASSIGNMENT",
                        "title": "Gate Assignment",
                        "message": "You have been assigned to Gate A.",
                        "channels": ["IN_APP"],
                        "priority": "HIGH",
                        "status": "DELIVERED",
                        "read": False,
                        "created_at": "2024-03-15T10:30:00Z",
                        "sent_at": "2024-03-15T10:30:05Z",
                        "read_at": None
                    }
                ],
                "total_count": 15,
                "unread_count": 3
            }
        }


class NotificationSendResponse(BaseModel):
    """Response model after sending notification(s)"""
    notification_ids: List[str] = Field(..., description="IDs of created notifications")
    status_message: str = Field(..., description="Summary message of send operation")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_ids": ["notif-550e8400-e29b-41d4-a716-446655440000"],
                "status_message": "Notification sent to 1 user(s)"
            }
        }


class NotificationReadResponse(BaseModel):
    """Response model for marking notification as read"""
    notification_id: str = Field(..., description="Notification ID")
    read: bool = Field(..., description="Read status")
    read_at: datetime = Field(..., description="Timestamp when marked as read")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_id": "notif-xxx",
                "read": True,
                "read_at": "2024-03-15T10:35:00Z"
            }
        }


class ActiveNotificationsResponse(BaseModel):
    """Response model for active (QUEUED/SENT) notifications"""
    active_notifications: List[NotificationResponse] = Field(..., description="List of active notifications")
    total_active: int = Field(..., description="Total active notifications")
    critical_count: int = Field(..., description="Count of CRITICAL priority")
    high_count: int = Field(..., description="Count of HIGH priority")
    medium_count: int = Field(..., description="Count of MEDIUM priority")
    low_count: int = Field(..., description="Count of LOW priority")

    class Config:
        json_schema_extra = {
            "example": {
                "active_notifications": [
                    {
                        "notification_id": "notif-xxx",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "notification_type": "EMERGENCY",
                        "title": "Emergency Alert",
                        "message": "Evacuation order. Proceed to nearest exit.",
                        "channels": ["IN_APP", "SMS"],
                        "priority": "CRITICAL",
                        "status": "SENT",
                        "created_at": "2024-03-15T11:00:00Z",
                        "sent_at": "2024-03-15T11:00:01Z"
                    }
                ],
                "total_active": 47,
                "critical_count": 3,
                "high_count": 15,
                "medium_count": 29,
                "low_count": 0
            }
        }


class ResendResponse(BaseModel):
    """Response model for resending failed notifications"""
    notification_id: str = Field(..., description="Notification ID")
    message: str = Field(..., description="Operation summary")
    channels_retried: List[str] = Field(..., description="Channels retried")

    class Config:
        json_schema_extra = {
            "example": {
                "notification_id": "notif-xxx",
                "message": "Notification resent to 2 channel(s)",
                "channels_retried": ["EMAIL", "SMS"]
            }
        }


class NotificationStatisticsResponse(BaseModel):
    """Response model for notification system statistics"""
    total_notifications_sent: int = Field(..., description="Total notifications sent")
    total_users: int = Field(..., description="Total users who received notifications")
    average_notifications_per_user: float = Field(..., description="Average notifications per user")
    notifications_by_type: Dict[str, int] = Field(..., description="Count by notification type")
    notifications_by_priority: Dict[str, int] = Field(..., description="Count by priority level")
    notifications_by_status: Dict[str, int] = Field(..., description="Count by delivery status")
    active_queued: int = Field(..., description="Currently queued notifications")
    delivery_channels: Dict[str, int] = Field(..., description="Count by delivery channel")
    timestamp: datetime = Field(..., description="Statistics snapshot timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_notifications_sent": 4523,
                "total_users": 1250,
                "average_notifications_per_user": 3.6,
                "notifications_by_type": {
                    "GATE_ASSIGNMENT": 1200,
                    "GATE_REASSIGNMENT": 450,
                    "FOOD_ORDER": 1850,
                    "EMERGENCY": 23,
                    "CROWD_WARNING": 1000
                },
                "notifications_by_priority": {
                    "CRITICAL": 23,
                    "HIGH": 650,
                    "MEDIUM": 2100,
                    "LOW": 1750
                },
                "notifications_by_status": {
                    "DELIVERED": 4400,
                    "SENT": 100,
                    "QUEUED": 15,
                    "FAILED": 8
                },
                "active_queued": 15,
                "delivery_channels": {
                    "IN_APP": 4200,
                    "EMAIL": 250,
                    "SMS": 73
                },
                "timestamp": "2024-03-15T11:30:00Z"
            }
        }


class Notification(BaseModel):
    """Internal model for storing notifications (same structure as response)"""
    notification_id: str
    user_id: UUID
    notification_type: Literal["GATE_ASSIGNMENT", "GATE_REASSIGNMENT", "FOOD_ORDER", "EMERGENCY", "CROWD_WARNING"]
    title: str
    message: str
    channels: List[Literal["IN_APP", "EMAIL", "SMS"]]
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    status: Literal["QUEUED", "SENT", "DELIVERED", "FAILED", "READ"] = "QUEUED"
    read: bool = False
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "notification_id": "notif-550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "notification_type": "GATE_ASSIGNMENT",
                "title": "Gate Assignment",
                "message": "You have been assigned to Gate A. Entry time approximately 8 minutes.",
                "channels": ["IN_APP"],
                "priority": "HIGH",
                "status": "DELIVERED",
                "read": False,
                "related_entity_id": "ticket-123",
                "related_entity_type": "TICKET",
                "created_at": "2024-03-15T10:30:00Z",
                "sent_at": "2024-03-15T10:30:05Z",
                "read_at": None
            }
        }
