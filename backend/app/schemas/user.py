from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema containing shared attributes."""
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["alice@example.com"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]{3,30}$",
        description="Username (3-30 alphanumeric characters or underscores)",
        examples=["alice_dev"],
    )


class UserCreate(UserBase):
    """Schema for user registration request."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Account password (minimum 8 characters)",
        examples=["SuperSecret123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "username": "alice_dev",
                "password": "SuperSecret123!",
            }
        }
    )


class UserRead(UserBase):
    """Schema for public user profile responses."""
    id: int = Field(..., description="Unique user identifier", examples=[1])
    is_active: bool = Field(..., description="Whether the user account is active", examples=[True])
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "alice@example.com",
                "username": "alice_dev",
                "is_active": True,
                "created_at": "2026-01-01T12:00:00Z",
            }
        },
    )
