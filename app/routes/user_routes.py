"""
Author: Mangesh Wagh
Email: mangeshwagh2722@gmail.com
"""

"""
User Routes - API endpoints for user management
"""
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import List

from app.models.user import (
    UserResponse,
    UserRegisterRequest,
    PreferenceUpdateRequest,
    PreferenceUpdateResponse,
    UserListResponse
)
from app.services.user_service import UserService

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest) -> UserResponse:
    """
    Register a new user
    
    - **name**: User's full name
    - **email**: Valid email address
    - **phone**: Phone number
    - **commute_preference**: metro, bus, private, or cab
    
    Returns: Registered user with UUID
    """
    user = UserService.register_user(request)
    return UserResponse(**user.dict())


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID) -> UserResponse:
    """
    Get user details by ID
    
    - **user_id**: UUID of the user
    
    Returns: User details or 404 if not found
    """
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return UserResponse(**user.dict())


@router.get("", response_model=UserListResponse)
async def list_users() -> UserListResponse:
    """
    Get all registered users
    
    Returns: List of all users
    """
    users = UserService.list_all_users()
    return UserListResponse(
        total=len(users),
        users=[UserResponse(**user.dict()) for user in users]
    )


@router.put("/{user_id}/preferences", response_model=PreferenceUpdateResponse)
async def update_preferences(
    user_id: UUID,
    request: PreferenceUpdateRequest
) -> PreferenceUpdateResponse:
    """
    Update user's commute preference
    
    - **user_id**: UUID of the user
    - **commute_preference**: metro, bus, private, or cab
    
    Returns: Updated preference or 404 if user not found
    """
    user = UserService.update_preference(user_id, request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return PreferenceUpdateResponse(
        message="Preferences updated successfully",
        user_id=user_id,
        commute_preference=user.commute_preference
    )


@router.get("/preference/{preference}", response_model=List[UserResponse])
async def get_users_by_preference(preference: str) -> List[UserResponse]:
    """
    Get all users with a specific commute preference
    
    - **preference**: metro, bus, private, or cab
    
    Returns: List of users with matching preference
    """
    users = UserService.get_users_by_commute_preference(preference)
    return [UserResponse(**user.dict()) for user in users]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):
    """
    Delete a user
    
    - **user_id**: UUID of the user
    
    Returns: 204 No Content or 404 if not found
    """
    deleted = UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return None
