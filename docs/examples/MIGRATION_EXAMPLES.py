"""
Migration Examples: Converting Services to Firestore
Shows before/after code for each service
"""

# ============================================================================
# EXAMPLE 1: USER SERVICE MIGRATION
# ============================================================================

# BEFORE (In-Memory:
"""
# app/services/user_service.py (OLD)

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from app.models.user import User

users_db: Dict[UUID, User] = {}

class UserService:
    @staticmethod
    def register_user(request: UserRegisterRequest) -> User:
        user_id = uuid4()
        user = User(
            user_id=user_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            commute_preference=request.commute_preference,
            created_at=datetime.now()
        )
        users_db[user_id] = user
        return user
    
    @staticmethod
    def get_user(user_id: UUID) -> Optional[User]:
        return users_db.get(user_id)
    
    @staticmethod
    def list_all_users() -> List[User]:
        return list(users_db.values())
"""

# AFTER (Firestore):
"""
# app/services/user_service.py (NEW)

import logging
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from app.models.user import User
from app.services.firestore_collections_service import (
    get_firestore_user_service,
    FirestoreUserService
)

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.fs = get_firestore_user_service()
    
    async def register_user(self, request: UserRegisterRequest) -> User:
        '''Register a new user in Firestore'''
        try:
            user_id = uuid4()
            user = User(
                user_id=user_id,
                name=request.name,
                email=request.email,
                phone=request.phone,
                password_hash=hash_password(request.password),
                commute_preference=request.commute_preference,
                created_at=datetime.now()
            )
            
            await self.fs.create_user(user)
            logger.info(f"✅ User registered: {user.email}")
            return user
        
        except Exception as e:
            logger.error(f"❌ Failed to register user: {e}")
            raise
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        '''Get user from Firestore'''
        try:
            user_doc = await self.fs.get_user_by_id(user_id)
            return user_doc
        except Exception as e:
            logger.error(f"❌ Failed to get user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        '''Get user by email from Firestore'''
        try:
            user_doc = await self.fs.get_user_by_email(email)
            return user_doc
        except Exception as e:
            logger.error(f"❌ Failed to get user by email: {e}")
            return None
    
    async def list_all_users(self, limit: int = 100) -> List[User]:
        '''List all users from Firestore (with limit)'''
        try:
            users = await self.fs.get_all_users(limit=limit)
            return users
        except Exception as e:
            logger.error(f"❌ Failed to list users: {e}")
            return []
    
    async def update_user_preference(
        self,
        user_id: UUID,
        preference: str
    ) -> bool:
        '''Update user commute preference'''
        try:
            return await self.fs.update_user(
                user_id,
                {'commute_preference': preference}
            )
        except Exception as e:
            logger.error(f"❌ Failed to update user: {e}")
            raise
"""


# ============================================================================
# EXAMPLE 2: USER ROUTES MIGRATION
# ============================================================================

# BEFORE (Sync):
"""
# app/routes/user_routes.py (OLD)

from fastapi import APIRouter, HTTPException
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register_user(request: UserRegisterRequest):
    try:
        user = UserService.register_user(request)
        return {
            "success": True,
            "user_id": user.user_id,
            "email": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
def get_user(user_id: str):
    try:
        user = UserService.get_user(UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def list_users():
    try:
        users = UserService.list_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

# AFTER (Async with Firestore):
"""
# app/routes/user_routes.py (NEW)

import logging
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.models.user import UserRegisterRequest
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])

# Initialize service
user_service = UserService()

@router.post("/register")
async def register_user(request: UserRegisterRequest):
    '''Register a new user in Firestore'''
    try:
        user = await user_service.register_user(request)
        return {
            "success": True,
            "user_id": str(user.user_id),
            "email": user.email,
            "message": "✅ User registered successfully"
        }
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.get("/{user_id}")
async def get_user(user_id: str):
    '''Retrieve user from Firestore'''
    try:
        user = await user_service.get_user(UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.get("")
async def list_users(limit: int = 100):
    '''List all users from Firestore'''
    try:
        users = await user_service.list_all_users(limit=limit)
        return {
            "count": len(users),
            "users": users
        }
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.put("/{user_id}/preferences")
async def update_user_preference(
    user_id: str,
    preference: dict
):
    '''Update user preferences in Firestore'''
    try:
        await user_service.update_user_preference(
            UUID(user_id),
            preference.get('commute_preference')
        )
        return {
            "success": True,
            "message": "✅ Preference updated"
        }
    except Exception as e:
        logger.error(f"Failed to update preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preference"
        )
"""


# ============================================================================
# EXAMPLE 3: TICKET SERVICE MIGRATION
# ============================================================================

# AFTER (Firestore with async):
"""
# app/services/ticket_service.py (NEW)

import logging
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List
from app.models.ticket import Ticket, TicketBookingRequest
from app.services.firestore_collections_service import (
    get_firestore_ticket_service
)

logger = logging.getLogger(__name__)

class TicketService:
    def __init__(self):
        self.fs = get_firestore_ticket_service()
    
    async def create_ticket(
        self,
        request: TicketBookingRequest
    ) -> Ticket:
        '''Create ticket in Firestore'''
        try:
            ticket = Ticket(
                ticket_id=uuid4(),
                user_id=request.user_id,
                event_id=request.event_id,
                seat_zone=request.seat_zone,
                seat_row=request.seat_row,
                seat_number=request.seat_number,
                price=request.price,
                status="CONFIRMED",
                created_at=datetime.now()
            )
            
            await self.fs.create_ticket(ticket)
            logger.info(f"✅ Ticket created: {ticket.ticket_id}")
            return ticket
        
        except Exception as e:
            logger.error(f"❌ Failed to create ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_id: UUID) -> Optional[Ticket]:
        '''Get ticket from Firestore'''
        try:
            ticket_doc = await self.fs.get_ticket_by_id(ticket_id)
            return ticket_doc
        except Exception as e:
            logger.error(f"❌ Failed to get ticket: {e}")
            return None
    
    async def get_user_tickets(self, user_id: UUID) -> List[Ticket]:
        '''Get all tickets for user from Firestore'''
        try:
            tickets = await self.fs.get_tickets_by_user(user_id)
            return tickets
        except Exception as e:
            logger.error(f"❌ Failed to get user tickets: {e}")
            return []
    
    async def update_ticket_status(
        self,
        ticket_id: UUID,
        status: str,
        gate_assignment: Optional[str] = None
    ) -> bool:
        '''Update ticket status in Firestore'''
        try:
            return await self.fs.update_ticket_status(
                ticket_id,
                status,
                gate_assignment
            )
        except Exception as e:
            logger.error(f"❌ Failed to update ticket: {e}")
            raise
    
    async def get_event_tickets(self, event_id: str) -> List[Ticket]:
        '''Get all tickets for event from Firestore'''
        try:
            tickets = await self.fs.get_tickets_by_event(event_id)
            return tickets
        except Exception as e:
            logger.error(f"❌ Failed to get event tickets: {e}")
            return []
"""


# ============================================================================
# EXAMPLE 4: FOOD ORDER SERVICE MIGRATION
# ============================================================================

# AFTER (Firestore with async):
"""
# app/services/food_service.py (NEW)

import logging
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List, Dict
from app.models.food_orders import FoodOrder, FoodOrderRequest
from app.services.firestore_collections_service import (
    get_firestore_food_order_service
)

logger = logging.getLogger(__name__)

class FoodService:
    def __init__(self):
        self.fs = get_firestore_food_order_service()
    
    async def create_order(
        self,
        request: FoodOrderRequest
    ) -> FoodOrder:
        '''Create food order in Firestore'''
        try:
            order = FoodOrder(
                order_id=uuid4(),
                user_id=request.user_id,
                event_id=request.event_id,
                items=request.items,
                booth_id=None,  # Will be assigned
                total_amount=self._calculate_total(request.items),
                status="PENDING",
                created_at=datetime.now()
            )
            
            await self.fs.create_food_order(order)
            logger.info(f"✅ Food order created: {order.order_id}")
            return order
        
        except Exception as e:
            logger.error(f"❌ Failed to create order: {e}")
            raise
    
    async def get_order(self, order_id: UUID) -> Optional[FoodOrder]:
        '''Get food order from Firestore'''
        try:
            order_doc = await self.fs.get_food_order_by_id(order_id)
            return order_doc
        except Exception as e:
            logger.error(f"❌ Failed to get order: {e}")
            return None
    
    async def get_pending_orders(self, limit: int = 50) -> List[FoodOrder]:
        '''Get pending orders for kitchen from Firestore'''
        try:
            orders = await self.fs.get_pending_orders(limit=limit)
            return orders
        except Exception as e:
            logger.error(f"❌ Failed to get pending orders: {e}")
            return []
    
    async def update_order_status(
        self,
        order_id: UUID,
        status: str,
        booth_id: Optional[str] = None
    ) -> bool:
        '''Update order status in Firestore'''
        try:
            return await self.fs.update_order_status(
                order_id,
                status,
                booth_id
            )
        except Exception as e:
            logger.error(f"❌ Failed to update order status: {e}")
            raise
    
    @staticmethod
    def _calculate_total(items: Dict[str, int]) -> float:
        '''Calculate total price for items'''
        prices = {
            'pizza': 300,
            'coke': 100,
            'burger': 250,
            'fries': 150
        }
        total = sum(prices.get(item, 0) * qty for item, qty in items.items())
        return total
"""


# ============================================================================
# EXAMPLE 5: EMERGENCY SERVICE MIGRATION
# ============================================================================

# AFTER (Firestore with async):
"""
# app/services/emergency_service.py (NEW)

import logging
from datetime import datetime
from typing import List, Optional
from app.services.firestore_collections_service import (
    get_firestore_emergency_service
)

logger = logging.getLogger(__name__)

class EmergencyService:
    def __init__(self):
        self.fs = get_firestore_emergency_service()
    
    async def report_emergency(
        self,
        emergency_type: str,
        location: str,
        severity: str,
        description: str,
        reported_by: str
    ) -> str:
        '''Report emergency in Firestore'''
        try:
            # Generate unique ID with timestamp
            emergency_id = f"EM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            doc_id = await self.fs.create_emergency(
                emergency_id=emergency_id,
                emergency_type=emergency_type,
                location=location,
                severity=severity,
                description=description,
                reported_by=reported_by
            )
            
            logger.warning(f"🚨 Emergency reported: {emergency_id} - {severity}")
            return doc_id
        
        except Exception as e:
            logger.error(f"❌ Failed to report emergency: {e}")
            raise
    
    async def get_active_emergencies(self) -> List[dict]:
        '''Get all active emergencies from Firestore'''
        try:
            emergencies = await self.fs.get_active_emergencies()
            return emergencies
        except Exception as e:
            logger.error(f"❌ Failed to get active emergencies: {e}")
            return []
    
    async def get_critical_emergencies(self) -> List[dict]:
        '''Get critical severity emergencies from Firestore'''
        try:
            emergencies = await self.fs.get_emergencies_by_severity("CRITICAL")
            return emergencies
        except Exception as e:
            logger.error(f"❌ Failed to get critical emergencies: {e}")
            return []
    
    async def resolve_emergency(
        self,
        emergency_id: str,
        response_time_minutes: Optional[int] = None
    ) -> bool:
        '''Resolve emergency in Firestore'''
        try:
            return await self.fs.update_emergency_status(
                emergency_id,
                status="RESOLVED",
                responded=True,
                response_time_minutes=response_time_minutes
            )
        except Exception as e:
            logger.error(f"❌ Failed to resolve emergency: {e}")
            raise
    
    async def add_emergency_update(
        self,
        emergency_id: str,
        update_message: str,
        updated_by: str
    ) -> bool:
        '''Add update to emergency in Firestore'''
        try:
            return await self.fs.add_emergency_update(
                emergency_id,
                update_message,
                updated_by
            )
        except Exception as e:
            logger.error(f"❌ Failed to add emergency update: {e}")
            raise
"""

print("✅ Migration examples loaded successfully")
