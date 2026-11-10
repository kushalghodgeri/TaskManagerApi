from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    description="Fetch the authenticated user's profile information.",
    responses={
        200: {"description": "Current user profile", "model": UserRead},
        401: {"description": "Unauthorized: invalid or missing bearer token"},
    },
)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Return the profile of the authenticated user."""
    return UserRead.model_validate(current_user)
