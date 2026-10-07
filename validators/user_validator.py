import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.validators.role_validator import RoleBrief

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


# Input schema (used for registration and full user updates)
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, examples=["john_doe"])
    email: EmailStr = Field(examples=["john@example.com"])
    password: str = Field(min_length=8, max_length=64, examples=["Str0ngPassw0rd"])

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not USERNAME_PATTERN.match(value):
            raise ValueError(
                "Username may only contain letters, numbers and underscores"
            )
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")
        return value


# Output schema (never expose hashed_password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    roles: list[RoleBrief] = []

    class Config:
        from_attributes = True


# Wrapped response with a message
class UserCreateResponse(BaseModel):
    message: str
    user: UserResponse


# Paginated list response
class UserListResponse(BaseModel):
    message: str
    page: int
    limit: int
    users: list[UserResponse]
    total: int
