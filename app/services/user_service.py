"""
User Service - Business logic for user management
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List
from app.models.user import User, UserRegisterRequest, PreferenceUpdateRequest

# ============================================================================
# IN-MEMORY USER DATABASE
# ============================================================================

users_db: Dict[UUID, User] = {}


# ============================================================================
# USER SERVICE CLASS
# ============================================================================

class UserService:
    """
    Service class for managing users
    """

    @staticmethod
    def register_user(request: UserRegisterRequest) -> User:
        """
        Register a new user
        
        Args:
            request: UserRegisterRequest with user details
            
        Returns:
            Created User object
        """
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
        
        print(f"✅ User registered: {user.name} ({user_id})")
        return user

    @staticmethod
    def get_user(user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User object or None if not found
        """
        return users_db.get(user_id)

    @staticmethod
    def list_all_users() -> List[User]:
        """
        Get all registered users
        
        Returns:
            List of User objects
        """
        return list(users_db.values())

    @staticmethod
    def update_preference(user_id: UUID, request: PreferenceUpdateRequest) -> Optional[User]:
        """
        Update user's commute preference
        
        Args:
            user_id: UUID of the user
            request: PreferenceUpdateRequest with new preference
            
        Returns:
            Updated User object or None if not found
        """
        if user_id not in users_db:
            return None
        
        user = users_db[user_id]
        user.commute_preference = request.commute_preference
        
        print(f"✅ User preference updated: {user.name} → {request.commute_preference}")
        return user

    @staticmethod
    def delete_user(user_id: UUID) -> bool:
        """
        Delete a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            True if deleted, False if not found
        """
        if user_id in users_db:
            deleted_user = users_db.pop(user_id)
            print(f"✅ User deleted: {deleted_user.name} ({user_id})")
            return True
        return False

    @staticmethod
    def get_users_by_commute_preference(preference: str) -> List[User]:
        """
        Get all users with a specific commute preference
        
        Args:
            preference: Commute preference (metro, bus, private, cab)
            
        Returns:
            List of matching User objects
        """
        return [
            user for user in users_db.values()
            if user.commute_preference == preference
        ]

    @staticmethod
    def get_user_count() -> int:
        """
        Get total number of registered users
        
        Returns:
            Count of users
        """
        return len(users_db)

    @staticmethod
    def clear_all():
        """
        Clear all users (for testing)
        """
        users_db.clear()
        print("✅ All users cleared from database")
