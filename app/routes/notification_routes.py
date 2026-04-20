"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from typing import Optional, List
from app.models.notification import (
    NotificationSendRequest,
    NotificationResponse,
    NotificationUserResponse,
    NotificationSendResponse,
    NotificationReadResponse,
    ActiveNotificationsResponse,
    ResendResponse
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "",
    response_model=NotificationSendResponse,
    status_code=201,
    summary="Send notification to user(s)",
    description="Send a notification to one or more users across multiple channels"
)
async def send_notification(request: NotificationSendRequest) -> NotificationSendResponse:
    """
    Send notification to specified users
    
    - **user_ids**: List of UUID strings for recipients
    - **notification_type**: Type of notification (GATE_ASSIGNMENT, GATE_REASSIGNMENT, FOOD_ORDER, EMERGENCY, CROWD_WARNING)
    - **title**: Notification title (max 200 chars)
    - **message**: Notification message (max 1000 chars)
    - **channels**: Delivery channels (IN_APP, EMAIL, SMS)
    - **priority**: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
    - **related_entity_id**: Reference to related object (optional)
    - **related_entity_type**: Type of related object (optional)
    """
    try:
        notification_ids, status_message = NotificationService.send_notification(
            user_ids=request.user_ids,
            notification_type=request.notification_type,
            title=request.title,
            message=request.message,
            channels=request.channels,
            priority=request.priority,
            related_entity_id=request.related_entity_id,
            related_entity_type=request.related_entity_type
        )
        
        return NotificationSendResponse(
            notification_ids=notification_ids,
            status_message=status_message
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/user/{user_id}",
    response_model=NotificationUserResponse,
    summary="Get user's notifications (paginated)",
    description="Retrieve paginated notification history for a specific user"
)
async def get_user_notifications(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=1000, description="Number of notifications to return"),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    read_status: Optional[str] = Query(None, description="Filter by read status: 'read', 'unread', or 'all'")
) -> NotificationUserResponse:
    """
    Get notifications for a specific user
    
    - **user_id**: User UUID
    - **limit**: Maximum number of notifications to return (default: 50)
    - **skip**: Number of notifications to skip for pagination (default: 0)
    - **read_status**: Filter by read status ('read', 'unread', or 'all')
    """
    if read_status and read_status not in ["read", "unread", "all"]:
        raise HTTPException(status_code=400, detail="read_status must be 'read', 'unread', or 'all'")
    
    notifications, total_count, unread_count = NotificationService.get_user_notifications(
        user_id=user_id,
        limit=limit,
        skip=skip,
        read_status=read_status
    )
    
    notification_responses = [NotificationResponse(**n.dict()) for n in notifications]
    
    return NotificationUserResponse(
        notifications=notification_responses,
        total_count=total_count,
        unread_count=unread_count
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification details",
    description="Retrieve full details of a specific notification"
)
async def get_notification(notification_id: str) -> NotificationResponse:
    """
    Get a specific notification by ID
    
    - **notification_id**: Notification ID to retrieve
    """
    notification = NotificationService.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse(**notification.dict())


@router.put(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
    summary="Mark notification as read",
    description="Mark a notification as read and record the timestamp"
)
async def mark_as_read(notification_id: str) -> NotificationReadResponse:
    """
    Mark a notification as read
    
    - **notification_id**: Notification ID to mark as read
    """
    notification = NotificationService.mark_as_read(notification_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationReadResponse(
        notification_id=notification.notification_id,
        read=notification.read,
        read_at=notification.read_at
    )


@router.get(
    "/active",
    response_model=ActiveNotificationsResponse,
    summary="List active notifications",
    description="Get all QUEUED/SENT notifications currently in system"
)
async def get_active_notifications(
    priority: Optional[str] = Query(None, description="Filter by priority: CRITICAL, HIGH, MEDIUM, LOW"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type")
) -> ActiveNotificationsResponse:
    """
    Get all active (QUEUED/SENT) notifications
    
    - **priority**: Optional filter by priority level
    - **notification_type**: Optional filter by notification type
    """
    valid_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    if priority and priority not in valid_priorities:
        raise HTTPException(status_code=400, detail=f"priority must be one of {valid_priorities}")
    
    active_notifs, priority_counts = NotificationService.get_active_notifications(
        priority_filter=priority,
        notification_type=notification_type
    )
    
    notification_responses = [NotificationResponse(**n.dict()) for n in active_notifs]
    
    return ActiveNotificationsResponse(
        active_notifications=notification_responses,
        total_active=len(active_notifs),
        critical_count=priority_counts["CRITICAL"],
        high_count=priority_counts["HIGH"],
        medium_count=priority_counts["MEDIUM"],
        low_count=priority_counts["LOW"]
    )


@router.get(
    "/priority/{priority}",
    response_model=dict,
    summary="Filter notifications by priority",
    description="Get notifications filtered by priority level"
)
async def get_by_priority(
    priority: str,
    notification_type: Optional[str] = Query(None, description="Optional filter by type"),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> dict:
    """
    Get notifications filtered by priority level
    
    - **priority**: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
    - **notification_type**: Optional filter by notification type
    - **limit**: Max results (default: 50)
    - **skip**: Pagination offset (default: 0)
    """
    valid_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    if priority not in valid_priorities:
        raise HTTPException(status_code=400, detail=f"priority must be one of {valid_priorities}")
    
    notifications, total_count = NotificationService.get_notifications_by_priority(
        priority=priority,
        notification_type=notification_type,
        limit=limit,
        skip=skip
    )
    
    notification_responses = [NotificationResponse(**n.dict()) for n in notifications]
    
    return {
        "priority": priority,
        "notifications": notification_responses,
        "total_count": total_count
    }


@router.delete(
    "/user/{user_id}",
    summary="Clear user notifications",
    description="Delete notifications for a specific user, optionally filtered by age"
)
async def clear_user_notifications(
    user_id: UUID,
    older_than_hours: Optional[int] = Query(None, description="Only delete notifications older than X hours")
) -> dict:
    """
    Delete notifications for a user
    
    - **user_id**: User UUID
    - **older_than_hours**: Optional age filter (only delete older than specified hours)
    """
    deleted_count = NotificationService.delete_user_notifications(
        user_id=user_id,
        older_than_hours=older_than_hours
    )
    
    return {
        "message": f"Deleted {deleted_count} notifications",
        "deleted_count": deleted_count
    }


@router.post(
    "/{notification_id}/resend",
    response_model=ResendResponse,
    summary="Resend failed notification",
    description="Resend a notification to specified channels"
)
async def resend_notification(
    notification_id: str,
    channels: List[str] = Query(..., description="Channels to retry: IN_APP, EMAIL, SMS")
) -> ResendResponse:
    """
    Resend notification to specified channels
    
    - **notification_id**: Notification ID to resend
    - **channels**: Channels to retry (must be at least one of: IN_APP, EMAIL, SMS)
    """
    valid_channels = ["IN_APP", "EMAIL", "SMS"]
    if not channels or not all(c in valid_channels for c in channels):
        raise HTTPException(status_code=400, detail=f"channels must contain valid channel names: {valid_channels}")
    
    notification = NotificationService.resend_notification(
        notification_id=notification_id,
        channels=channels
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return ResendResponse(
        notification_id=notification.notification_id,
        message=f"Notification resent to {len(channels)} channel(s)",
        channels_retried=channels
    )


@router.get(
    "/statistics/summary",
    summary="Get notification statistics",
    description="Get system-wide notification statistics and metrics"
)
async def get_statistics() -> dict:
    """
    Get notification system statistics
    
    Returns aggregated statistics including:
    - Total notifications sent
    - Average notifications per user
    - Breakdown by type, priority, status
    - Delivery channel usage
    - Active queued notifications
    """
    stats = NotificationService.get_notification_statistics()
    return stats.dict()
