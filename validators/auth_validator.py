from pydantic import BaseModel, Field

from app.validators.user_validator import UserResponse


class LoginRequest(BaseModel):
    email: str = Field(examples=["admin@example.com"])
    password: str = Field(examples=["Admin@123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int  # seconds


class MeResponse(BaseModel):
    user: UserResponse
    is_admin: bool
    # resource -> { read, write, create, delete }
    permissions: dict[str, dict[str, bool]]
