"""
Firebase Collection-Specific Service Classes
Extends FirestoreService with domain-specific methods
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID
import logging
from app.services.firebase_service import FirestoreService, get_firestore_service
from app.config.firebase_config import Collections
from app.models.user import User
from app.models.ticket import Ticket
from app.models.food import FoodOrder

logger = logging.getLogger(__name__)


# ============================================================================
# USER SERVICE WITH FIRESTORE
# ============================================================================

class FirestoreUserService:
    """Firestore-backed user management service"""
    
    def __init__(self):
        self.fs = get_firestore_service()
        self.collection = Collections.USERS
    
    async def create_user(self, user: User) -> str:
        """
        Create a new user document
        
        Args:
            user: User object
            
        Returns:
            User document ID
        """
        try:
            user_data = {
                'user_id': str(user.user_id),
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'password_hash': user.password_hash,
                'commute_preference': user.commute_preference,
                'departure_preference': user.departure_preference,
                'created_at': user.created_at,
                'updated_at': datetime.now(),
                'is_active': True
            }
            
            # Use user_id as document ID for quick lookups
            doc_id = await self.fs.create_document(
                self.collection,
                document_id=str(user.user_id),
                data=user_data
            )
            
            logger.info(f"✅ User created in Firestore: {user.email}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to create user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by UUID
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User document or None
        """
        try:
            return await self.fs.get_document(self.collection, str(user_id))
        except Exception as e:
            logger.error(f"❌ Failed to retrieve user: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user by email
        
        Args:
            email: User email
            
        Returns:
            User document or None
        """
        try:
            users = await self.fs.query_documents(
                self.collection,
                field='email',
                operator='==',
                value=email,
                limit=1
            )
            return users[0] if users else None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve user by email: {str(e)}")
            return None
    
    async def update_user(self, user_id: UUID, updates: Dict[str, Any]) -> bool:
        """
        Update user document
        
        Args:
            user_id: UUID of the user
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            return await self.fs.update_document(
                self.collection,
                str(user_id),
                updates,
                merge=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to update user: {str(e)}")
            raise
    
    async def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve all users (with limit for performance)
        
        Args:
            limit: Maximum number of users to retrieve
            
        Returns:
            List of user documents
        """
        try:
            return await self.fs.get_all_documents(self.collection, limit=limit)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve users: {str(e)}")
            return []
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        Deactivate a user account
        
        Args:
            user_id: UUID of the user
            
        Returns:
            True if successful
        """
        try:
            return await self.fs.update_document(
                self.collection,
                str(user_id),
                {'is_active': False},
                merge=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to deactivate user: {str(e)}")
            raise


# ============================================================================
# TICKET SERVICE WITH FIRESTORE
# ============================================================================

class FirestoreTicketService:
    """Firestore-backed ticket management service"""
    
    def __init__(self):
        self.fs = get_firestore_service()
        self.collection = Collections.TICKETS
    
    async def create_ticket(self, ticket: Ticket) -> str:
        """
        Create a new ticket document
        
        Args:
            ticket: Ticket object
            
        Returns:
            Ticket document ID
        """
        try:
            ticket_data = {
                'ticket_id': str(ticket.ticket_id),
                'user_id': str(ticket.user_id),
                'event_id': ticket.event_id,
                'seat_zone': ticket.seat_zone,
                'seat_row': ticket.seat_row,
                'seat_number': ticket.seat_number,
                'price': ticket.price,
                'status': ticket.status,
                'gate_assignment': ticket.gate_assignment,
                'created_at': ticket.created_at,
                'updated_at': datetime.now()
            }
            
            # Use ticket_id as document ID
            doc_id = await self.fs.create_document(
                self.collection,
                document_id=str(ticket.ticket_id),
                data=ticket_data
            )
            
            logger.info(f"✅ Ticket created in Firestore: {ticket.ticket_id}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to create ticket: {str(e)}")
            raise
    
    async def get_ticket_by_id(self, ticket_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve ticket by ID
        
        Args:
            ticket_id: UUID of the ticket
            
        Returns:
            Ticket document or None
        """
        try:
            return await self.fs.get_document(self.collection, str(ticket_id))
        except Exception as e:
            logger.error(f"❌ Failed to retrieve ticket: {str(e)}")
            return None
    
    async def get_tickets_by_user(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Retrieve all tickets for a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of ticket documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='user_id',
                operator='==',
                value=str(user_id)
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve user tickets: {str(e)}")
            return []
    
    async def update_ticket_status(
        self,
        ticket_id: UUID,
        status: str,
        gate_assignment: Optional[str] = None
    ) -> bool:
        """
        Update ticket status and optionally gate assignment
        
        Args:
            ticket_id: UUID of the ticket
            status: New status (CONFIRMED, CANCELLED, USED)
            gate_assignment: Optional gate assignment
            
        Returns:
            True if successful
        """
        try:
            updates = {'status': status}
            if gate_assignment:
                updates['gate_assignment'] = gate_assignment
            
            return await self.fs.update_document(
                self.collection,
                str(ticket_id),
                updates,
                merge=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to update ticket status: {str(e)}")
            raise
    
    async def get_tickets_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all tickets for an event
        
        Args:
            event_id: Event ID
            
        Returns:
            List of ticket documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='event_id',
                operator='==',
                value=event_id
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve event tickets: {str(e)}")
            return []


# ============================================================================
# FOOD ORDER SERVICE WITH FIRESTORE
# ============================================================================

class FirestoreFoodOrderService:
    """Firestore-backed food order management service"""
    
    def __init__(self):
        self.fs = get_firestore_service()
        self.collection = Collections.FOOD_ORDERS
    
    async def create_food_order(self, order: FoodOrder) -> str:
        """
        Create a new food order document
        
        Args:
            order: FoodOrder object
            
        Returns:
            Order document ID
        """
        try:
            order_data = {
                'order_id': str(order.order_id),
                'user_id': str(order.user_id),
                'event_id': order.event_id,
                'items': order.items,
                'booth_id': order.booth_id,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at,
                'updated_at': datetime.now(),
                'estimated_ready_time': order.estimated_ready_time
            }
            
            # Use order_id as document ID
            doc_id = await self.fs.create_document(
                self.collection,
                document_id=str(order.order_id),
                data=order_data
            )
            
            logger.info(f"✅ Food order created in Firestore: {order.order_id}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to create food order: {str(e)}")
            raise
    
    async def get_food_order_by_id(self, order_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve food order by ID
        
        Args:
            order_id: UUID of the order
            
        Returns:
            Food order document or None
        """
        try:
            return await self.fs.get_document(self.collection, str(order_id))
        except Exception as e:
            logger.error(f"❌ Failed to retrieve food order: {str(e)}")
            return None
    
    async def get_orders_by_user(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Retrieve all food orders for a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of order documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='user_id',
                operator='==',
                value=str(user_id)
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve user orders: {str(e)}")
            return []
    
    async def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Retrieve food orders by status
        
        Args:
            status: Order status (PENDING, READY, SERVED, CANCELLED)
            
        Returns:
            List of order documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='status',
                operator='==',
                value=status
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve orders by status: {str(e)}")
            return []
    
    async def update_order_status(
        self,
        order_id: UUID,
        status: str,
        booth_id: Optional[str] = None
    ) -> bool:
        """
        Update food order status
        
        Args:
            order_id: UUID of the order
            status: New status
            booth_id: Optional booth where order is being prepared
            
        Returns:
            True if successful
        """
        try:
            updates = {'status': status}
            if booth_id:
                updates['booth_id'] = booth_id
            
            return await self.fs.update_document(
                self.collection,
                str(order_id),
                updates,
                merge=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to update order status: {str(e)}")
            raise
    
    async def get_pending_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve pending food orders
        
        Args:
            limit: Maximum number of orders
            
        Returns:
            List of pending orders
        """
        try:
            orders = await self.fs.query_documents(
                self.collection,
                field='status',
                operator='==',
                value='PENDING'
            )
            return orders[:limit] if orders else []
        except Exception as e:
            logger.error(f"❌ Failed to retrieve pending orders: {str(e)}")
            return []


# ============================================================================
# EMERGENCY SERVICE WITH FIRESTORE
# ============================================================================

class FirestoreEmergencyService:
    """Firestore-backed emergency management service"""
    
    def __init__(self):
        self.fs = get_firestore_service()
        self.collection = Collections.EMERGENCIES
    
    async def create_emergency(
        self,
        emergency_id: str,
        emergency_type: str,
        location: str,
        severity: str,
        description: str,
        reported_by: str
    ) -> str:
        """
        Create a new emergency report
        
        Args:
            emergency_id: Unique emergency ID
            emergency_type: Type of emergency (FIRE, MEDICAL, SECURITY, CROWD_CRUSH, etc.)
            location: Location in stadium
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            description: Description of emergency
            reported_by: User ID who reported the emergency
            
        Returns:
            Emergency document ID
        """
        try:
            emergency_data = {
                'emergency_id': emergency_id,
                'type': emergency_type,
                'location': location,
                'severity': severity,
                'description': description,
                'reported_by': reported_by,
                'status': 'ACTIVE',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'responded': False,
                'response_time_minutes': None
            }
            
            doc_id = await self.fs.create_document(
                self.collection,
                document_id=emergency_id,
                data=emergency_data
            )
            
            logger.info(f"✅ Emergency created in Firestore: {emergency_id}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to create emergency: {str(e)}")
            raise
    
    async def get_emergency_by_id(self, emergency_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve emergency by ID
        
        Args:
            emergency_id: ID of the emergency
            
        Returns:
            Emergency document or None
        """
        try:
            return await self.fs.get_document(self.collection, emergency_id)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve emergency: {str(e)}")
            return None
    
    async def get_active_emergencies(self) -> List[Dict[str, Any]]:
        """
        Retrieve all active emergencies
        
        Returns:
            List of active emergency documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='status',
                operator='==',
                value='ACTIVE'
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve active emergencies: {str(e)}")
            return []
    
    async def get_emergencies_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Retrieve emergencies by severity
        
        Args:
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            List of emergency documents
        """
        try:
            return await self.fs.query_documents(
                self.collection,
                field='severity',
                operator='==',
                value=severity
            )
        except Exception as e:
            logger.error(f"❌ Failed to retrieve emergencies by severity: {str(e)}")
            return []
    
    async def update_emergency_status(
        self,
        emergency_id: str,
        status: str,
        responded: bool = False,
        response_time_minutes: Optional[int] = None
    ) -> bool:
        """
        Update emergency status
        
        Args:
            emergency_id: ID of the emergency
            status: New status (ACTIVE, RESOLVED, CANCELLED)
            responded: Whether emergency was responded to
            response_time_minutes: Time taken to respond
            
        Returns:
            True if successful
        """
        try:
            updates = {
                'status': status,
                'responded': responded
            }
            if response_time_minutes is not None:
                updates['response_time_minutes'] = response_time_minutes
            
            return await self.fs.update_document(
                self.collection,
                emergency_id,
                updates,
                merge=True
            )
        except Exception as e:
            logger.error(f"❌ Failed to update emergency status: {str(e)}")
            raise
    
    async def add_emergency_update(
        self,
        emergency_id: str,
        update_message: str,
        updated_by: str
    ) -> bool:
        """
        Add an update to an emergency
        
        Args:
            emergency_id: ID of the emergency
            update_message: Update message
            updated_by: User ID who made the update
            
        Returns:
            True if successful
        """
        try:
            update_entry = {
                'message': update_message,
                'updated_by': updated_by,
                'timestamp': datetime.now()
            }
            
            return await self.fs.add_to_array(
                self.collection,
                emergency_id,
                'updates',
                update_entry
            )
        except Exception as e:
            logger.error(f"❌ Failed to add emergency update: {str(e)}")
            raise


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_user_service: Optional[FirestoreUserService] = None
_ticket_service: Optional[FirestoreTicketService] = None
_food_order_service: Optional[FirestoreFoodOrderService] = None
_emergency_service: Optional[FirestoreEmergencyService] = None


def get_firestore_user_service() -> FirestoreUserService:
    """Get or create Firestore user service singleton"""
    global _user_service
    if _user_service is None:
        _user_service = FirestoreUserService()
    return _user_service


def get_firestore_ticket_service() -> FirestoreTicketService:
    """Get or create Firestore ticket service singleton"""
    global _ticket_service
    if _ticket_service is None:
        _ticket_service = FirestoreTicketService()
    return _ticket_service


def get_firestore_food_order_service() -> FirestoreFoodOrderService:
    """Get or create Firestore food order service singleton"""
    global _food_order_service
    if _food_order_service is None:
        _food_order_service = FirestoreFoodOrderService()
    return _food_order_service


def get_firestore_emergency_service() -> FirestoreEmergencyService:
    """Get or create Firestore emergency service singleton"""
    global _emergency_service
    if _emergency_service is None:
        _emergency_service = FirestoreEmergencyService()
    return _emergency_service
