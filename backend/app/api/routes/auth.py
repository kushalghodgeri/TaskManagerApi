from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token
from app.crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with a unique email, unique username, and secure password.",
    responses={
        201: {"description": "User successfully created", "model": UserRead},
        409: {"description": "Conflict: email or username already registered"},
        422: {"description": "Validation error for invalid email, username, or password"},
    },
)
def register(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    """Create a new user profile."""
    # Check if email is already taken
    if get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check if username is already taken
    if get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = create_user(db=db, user_in=user_in)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and get access token",
    description="Login using OAuth2 password flow. The `username` field accepts the user's email address.",
    responses={
        200: {"description": "JWT access token successfully issued", "model": Token},
        401: {"description": "Unauthorized: incorrect email or password"},
    },
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate user credentials and issue a bearer JWT token."""
    user = authenticate_user(
        db,
        username_or_email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token, token_type="bearer")
