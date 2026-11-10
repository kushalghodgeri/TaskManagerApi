from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Retrieve a user by their primary key ID."""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by their email address."""
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Retrieve a user by their username."""
    stmt = select(User).where(User.username == username)
    return db.scalars(stmt).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user with hashed password."""
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    """Authenticate a user by username or email and password."""
    # Check if input matches email or username
    user = get_user_by_email(db, username_or_email)
    if not user:
        user = get_user_by_username(db, username_or_email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
