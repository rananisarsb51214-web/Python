"""User management routes."""

from fastapi import APIRouter, status, HTTPException, Depends
from app.models.schemas import UserResponse
from app.services.user_service import UserService
from app.middlewares.auth import verify_jwt
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User",
    description="Retrieve user profile information",
)
async def get_user(
    user_id: str,
    token_payload: dict = Depends(verify_jwt),
) -> UserResponse:
    """
    Get user profile.
    
    Args:
        user_id: User ID to retrieve
        token_payload: Verified JWT token payload
        
    Returns:
        UserResponse with user data
        
    Raises:
        HTTPException: If user not found
    """
    try:
        # Verify user can only access their own profile
        if token_payload.get("sub") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        service = UserService()
        user = await service.get_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete user account and all associated data",
)
async def delete_user(
    user_id: str,
    token_payload: dict = Depends(verify_jwt),
):
    """
    Delete user account.
    
    Args:
        user_id: User ID to delete
        token_payload: Verified JWT token payload
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Verify user can only delete their own account
        if token_payload.get("sub") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        
        service = UserService()
        success = await service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )
        
        logger.info(f"User deleted: {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )
