# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Firebase Cloud Messaging Service
Sends real device push notifications via FCM for gate assignments,
crowd alerts, and emergency broadcasts.
"""

from firebase_admin import messaging
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FCMService:
    """
    Firebase Cloud Messaging integration.
    Sends push notifications to registered device tokens.
    """

    @staticmethod
    def send_gate_notification(
        fcm_token: str,
        gate_id: str,
        queue_depth: int,
        lang: str = "en"
    ) -> bool:
        """
        Send a gate assignment push notification to a device.

        Args:
            fcm_token:   Device FCM registration token
            gate_id:     Assigned gate identifier (e.g., "Gate A")
            queue_depth: Current queue size at the gate
            lang:        Language code for notification text

        Returns:
            True if sent successfully, False otherwise
        """
        titles = {
            "en": "Gate Assignment",
            "hi": "गेट असाइनमेंट",
            "mr": "गेट नियुक्ती"
        }
        bodies = {
            "en": f"Head to {gate_id} — current queue: {queue_depth} people.",
            "hi": f"{gate_id} पर जाएं — वर्तमान कतार: {queue_depth} लोग।",
            "mr": f"{gate_id} कडे जा — सध्याची रांग: {queue_depth} लोक।"
        }

        message = messaging.Message(
            notification=messaging.Notification(
                title=titles.get(lang, titles["en"]),
                body=bodies.get(lang, bodies["en"]),
            ),
            data={
                "gate_id": gate_id,
                "queue_depth": str(queue_depth),
                "action": "navigate_to_gate",
                "type": "gate_assignment"
            },
            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    sound="default",
                    channel_id="gate_alerts"
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1)
                )
            ),
            token=fcm_token,
        )

        try:
            response = messaging.send(message)
            logger.info(f"FCM gate notification sent: {response}")
            return True
        except messaging.UnregisteredError:
            logger.warning(f"FCM token unregistered for gate notification")
            return False
        except Exception as e:
            logger.error(f"FCM send failed: {e}")
            return False

    @staticmethod
    def send_emergency_broadcast(
        fcm_tokens: List[str],
        emergency_type: str,
        safe_exit: str
    ) -> dict:
        """
        Send an emergency alert to multiple devices via FCM multicast.

        Args:
            fcm_tokens:     List of device tokens to notify
            emergency_type: Type of emergency (e.g., "Fire", "Medical")
            safe_exit:      Nearest safe exit identifier

        Returns:
            Dict with success_count and failure_count
        """
        if not fcm_tokens:
            return {"success_count": 0, "failure_count": 0}

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="🚨 EMERGENCY ALERT",
                body=f"{emergency_type} — Proceed to {safe_exit} immediately.",
            ),
            data={
                "emergency_type": emergency_type,
                "safe_exit": safe_exit,
                "action": "emergency_evacuation",
                "priority": "critical"
            },
            android=messaging.AndroidConfig(priority="high"),
            tokens=fcm_tokens[:500],   # FCM multicast limit
        )

        try:
            response = messaging.send_each_for_multicast(message)
            logger.info(
                f"Emergency broadcast: {response.success_count} sent, "
                f"{response.failure_count} failed"
            )
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            logger.error(f"FCM emergency broadcast failed: {e}")
            return {"success_count": 0, "failure_count": len(fcm_tokens)}

    @staticmethod
    def send_crowd_warning(
        fcm_token: str,
        gate_id: str,
        capacity_percent: int,
        alternate_gate: str
    ) -> bool:
        """
        Warn a user their gate is approaching capacity and suggest an alternate.

        Args:
            fcm_token:        Device FCM token
            gate_id:          Congested gate
            capacity_percent: Current capacity percentage
            alternate_gate:   Suggested alternate gate

        Returns:
            True if sent successfully
        """
        message = messaging.Message(
            notification=messaging.Notification(
                title="⚠️ Gate Congestion Alert",
                body=(
                    f"{gate_id} is {capacity_percent}% full. "
                    f"Consider {alternate_gate} for faster entry."
                ),
            ),
            data={
                "gate_id": gate_id,
                "capacity_percent": str(capacity_percent),
                "alternate_gate": alternate_gate,
                "action": "reroute_gate",
                "type": "crowd_warning"
            },
            token=fcm_token,
        )

        try:
            messaging.send(message)
            return True
        except Exception as e:
            logger.error(f"FCM crowd warning failed: {e}")
            return False
