from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""
    sub: str | None = None
    exp: int | None = None
